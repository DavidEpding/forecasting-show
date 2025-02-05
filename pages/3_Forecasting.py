#!/usr/bin/env python
# coding: utf-8
#### Import Libraries and settings ####

import streamlit as st
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import plotly.express as px
import matplotlib.pyplot as plt
import xgboost as xgb
from prophet import Prophet

###### Header ########
app_title = "ForeCasting-Show v0.9"
st.set_page_config(layout="wide",page_title=app_title,page_icon=":gorilla:")
st.markdown(
    """
    <style>
        /* Stil für die Sidebar-Überschrift */
        [data-testid="stSidebarNavItems"]::before {
            content: '"""+str(app_title)+"""';
            font-size: 24px;
            font-weight: 700;
            position: absolute;
            top: -60px;
            left: 10%;
            text-align: center; /* Text zentrieren */
            display: block;
            width: 80%; /* Die ganze Breite verwenden */
        }
        /* Stil für den Footer-Text in der Sidebar */
        [data-testid="stSidebarNav"]::before {
            content: "🐍 by DavidEpding ©";
            font-size: 14px;
            position: absolute;
            top: -25px;
            left: 10%;
            text-align: center; /* Text zentrieren */
            display: block;
            width: 80%; /* Die ganze Breite verwenden */
            color:#888;
        }
        [data-testid="stSidebarNav"] {
            margin-top:30px;
        }
        .stMainBlockContainer  {
            padding-top:30px;
            
        }
    </style>""",

    unsafe_allow_html=True,
)

 

###### Functions ######

def prophet_forecasting(used_data, date_column, metric_column, train_data_index, model_prediction_steps, dimension_column = None, value = None):
    _df_grouped_data = used_data[[date_column,metric_column]]
    df_grouped_data = _df_grouped_data.groupby(by=date_column).agg(metrics_aggregations[metric_column]).reset_index()
    df_grouped_data[date_column] = pd.to_datetime(df_grouped_data[date_column])

 
    train_data = df_grouped_data[df_grouped_data[date_column] < df_grouped_data[date_column].quantile(train_data_index)]
    test_data = df_grouped_data[df_grouped_data[date_column] >= df_grouped_data[date_column].quantile(train_data_index)]
    train_data_prophet = train_data.reset_index().rename(columns={date_column: 'ds', metric_column: 'y'})

    model = Prophet()
    model.fit(train_data_prophet)
    #test_data_prophet = test_data.reset_index().rename(columns={'date': 'ds'})

    future = model.make_future_dataframe(periods=model_prediction_steps+len(test_data), freq='D', include_history=False)
    forecast = model.predict(future)
    forecast_to_plot = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    df_grouped_data = df_grouped_data.rename(columns={date_column: "ds", metric_column: "y"})
    combined = pd.merge(forecast_to_plot, df_grouped_data, on="ds", how="outer")
    combined.rename(columns={"y": "actual " + metric_column, "yhat": "predicted " + metric_column }, inplace=True)
    #fig = px.line(combined, x="ds", y=["y", "yhat", "yhat_lower", "yhat_upper"], title="Prophet Forecasting")
    
    if dimension_column:
        fig = px.line(combined, x="ds", y=["actual " + metric_column, "predicted " + metric_column], title="Prophet Forecasting von '"+str(metric_column)+"' für " + str(dimension_column) + ": " + str(value), color_discrete_sequence=["lightskyblue", "lightcoral"])
    else:
        fig = px.line(combined, x="ds", y=["actual " + metric_column, "predicted " + metric_column], title="Prophet Forecasting von '"+str(metric_column)+"'", color_discrete_sequence=["lightskyblue", "lightcoral"])
        
    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig)
    
    
    #fig2 = model.plot_components(forecast)
    #st.plotly_chart(fig2)
    
    
    
###### BODY ########

