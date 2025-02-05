#!/usr/bin/env python
# coding: utf-8
#### Import Libraries and settings ####

import streamlit as st
import pandas as pd
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

 

###### Functions ######

@st.cache_data
def load_data():
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file, sep=';')
        data.reset_index(drop=True, inplace=True)
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
        data.reset_index(drop=True, inplace=True)
    else:
        st.error("Fehler: Dateiformat nicht unterstützt.")
        #st.stop()
        
    st.session_state["filename"] = uploaded_file.name
    st.session_state["data"] = data
    st.session_state['columns'] = {'unspecified':data.columns}
    date_columns = [col for col in data.columns if pd.api.types.is_datetime64_any_dtype(data[col])]
    if len(date_columns) == 0:
        date_columns = data.columns
    st.session_state['columns']['dates'] = list(date_columns)
    #st.session_state["data"]["date"] = pd.to_datetime(st.session_state["data"]["date"], errors='coerce')

    col_count, row_count = data.shape
    col_count_str = '{:,}'.format(col_count).replace(',', '.')
    st.success("Daten erfolgreich geladen ("+str(col_count_str)+" Zeilen x "+str(row_count)+" Spalten) aus File: "+st.session_state["filename"])


###### Load Data ########

st.title("Daten laden")

st.sidebar.write("### :one: Lade deine Daten hoch")
uploaded_file = st.sidebar.file_uploader("Wähle eine CSV- oder Excel-Datei", type=["csv", "xlsx"])


if uploaded_file:
    load_data.clear()
    load_data()
else:
    if "data" in st.session_state:
        st.info("Daten bereits geladen: '"+str(st.session_state["filename"])+"'. Alternativ kannst du links in der Sidebar eine neue Datei hochladen.")
    else:
        st.info("Bitte lade eine Datei hoch.")

 

