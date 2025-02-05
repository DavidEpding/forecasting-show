#!/usr/bin/env python
# coding: utf-8
#### Import Libraries and settings ####
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
 


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

debug_mode = st.sidebar.toggle("Debug Mode")

############## Functions #################
 

def ausreißer_ermitteln():
    st.session_state.ausreißer_clicked = True

############# Body ####################
st.title("Data Check")
# Sicherstellen, dass Daten geladen wurden
if 'data' in st.session_state:
    data = st.session_state['data']
    if 'columns' not in st.session_state:
        st.warning("Bitte lade zuerst ein Datenset und definiere die Spalten-Typen auf der 'Daten laden' Seite.")
    else:
        if 'metrics' not in st.session_state['columns'] or 'date_select' not in st.session_state['columns']:
            st.warning("Bitte definiere für dein Datenset zuerst die Spalten-Typen auf der 'Daten laden' Seite.")
        else:
            if len(st.session_state['columns']['metrics'])<1:
                st.warning("Bitte definiere für dein Datenset zuerst die eine Metric-Spalte auf der 'Daten laden' Seite.")
            date_column = st.session_state['columns']['date_select']
    #st.write(st.session_state['columns'])
    
    # Überprüfen, ob es eine Datumsspalte gibt
    date_columns = st.session_state['columns']['dates']
    if date_columns:
        st.sidebar.write("### :one: Check Dimensionen (Histogramme)")
        
        st.sidebar.write("### :two: Daten visuell prüfen (Zeitverlauf)")
        if date_column:
            #data_by_date = data.groupby(date_column).sum()#.reset_index()
            #with st.expander("Daten einblenden..."):
            #    st.write("Data grouped by DATE-column '"+date_column+"'")
            #    st.write(data_by_date)

            # automatically check creation date-formats from date column
            data_column_formats = [date_column]
            df_data_formats = data
            data[date_column] = pd.to_datetime(data[date_column], errors='coerce')
            try:
                df_data_formats["month-name"] = "m"+data[date_column].dt.month.astype(str)
                data_column_formats.append("month-name")
            except Exception as e:
                if debug_mode:
                    st.warning("Could not convert DATUM-Spalte to Month-Name")
                    st.error(e)
            try:
                df_data_formats["month"] = data[date_column].dt.month
                data_column_formats.append("month")
            except Exception as e:
                if debug_mode:
                    st.warning("Could not convert DATUM-Spalte to month")
                    st.error(e)
            try:
                df_data_formats["year"] = data[date_column].dt.year
                df_data_formats["year"] = data['year'].astype(str)
                data_column_formats.append("year")
            except Exception as e:
                if debug_mode:
                    st.warning("Could not convert DATUM-Spalte to year")
                    st.error(e)
                    
            st.session_state['columns']['date_formats'] = data_column_formats

        visualize_dates = st.sidebar.multiselect("Wähle DATUM-Spalten zur Visualisierung", data_column_formats,key="viz_dates",default=[date_column])
        visualize_metrics = st.sidebar.multiselect("Wähle METRIK-Spalten zur Visualisierung", st.session_state['columns']['metrics'], key="viz_metrics",default=st.session_state['columns']['metrics'][0])
        visualize_dimensions = st.sidebar.multiselect("Wähle DIMENSIONS-Spalten zur Visualisierung", st.session_state['columns']['dimensions'], key= "viz_dims")

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
        
        metric_col = visualize_metrics[0] if len(visualize_metrics) > 0 else "lead_cnt"
        ui_section_cols = {}

        with st.expander("**Check Dimensionen (Histogramme)...**", expanded=False):
            for dimension in st.session_state['columns']['dimensions']:
                dimension_unique_values = len(data[dimension].unique())
                st.write("##### '"+str(dimension)+"' ("+str(dimension_unique_values)+" unique values)")
                if dimension_unique_values > 7:
                    st.error("**Dimension nicht geeignet ODER Metrik falsch klassifiziert**: Zu viele Ausprägungen für '"+str(dimension)+"' - bitte nicht verwenden")
                    
                #df_dim_hist_chart = data[dimension].value_counts().reset_index().rename(columns={'index': dimension, 0: 'count'})
                df_dim_hist = data.groupby(by=dimension).agg({''+metric_col+'':["count","sum","mean","max","min"]}).reset_index()
                #df_dim_hist = data[[dimension,metric_col]].groupby(by=dimension).describe()
                df_dim_hist.columns = ['_'.join(col) if not 'count' in col else 'count' for col in df_dim_hist.columns]
                df_dim_hist.rename(columns={dimension+'_':dimension},inplace=True)
                df_dim_hist.sort_values(by="count",ascending=False,inplace=True)

                # add % of total for count and sum
                df_dim_hist_table = df_dim_hist
                count_total = df_dim_hist["count"].sum()
                metric_col_total = df_dim_hist[metric_col+"_sum"].sum()
                count_col_pos = df_dim_hist_table.columns.get_loc("count")
                df_dim_hist_table.insert(count_col_pos+1,"%count",round(df_dim_hist["count"]/count_total*100,1))
                metric_col_pos = df_dim_hist_table.columns.get_loc(metric_col+"_sum")
                df_dim_hist_table.insert(metric_col_pos+1,"%"+metric_col+"_sum",round(df_dim_hist[metric_col+"_sum"]/metric_col_total*100,1))


                # display data as table and chart
                df_dim_hist_chart = df_dim_hist_table[[dimension,"count"]]
                ui_section_cols[dimension+" hist"] = st.columns(2)
                ui_section_cols[dimension+" hist"][0].write(df_dim_hist)
                #ui_section_cols[dimension+" hist"][0].write(data[[dimension,metric_col]].groupby(by=dimension).describe())
                ui_section_cols[dimension+" hist"][1].bar_chart(df_dim_hist_chart,x=dimension)

        with st.expander("**Daten Visualisierungen prüfen (Zeitverlauf)...**"):
            st.info("**Prüfe die Daten auf Verzerrungen, Ausreißer und Anomalien**   \nVerzerrungen, Ausreißer, Anomalien können dein Forecasting signifikant verzerren und dein Modell schwächen.  \nEnthält dein Datenset zu einem Großteil Daten einer bestimmten Ausprägung (Dimension), dann wird das Forecasting Modell stark von dieser Kategorie bestimmt - prüfe, ob das für die Aussagekraft deines Modells relevant ist.")
            st.write("##### '"+metric_col+"' ("+metrics_aggregations[metric_col]+") im Zeitverlauf")

            if(len(visualize_dates) < 1):
                st.warning("Bitte DATUM-Spalte zur Visualisierung auswählen")
            else:
                df_visualize = df_data_formats.groupby(by=visualize_dates).agg(metrics_aggregations[metric_col],numeric_only=True).reset_index()
                ui_section_cols["viz_all"] = st.columns(2)
                if len(visualize_dates) == 1:
                    df_visualize_all = df_visualize[[metric_col]].describe()
                    ui_section_cols["viz_all"][0].write(df_visualize_all)
                    ui_section_cols["viz_all"][1].line_chart(df_visualize,x=visualize_dates[0] ,y= metric_col, use_container_width=True)
                else:
                    df_visualize_all = df_visualize.describe()
                    ui_section_cols["viz_all"][0].write(df_visualize_all)
                    ui_section_cols["viz_all"][1].line_chart(df_visualize,x=visualize_dates[0] ,y= metric_col,color= visualize_dates[1], use_container_width=True)

                for dimension in visualize_dimensions:
                    dimension_unique_values = list(data[dimension].unique())
                    st.write("##### '"+str(dimension)+"' ("+str(len(dimension_unique_values))+" unique values)")
                    df_visualize_dim = df_data_formats.groupby(by=visualize_dates+[dimension]).agg(metrics_aggregations[metric_col],numeric_only=True).reset_index()
                    df_visualize_dim_chart = df_visualize_dim.groupby(by=[visualize_dates[0]]+[dimension]).agg(metrics_aggregations[metric_col],numeric_only=True).reset_index()

                    ui_section_cols["dim_overview"] = st.columns(2)
                    if 'id' in dimension:
                        df_visualize_dim_chart[dimension+'str'] = "id_"+df_visualize_dim_chart[dimension].astype(str)
                        df_visualize_dim_hist = df_visualize_dim[[dimension,metric_col]].groupby(by=dimension).describe()
                        df_visualize_dim_hist.columns = ['_'.join(col) if not 'count' in col else 'count' for col in df_visualize_dim_hist.columns]
                        ui_section_cols["dim_overview"][0].write(df_visualize_dim_hist)
                        ui_section_cols["dim_overview"][1].line_chart(df_visualize_dim_chart,x=visualize_dates[0],y= metric_col,color=dimension+'str', use_container_width=True)
                    else:
                        df_visualize_dim_hist = df_visualize_dim[[dimension,metric_col]].groupby(by=dimension).describe()
                        df_visualize_dim_hist.columns = ['_'.join(col) if not 'count' in col else 'count' for col in df_visualize_dim_hist.columns]
                        ui_section_cols["dim_overview"][0].write(df_visualize_dim_hist)
                        ui_section_cols["dim_overview"][1].line_chart(df_visualize_dim_chart,x=visualize_dates[0],y= metric_col,color=dimension, use_container_width=True)

                    for dim_value in dimension_unique_values:
                        df_chart = df_visualize_dim[df_visualize_dim[dimension]==dim_value]
                        st.write("###### "+str(dimension)+" '"+str(dim_value)+"'")
                        if len(visualize_dates) == 1:
                            for metric_col in visualize_metrics:
                                st.line_chart(df_chart,x=visualize_dates[0] ,y=metric_col, use_container_width=True)
                        elif len(visualize_dates) == 2:
                            for metric_col in visualize_metrics:
                                try:
                                    st.line_chart(df_chart,x=visualize_dates[0] ,y= metric_col,color= visualize_dates[1], use_container_width=True)
                                except:
                                    st.warning("Could not set color by '"+str(visualize_dates[1])+"'")
                                    df_chart = df_chart.groupby(by=[visualize_dates[0]]+[dimension]).agg(metrics_aggregations[metric_col]).reset_index()
                                    st.line_chart(df_chart,x=visualize_dates[0] ,y= metric_col, use_container_width=True)
                        else:
                            st.info("Please select only a max of two DATE columns")

        st.sidebar.write("### :three: Korrelationen betrachten")
        with st.expander("**Korrelationen der Metriken betrachten...**"):
            st.write("#### Korrelationen zwischen den METRIK-Spalten")
            if len(visualize_metrics) < 2:
                st.info("Füge eine zweite METRIK-Spalte hinzu, um Korrelationen anzeigen zu lassen.")
            else:
                st.info("**Sind die Korrelationen inhaltlich begründet und signifikant?**   \nWillst Du eine Metrik forecasten, die stark von externen Faktoren/Metriken beeinflusst wird, wird dein Modell ohne diese Faktoren nicht gut funktionieren.   \nSind diese Faktoren zum Großteil unmodellierbaren externen Faktoren unterlegen, wird ein Forecasting nicht erfolgreich sein.")
                df_corr = df_visualize[visualize_metrics].corr()
                df_corr = df_corr.round(2).style.background_gradient(axis=0,cmap='RdBu',vmin=-0.7,vmax=0.7).format(na_rep='MISS', precision=2)
                st.write(df_corr)
                
                if len(visualize_dimensions)>0:
                    st.write("#### Korrelationen nach DIMENSIONS-Spalte: '"+str(dimension)+"'")
                for dimension in visualize_dimensions:
                    df_visualize_dim = df_data_formats.groupby(by=visualize_dates+[dimension]).agg(metrics_aggregations[metric_col],numeric_only=True).reset_index()
                    ui_section_cols["corr_dims"] = {}
                    dimension_unique_values = list(data[dimension].unique())
                    ui_section_cols["corr_dims"][dimension] = st.columns(len(dimension_unique_values))
                    for num, dim_value in enumerate(dimension_unique_values):
                        df_dim_value = df_visualize_dim[df_visualize_dim[dimension]==dim_value]
                        df_corr_dim = df_dim_value[visualize_metrics].corr()
                        df_corr_dim = df_corr_dim.round(2).style.background_gradient(axis=0,cmap='RdBu',vmin=-0.7,vmax=0.7).format(na_rep='MISS', precision=2)
                        ui_section_cols["corr_dims"][dimension][num].write("###### Korrelationen bei '"+str(dim_value)+"'")
                        ui_section_cols["corr_dims"][dimension][num].write(df_corr_dim)

