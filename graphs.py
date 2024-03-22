import matplotlib.pyplot as plt
import plotly.express as px

def display_utilizzato_per_intermediario(df):

  fig = px.pie(df, values="Utilizzato", names="Intermediario", hole=0.5)
  
  return fig