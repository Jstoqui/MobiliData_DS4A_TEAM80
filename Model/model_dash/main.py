import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import os
import pandas as pd
import datetime
import math
from datetime import date
import datetime
from utils import *
import joblib
import xgboost as xgb
from warnings import filterwarnings
filterwarnings('ignore')


dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server

# Load data
df = pd.read_csv("siniestros_con_hipotesis.csv")
siniestrost = pd.DataFrame(df.groupby('FECHA')['CODIGO_SINIESTRO'].count().reset_index(name='Cantidad_siniestros'))
siniestrost['FECHA'] = pd.to_datetime(siniestrost['FECHA'])
siniestrost = siniestrost.sort_values(by=['FECHA'])
siniestrost.set_index('FECHA', inplace=True)
siniestrost.index.rename('From', inplace=True)

training_df = siniestrost.groupby(['From'])['Cantidad_siniestros'].sum().reset_index()
training_df['Date'] = pd.to_datetime(training_df['From']).dt.date
training_df['From'] = pd.to_datetime(training_df['From'])
training_df.set_index('From', inplace=True)
training_df = training_df['2016-01-01':]

# Figure
data = [
    go.Scatter(x=training_df['20190901':'20191231'].index, y=training_df['Cantidad_siniestros']['20190901':'20191231'], mode="lines")
]
fig = go.Figure(
    data=data
)


# Model load
model = joblib.load("model_xgb_gridcv.joblib")


dash_app.layout = dbc.Container([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Filter by"),
                ], style={'marginBottom': 50, 'marginTop': 30, "color": "white", "text-align": "center"}),
                html.Div([
                    html.H2("Date Picker"),
                    dcc.DatePickerRange(
                        id="range-picker",
                        start_date=date(2019,9,1),
                        end_date=date(2019,12,31),
                        display_format='YYYY-MM-DD',
                        start_date_placeholder_text='YYYY-MM-DD'
                    )
                ])
            ],
            width={"size":2},
            style={"background-color": "#2f2935"}
            ),
            dbc.Col([
                html.Div(dcc.Graph(id="time-plot", figure=fig), style={"border":"2px #6c757d solid", "border-radius": "4px"})
            ])
        ])
    ])
], fluid=True
)

# callbacks
'''
Feature matrix:

'dayofweek',  'month', 'dayofyear',
         'dayofmonth', 'weekofyear'

Filtro dropdown: Para
Descriptivas de la series predicha: min, max, media
'''

@dash_app.callback(
    Output("time-plot", "figure"),
    [Input('range-picker', 'start_date'),
    Input('range-picker', 'end_date') ])
def get_date_range(start_date, end_date):
    feat_mat_df = get_feature_matrix(start_date, end_date)
    prediction = model.predict(feat_mat_df)
    # Plot figure
    data = [
        go.Scatter(x=training_df['20190901':'20191231'].index, y=training_df['Cantidad_siniestros']['20190901':'20191231'], mode="lines"),
        go.Scatter(x=feat_mat_df.index, y=prediction, mode="lines")
    ]
    fig = go.Figure(
        data=data
    )
    return fig

if __name__ == '__main__':
    dash_app.run_server(debug=True)
