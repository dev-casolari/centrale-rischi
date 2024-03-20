from utils import italian_date_to_datetime, create_df_from_pdf

import plotly.express as px
import streamlit as st
import pandas as pd
import logging
import os

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
log.info('Page loaded')
pdf_file = st.file_uploader(":file_folder: Upload a file", type=(["pdf"]))

if pdf_file and 'table' not in st.session_state:

  log.info("File uploaded successfully")

  df = create_df_from_pdf(pdf_file)
  log.info("DataFrame created successfully")

  mask = ((df['Accordato'] == df['Accordato Operativo']) |
          (df['Accordato'] == df['Utilizzato']) |
          (df['Accordato Operativo'] == df['Utilizzato']))
  df = df[mask]

  st.session_state['table'] = df

if 'table' in st.session_state:
  df = st.session_state['table']
  st.dataframe(df)

if 'table' in st.session_state:

  df = st.session_state['table']
  df['Periodo_dt'] = df['Periodo'].apply(italian_date_to_datetime)
  startDate = pd.to_datetime(df["Periodo_dt"]).min()
  endDate = pd.to_datetime(df["Periodo_dt"]).max()
  st.session_state['dates'] = [startDate, endDate]

  col1, col2 = st.columns((2))

  with col1:
    date1 = st.date_input("Start Date", startDate)
    date1 = pd.to_datetime(date1)

  with col2:
    date2 = st.date_input("End Date", endDate)
    date2 = pd.to_datetime(date2)

  df = df[(df["Periodo_dt"] >= date1) & (df["Periodo_dt"] <= date2)].copy()

  # Filter the DataFrame to include only "RISCHI AUTOLIQUIDANTI" and "RISCHI A SCADENZA"
  filtered_df = df[df['Categoria'].isin(
      ['RISCHI AUTOLIQUIDANTI', 'RISCHI A REVOCA'])]
  # Create a new DataFrame with the desired calculation
  ratio_df = filtered_df.groupby('Periodo_dt').apply(lambda group: group[
      'Utilizzato'].sum() / group['Accordato Operativo'].sum()).reset_index(
          name='Utilizzato su Acc. Operativo')
  ratio_df = ratio_df.sort_values('Periodo_dt')
  ratio_df['Utilizzato su Acc. Operativo (%)'] = ratio_df[
      'Utilizzato su Acc. Operativo'] * 100

  with col1:
    st.subheader("Utilizzato su Accordato Operativo")
    fig = px.bar(ratio_df,
                 x="Periodo_dt",
                 y="Utilizzato su Acc. Operativo (%)",
                 template="seaborn")
    st.write(ratio_df)
    st.plotly_chart(fig, height=200)
    # st.subheader("Utilizzato su Accordato Operativo per Intermediario")
    # st.write(filtered_df.groupby('Periodo_dt'))

  with col2:
    st.subheader("Utilizzato per Intermediario")
    fig = px.pie(df, values="Utilizzato", names="Intermediario", hole=0.5)
    fig.update_traces(text=df["Intermediario"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