st.title("Forecasting (Skizze)")

 
if "data" in st.session_state:
    #st.sidebar.write("### :two: Wähle dein Modell")
    #st.sidebar.markdown("""<span style="color:#888">Mit der Einordnung der Spalten in DATE, METRIK oder DIMENSION wird das Datenset für das Forecasting vorbereitet.</span>""",unsafe_allow_html=True)
    #st.sidebar.write("### :three: Finetune das Modell")

    #st.sidebar.markdown("""<span style="color:#888">Das Entfernen unnötiger Spalten kann die Performance verbessern.</span>""",unsafe_allow_html=True)
    
    
    data = st.session_state['data']
    date_column = st.session_state['data'][st.session_state['columns']['date_select']].name

    data[date_column] = pd.to_datetime(data[date_column], errors='coerce')

    #date_columns = st.session_state['columns']['date_formats']

    if date_column is not None:
        st.sidebar.write("## Modell Einstellungen")
        st.sidebar.write("### :one: Forecasting definieren")
        #model_selected = st.sidebar.selectbox("Wähle einen ML Algorithmus",options=["Prophet","XGBoost","ARIMA"])
        model_selected = st.sidebar.segmented_control("Wähle einen ML Algorithmus",options=["Prophet","XGBoost","ARIMA"],selection_mode="single",default="Prophet")
        metric_column = st.sidebar.selectbox("Forecasting welcher METRIK?", st.session_state['columns']['metrics'], index=0)
        #date_column = st.sidebar.selectbox("Forecasting auf welcher DATUM-Granularität", date_columns, index=0,key="date_col")
        dimension_checkbox = st.sidebar.checkbox("Forecasting nach Dimension", value=False)

        if dimension_checkbox:
            dimension_column = st.sidebar.selectbox("Forecasting nach DIMENSION?", st.session_state['columns']['dimensions'], placeholder="...")
        else:
            dimension_column = None
            
        if dimension_column is not None:
            if 30 > len(data[dimension_column].unique()) > 5:
                st.sidebar.info("Die Dimension " + dimension_column + " hat " + str(len(data[dimension_column].unique())) + " verschiedene Werte. Für jede Ausprägung wird ein eigenes Modell trainiert, was die Ladezeiten erheblich erhöhen kann.")
            elif len(data[dimension_column].unique()) >= 30:
                st.sidebar.warning("Die Dimension " + dimension_column + " hat " + str(len(data[dimension_column].unique())) + " verschiedene Werte. Für jede Ausprägung wird ein eigenes Modell trainiert, weshalb entweder keine oder eine andere Dimension ausgewählt werden sollte.")

        #date_column = st.session_state['columns']['date_select']

        st.sidebar.write("### :two: Modell-Parameter variieren")
        #st.sidebar.caption("Trainingsdaten Zeitraum festlegen (Standard: vollständiger Zeitraum)")
        min_date = data[date_column].min()
        max_date = data[date_column].max()
        #st.sidebar.header("Datumsauswahl")
        col_date_left, col_date_right = st.sidebar.columns([1,1])
        start_date = col_date_left.date_input("Zeitraum Testdaten", min_date, min_value=min_date, max_value=max_date)
        end_date = col_date_right.date_input("", max_date, min_value=min_date, max_value=max_date)


        train_data_index = st.sidebar.slider("Anteil der Trainingsdaten (Standard: 80%)", min_value=0.3, max_value=1.0, value=0.8, step=0.1)
        features = st.sidebar.multiselect("Wähle Features / Einflussfaktoren (optional)", data.columns.difference([date_column]))
        model_prediction_steps = st.sidebar.select_slider("Prognose von x Tagen in die Zukunft",options=range(1,356),value=30)
        
        
        finetune = st.sidebar.toggle("Finetune Modell?")
        if finetune:
            st.sidebar.write("### :three: Modell Finetuning (Mango)")
            st.sidebar.segmented_control("Growth",options=["linear","logistic","flat"],selection_mode="multi",default=["linear","logistic","flat"])
            st.sidebar.segmented_control("Seasonality",options=["additive","multiplicative"],selection_mode="multi",default=["additive","multiplicative"])
            st.sidebar.slider("Initial Random",min_value=1,max_value=1000,value=20)
            st.sidebar.slider("#Iterations",min_value=5,max_value=100,value=50)
            
        
        submit = st.sidebar.button(":rocket: Prognose starten :chart_with_upwards_trend:",use_container_width=True)
        if submit:

            #clear old plots if exist
            st.empty()
            #Nur Daten aus festgelegtem Zeitraum verwenden
            used_data = data.copy()
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            used_data = used_data[(used_data[date_column] >= start_date) & (used_data[date_column] <= end_date)]
 
            metrics_aggregations = { # hardcoded - should be setting or semi-automatic detection
                'lead_cnt': 'sum',
                'price':'mean',
                'clicks':'sum',
                'impressions':'sum',
                'speed':'mean',
                'provider_id': 'unique',
                'ctr': 'mean',
                'position': 'mean',
                '#Calls': 'sum',
                'Task Created': 'sum',
                'Task Closed': 'sum'
            }

            # Forecasting procedure
            if dimension_column:
                for value in used_data[dimension_column].unique():
                    data_filtered = used_data[used_data[dimension_column] == value]
                    prophet_forecasting(data_filtered, date_column, metric_column, train_data_index, model_prediction_steps, dimension_column, value)     
                            
            else:
                prophet_forecasting(used_data, date_column, metric_column, train_data_index, model_prediction_steps)
            
            with st.expander("Model Evaluation ansehen..."):
                st.write("To Do")
                
            header_left, header_middle, header_right = st.columns([2,2,5])   
            header_middle.button(":chart_with_upwards_trend: Forecast Download  :arrow_heading_down:")
            header_right.button(":page_with_curl: Python Code Download :arrow_heading_down:")    
            
                #with st.expander("Daten des Modells anzeigen..."):
                #    left_side, middle, right_side = st.columns([2,1,1])
                #    left_side.write("##### Daten:")
                #    left_side.data_editor(df_model,key="")
                #    middle.write("##### Trainingsdaten:")
                #    middle.data_editor(X.head(20),key="X")
                #    right_side.write("##### Zielvariable:")
                #    right_side.data_editor(y.head(20),key="y")

    else:
        st.warning("Keine Datumsspalte gefunden. Bitte überprüfe deine Daten.")
else:
    st.warning("Keine Daten gefunden. Bitte lade die Daten zuerst auf der 'Daten laden' Seite hoch.")