#### OLDER CODE ####

        if False:#if features:
            grouped_data = pd.DataFrame()  # QUICKFIX
            features = [] # QUICKFIX
            # Daten sortieren nach Datum
            #data = data.sort_values(by=date_column)
            # Datenframe für die Visualisierung vorbereiten
            #data_to_plot = grouped_data[[date_column] + features]#.set_index(date_column)
            data_to_plot = grouped_data

            with st.expander("Daten einblenden..."):
                st.write(grouped_data)
                st.write(data_to_plot)

            plot_title = "Zeitverlauf der Features "+" & ".join(['"'+str(f)+'"' for f in features])
            #fig = px.line(data_to_plot, x=date_column, y=features, title=plot_title)
            fig = px.line(data_to_plot, x=date_column, y="lead_cnt", title=plot_title, color="provider_id",height=600)
            st.plotly_chart(fig, use_container_width=True)
 
            st.button(":o: Ausreißer ermitteln", on_click=ausreißer_ermitteln)
            Q_values = st.sidebar.slider("Ausreißer Threshhold", value=[0.25, 0.75], min_value=0.01, max_value=0.99, step=0.01)
        else:
            if False:
                st.info("Bitte wähle mindestens ein Feature zur Visualisierung aus.")

    else:
        st.warning("Keine Datumsspalte gefunden. Bitte überprüfe deine Daten.")
