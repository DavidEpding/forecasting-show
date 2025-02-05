#!/usr/bin/env python
# coding: utf-8
#### Import Libraries and settings ####
import streamlit as st
import numpy as np
import pandas as pd
import os
import xlsxwriter
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

import time
import datetime


today_str = datetime.datetime.today().strftime('%Y%m%d') # heutiges Datum als Default-Wert für Dateiname
year_str = today_str[0:4]
month_str = today_str[-4:-2]
day_str = today_str[-2:]



pyToolName = "ForeCasting-Show v0.9"
default_directory = "C:\\Users\\Nutzer\\Desktop\\TheSERPiant\\Forecasting"

###### Header ########
st.set_page_config(layout="wide",page_title=pyToolName,page_icon=":gorilla:")
st.markdown(
    """
    <style>
        /* Stil für die Sidebar-Überschrift */
        [data-testid="stSidebarNavItems"]::before {
            content: '"""+str(pyToolName)+"""';
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

#st.sidebar.markdown("""<h1>fc - Forecasting</h1><p style="font-size:15px;color:#888;margin-top:-15px">🐍 by DavidEpding ©</p>""",unsafe_allow_html=True)
st.sidebar.markdown("""<span style="font-size:14px;color:#eee"><em>This app helps you to upload a dataset, transform it and run basic Forecasting Models to compare.</em></span>""",unsafe_allow_html=True)

st.sidebar.write("### Steps")
st.sidebar.write(":one:  Upload Data  \n:two:  Check Data  \n:three:  Run Forecasting")
st.sidebar.write("---")

st.title("ForeCasting-Show: The stage is yours! :rocket:")
st.write(":dart: This app aims to provide a **quickstart into Forecasting**.  \n  \nUpload **your dataset** of choice, check whether their suitable for Forecasting and run basic Forecasting algorithms.  \nFuture versions will offer downloads of your forecasted data, the specs of your model AND the python code for implementation.")