from utils import italian_date_to_datetime, create_df_from_pdf
from graphs import display_utilizzato_per_intermediario

import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import pandas as pd
import logging

# streamlit conf
st.set_page_config(page_title="ANALISI CENTRALE RISCHI",
                   page_icon=":bar_chart:",
                   layout="wide")
st.title(" :bar_chart: Analisi CR")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',
            unsafe_allow_html=True)

# logger conf
logging.basicConfig(filename='example.log', level=logging.INFO, 
  format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# logger console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.getLogger().addHandler(console_handler)

# frontend
log.info('### ----- Page loaded ----- ###')
pdf_file = st.file_uploader(":file_folder: Upload a file", type=(["pdf"]))

if pdf_file and 'table' not in st.session_state:

  log.info("File uploaded successfully")

  with st.spinner():
    df = create_df_from_pdf(pdf_file)
  log.info("DataFrame created successfully")

  mask = ((df['Accordato'] == df['Accordato Operativo']) |
          (df['Accordato'] == df['Utilizzato']) |
          (df['Accordato Operativo'] == df['Utilizzato']))
  df = df[mask]

  st.session_state['table'] = df
  st.dataframe(df, hide_index=True,
              column_config = {
                "Utilizzato": st.column_config.NumberColumn(format="%d"),
                "Accordato Operativo": st.column_config.NumberColumn(format="%d"),
                "Accordato": st.column_config.NumberColumn(format="%d"),
              })

if 'table' in st.session_state:

  df = st.session_state['table']
  df['Periodo_dt'] = df['Periodo'].apply(italian_date_to_datetime)

  col1, col2 = st.columns((2))

  filtered_df = df[df['Categoria'].isin(['RISCHI AUTOLIQUIDANTI', 'RISCHI A REVOCA'])]

  ratio_df = filtered_df.groupby('Periodo').agg({'Utilizzato':'sum', 'Accordato Operativo':'sum'})
  ratio_df = ratio_df.reset_index()
  ratio_df['Ratio (%)'] = round(ratio_df['Utilizzato'] * 100 / ratio_df['Accordato Operativo'])
  ratio_df = ratio_df[['Periodo', 'Ratio (%)', 'Utilizzato', 'Accordato Operativo']]

  ratio_per_inter = filtered_df.groupby(['Periodo', 'Intermediario']).agg({'Utilizzato':'sum', 'Accordato Operativo':'sum'})
  ratio_per_inter = ratio_per_inter.reset_index()
  ratio_per_inter['Ratio (%)'] = round(ratio_per_inter['Utilizzato'] * 100 / ratio_per_inter['Accordato Operativo'])
  ratio_per_inter = ratio_per_inter[['Periodo', 'Ratio (%)', 'Intermediario', 'Utilizzato', 'Accordato Operativo']]

  with col1:
    st.subheader("Rischi autoliquidanti e a revoca")
    st.caption("Utilizzato su accordato totale")
    st.dataframe(ratio_df, hide_index=True,
                column_config = {
                  "Utilizzato": st.column_config.NumberColumn(format="%d"),
                  "Accordato Operativo": st.column_config.NumberColumn(format="%d"),
                })
    st.caption("Utilizzato su accordato per intermediario")
    st.dataframe(ratio_per_inter,
                 hide_index=True,
                column_config = {
                  "Utilizzato": st.column_config.NumberColumn(format="%d"),
                  "Accordato Operativo": st.column_config.NumberColumn(format="%d"),
                })

  with col2:
    st.subheader("Utilizzato per Intermediario")
    with st.spinner():
      fig = display_utilizzato_per_intermediario(df)
      st.plotly_chart(fig, use_container_width=True)
