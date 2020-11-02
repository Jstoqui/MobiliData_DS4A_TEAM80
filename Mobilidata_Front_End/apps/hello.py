import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json

#Create the app
app = dash.Dash(__name__)

#Create Layout
app.layout = html.Div([
    html.H2("US Sales Map", id='title'), #Creates the title of the app

])

#Initiate the server where the app will work
if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port='8050',debug=True)