else:
    st.warning("Keine Daten gefunden. Bitte lade die Daten zuerst auf der 'Daten laden' Seite hoch.")

 

if 'ausreißer_clicked' not in st.session_state:
    st.session_state.ausreißer_clicked = False


if st.session_state.ausreißer_clicked:
    features = [st.session_state['columns']['date_select']]

    if features:
        for feature in features:
            # Berechne IQR und identifiziere Ausreißer
            Q1 = grouped_data[feature].quantile(Q_values[0])
            Q3 = grouped_data[feature].quantile(Q_values[1])

            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

        # Erstelle eine Spalte, die Ausreißer markiert
        grouped_data[f"{feature}_outlier"] = np.where((grouped_data[feature] < lower_bound) | (grouped_data[feature] > upper_bound), "Ausreißer", "Kein Ausreißer")

        # Datenframe für die Visualisierung vorbereiten
        data_to_plot = grouped_data[[date_column] + features + [f"{feature}_outlier" for feature in features]]

        # Interaktive Zeitreihengrafik mit Plotly und Markierung von Ausreißern
        for feature in features:
            fig = px.line(data_to_plot, x=date_column, y=feature, title=f'Zeitverlauf und Ausreißer von {feature}')
            # Füge die Ausreißer als Scatter Plot hinzu
            outliers = data_to_plot[data_to_plot[f"{feature}_outlier"] == "Ausreißer"]
            fig.add_scatter(x=outliers[date_column], y=outliers[feature], mode='markers', name='Ausreißer', marker=dict(color='red', size=10, symbol='x'))
            st.plotly_chart(fig, use_container_width=True)