if "data" in st.session_state:
    st.sidebar.write("### :two: Erkläre dein Datenset")
    st.sidebar.markdown("""<span style="color:#888">Mit der Einordnung der Spalten in DATE, METRIK oder DIMENSION wird das Datenset für das Forecasting vorbereitet.</span>""",unsafe_allow_html=True)
    st.sidebar.write("### :three: Unnötige Spalten entfernen")

    st.sidebar.markdown("""<span style="color:#888">Das Entfernen unnötiger Spalten kann die Performance verbessern.</span>""",unsafe_allow_html=True)
    st.write("#### Erkläre dein Datenset: Ordne die Spalten ein in DATE, METRIK oder DIMENSION")
    sec1_left1,sec1_left2,sec1_middle,sec1_right = st.columns([3,1,2,2])
    data = st.session_state['data']
    df_columns = list(data.columns)

    if not "columns" in st.session_state:
        st.session_state['columns'] = {'unspecified':df_columns}
        date_columns = [col for col in df_columns if pd.api.types.is_datetime64_any_dtype(data[col])]
        if len(date_columns) == 0:
            date_columns = df_columns
        st.session_state['columns']['dates'] = list(date_columns)
    elif 'unspecified' not in st.session_state['columns'] or 'dates' not in st.session_state['columns']:
        st.session_state['columns']['unspecified'] = df_columns
        date_columns = [col for col in df_columns if pd.api.types.is_datetime64_any_dtype(data[col])]
        if len(date_columns) == 0:
            date_columns = df_columns
        st.session_state['columns']['dates'] = list(date_columns)

    ### Multiselects für Date, Dateformat, Metrics, Dimensions ###
    if "date_select" not in st.session_state['columns']:
        st.session_state['columns']['date_select'] = sec1_left1.selectbox("DATUM-Spalte", st.session_state['columns']['dates'], help="Die DATUM-Spalte wird für das Forecasting verwendet - idealerweise enthält sie alle notwendigen Datums- und Zeit-Informationen in einem Datetime-String, von dem Details abgeleitet werden (Monat, Wochentag, Stunde etc.)")
    else:
        st.session_state['columns']['date_select'] = sec1_left1.selectbox("DATUM-Spalte", st.session_state['columns']['dates'], index = st.session_state['columns']['dates'].index(st.session_state['columns']['date_select']), help="Die DATUM-Spalte wird für das Forecasting verwendet - idealerweise enthält sie alle notwendigen Datums- und Zeit-Informationen in einem Datetime-String, von dem Details abgeleitet werden (Monat, Wochentag, Stunde etc.)")

    if "date_format" not in st.session_state['columns']:
        st.session_state['columns']['date_format'] = sec1_left2.text_input("Datumsformat (optional)", key="date_format", placeholder="%Y/%m/%d", value="%Y/%m/%d",help="Gib das Datumsformat an, falls es nicht automatisch erkannt wird (z.B. '%Y/%m/%d')")
    else:
        #last_selection = st.session_state['columns']['date_format']
        st.session_state['columns']['date_format'] = sec1_left2.text_input("Datumsformat (optional)", key="date_format", placeholder="%Y/%m/%d", value=st.session_state['columns']['date_format'],help="Gib das Datumsformat an, falls es nicht automatisch erkannt wird (z.B. '%Y/%m/%d')")

    date_column = st.session_state['columns']['date_select']
    if "metrics" not in st.session_state['columns']:
        st.session_state['columns']['metrics'] = []
    selected_options = sec1_middle.multiselect("METRIK-Spalten", st.session_state['columns']['unspecified'].difference([date_column]), default = st.session_state['columns']['metrics'], key="metric_cols", help="METRIC-Spalten sind numerische Kennzahlen, die später entweder für das Forecasting ODER als Features verwendet werden können. Sie müssen über mehrere Zeilen aggregierbar sein (Summe, Durchschnitt, Max, Min).")
    st.session_state['columns']['metrics'] = selected_options

    if "dimensions" not in st.session_state['columns']:
        st.session_state['columns']['dimensions'] = sec1_right.multiselect("DIMENSIONS-Spalten", st.session_state['columns']['unspecified'], key="dimension_cols",help="DIMENSIONS-Spalten sind disktinkte Kategorien ohne Ordnung/zählbar zu sein, bspw. eine Klassifizierung via strings oder auch IDs - sie ermöglichen später das Datenset in unterschiedlichen Dimensionen/Schichten zu filtern")
    else:
        st.session_state['columns']['dimensions'] = sec1_right.multiselect("DIMENSIONS-Spalten", st.session_state['columns']['unspecified'], default=st.session_state['columns']['dimensions'], key="dimension_cols",help="DIMENSIONS-Spalten sind disktinkte Kategorien ohne Ordnung/zählbar zu sein, bspw. eine Klassifizierung via strings oder auch IDs - sie ermöglichen später das Datenset in unterschiedlichen Dimensionen/Schichten zu filtern")

    #if date_column:
    #    try:
    #        st.session_state["data"][date_column] = pd.to_datetime(st.session_state["data"][date_column], format=st.session_state['columns']['date_format'], errors='coerce')
    #        #if pd.isnull(np.datetime64(st.session_state["data"][date_column].iloc[0])):
    #        #    st.session_state["data"][date_column] = pd.to_datetime(st.session_state["data"][date_column], format="%Y-%m-%d", errors='coerce')
    #        if 'date_select' in st.session_state['columns']:
    #            st.session_state['data']['year'] = st.session_state['data'][st.session_state['columns']['date_select']].dt.year
    #            st.session_state['data']['month'] = st.session_state['data'][st.session_state['columns']['date_select']].dt.month
    #            st.session_state['data']['day'] = st.session_state['data'][st.session_state['columns']['date_select']].dt.day
    #            st.session_state['data']['weekday'] = st.session_state['data'][st.session_state['columns']['date_select']].dt.dayofweek
    #    except Exception as e:
    #        st.error(f"Ungültige Datumsspalte: {e}")

   

 

    ### Datenvorschau ###
    st.write("#### Vorschau der Daten: erste vs. letzte 5 Zeilen")
    left_side,right_side = st.columns(2)
    left_side.write(st.session_state["data"].head(5))
    right_side.write(st.session_state["data"].tail(5))

   

    columns_to_drop = st.multiselect("Wähle die Spalten, die du entfernen möchtest:", st.session_state["data"].columns)
    if columns_to_drop:
        st.write("#### Aktualisierte Datenvorschau:")
        st.session_state["data"].drop(columns=columns_to_drop, inplace=True)
        st.write(f"Die folgenden Spalten wurden entfernt: {columns_to_drop}")
        left_side,right_side = st.columns(2)
        left_side.write(st.session_state["data"].head(5))
        right_side.write(st.session_state["data"].tail(5))


# toller_button = st.button("Test-Button")
# if toller_button:
#     for i in st.session_state['data'].columns:
#         st.write(i + " " + str(st.session_state['data'][i].dtype))