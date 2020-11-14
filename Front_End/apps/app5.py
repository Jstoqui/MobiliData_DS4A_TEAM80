import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import os
import pandas as pd
import datetime
import uuid
import csv 
from urllib.parse import quote as urlquote
# from flask import Flask, send_from_directory
from google.cloud import storage

from datetime import date
import datetime
import json
from utils import *
import joblib
import os
import numpy as np
import xgboost as xgb
import requests
from collections import deque
from warnings import filterwarnings
filterwarnings('ignore')


dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server


# Model endpoint (1.2.1) MEDIA, DIA CON MAYOR (cantidad y fecha) Y MENOR SINIESTROS (DEL PERIODO SELECCIONADO)
base_model_url = "https://scenic-kiln-292815.ue.r.appspot.com/predict/"

# Load data
df = pd.read_csv("siniestros_con_hipotesis.csv")
# Data wrangling
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

# KPI VALUES
year, month, day = datetime.datetime.now().isoformat()[0:10].split("-")
average_sinisters = 0
day_least_sinisters, num_least_sinisters = 0,0
day_most_sinisters, num_most_sinisters = 0,0


# Figure
data = [
    go.Scatter(x=training_df['20190901':'20191231'].index, y=training_df['Cantidad_siniestros']['20190901':'20191231'], mode="lines")
]
layout = go.Layout(title="Average Sinisters", xaxis={"title": "Date"}, yaxis={"title": "# Siniestros"})
fig_init = go.Figure(
    data=data,
    layout=layout
)


predicted_data = ""
time_data = ""

dash_app.layout = dbc.Container([
        html.Div([
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H2("Filter by"),
                        ], style={'marginBottom': 50, 'marginTop': 30, "color": "white", "text-align": "center"}),
                        html.Div([
                            html.H2("Date Picker", style={"color": "white", 'marginBottom': 25, 'marginTop': 25, "text-align": "center"}),
                            dcc.DatePickerRange(
                                id="range-picker",
                                min_date_allowed=date(2019, 9, 1),
                                start_date=date(2019,9,1),
                                end_date=date(2019,12,31),
                                display_format='YYYY-MM-DD',
                                clearable=True,
                                calendar_orientation="horizontal",#vertical
                                start_date_placeholder_text='Start Date',
                                with_portal=False,
                                number_of_months_shown=2,
                                updatemode="bothdates",
                                minimum_nights=1,
                                reopen_calendar_on_clear=True,
                            ),
                        ], style={'marginBottom': 50, 'marginTop': 25}),
                        html.Div(id='predicted-data', style={'display': 'none'}, children = predicted_data),
                        html.Div(id='time-data', style={'display': 'none'}, children = time_data),
                    ], 
                        width={"size":2},
                        style={"background-color": "#2f2935"}),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.Div(dcc.Graph(id="time-plot", figure=fig_init, animate=True))
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Alert([
                                    "Take into account that the higher the prediction range, the lower the accuracy of predictions",
                                ])
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                kpi_component(
                                    header="Average of sinisters predicted",
                                    body=average_sinisters,
                                    id_header="header-sinister",
                                    id_body="mean-sinister",
                                    color="primary"),
                            ], style={'marginBottom': 25, 'marginTop': 25}),
                            dbc.Col([
                                kpi_component(
                                    header="The day with least sinisters predicted is...",
                                    body="{}\nwith {} sinisters".format(day_least_sinisters, num_least_sinisters),
                                    id_header="header-sinister2",
                                    id_body="min-sinister",
                                    color="secondary"),
                            ], style={'marginBottom': 25, 'marginTop': 25}),
                            dbc.Col([
                                kpi_component(
                                    header="Day with most sinisters predicted",
                                    body="{}\nwith {} sinisters".format(day_most_sinisters, num_most_sinisters),
                                    id_header="header-sinister3",
                                    id_body="max-sinister",
                                    color="info"),
                            ], style={'marginBottom': 25, 'marginTop': 25})
                        ]),
                    ])
                ])
            ])
        ])
    ],
    fluid=True
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
    [Output("time-plot", "figure"),
    Output("mean-sinister", "children"),
    Output("min-sinister", "children"),
    Output("max-sinister", "children"),
    Output("predicted-data", "children"),
    Output("time-data", "children")
    ],
    # [Input("button-pred", "n_clicks"),
    [Input('range-picker', 'start_date'),
    Input('range-picker', 'end_date')]
)
def on_button_click(start_date, end_date):
    print("entre")
    print(start_date, end_date)
    if start_date is None or end_date is None:
        print("aqui")
        fig = go.Figure(
            data=[]
        )
        return [
            fig,
            str(0),
            "{}\nwith {} sinisters".format("unknown", 0),
            "{}\nwith {} sinisters".format("unknown", 0),
            "",
            ""
        ]

    model_url = "{}/generalModel".format(base_model_url)
    data = json.dumps({"start_date": start_date, "end_date": end_date})
    headers = {"Content-Type": "application/json"}
    r_model = requests.post(model_url, data=data, headers=headers)

    x_time = get_x_time_vector(start_date, end_date)

    if r_model.json().get("success") == True:
        mean_prediction = json.loads(r_model.json()["prediction"].get("mean_prediction"))

        # Determine average, min, max
        average = "{:.2f}".format(np.mean(mean_prediction))
        num_most_sinisters = "{:.0f}".format(int(np.max(mean_prediction)))
        num_least_sinisters = "{:.0f}".format(int(np.min(mean_prediction)))

        day_most_sinisters = x_time[np.argmax(mean_prediction)].isoformat()[0:10]
        day_least_sinisters = x_time[np.argmin(mean_prediction)].isoformat()[0:10]

        data = [
            go.Scatter(x=training_df['20190901':'20191231'].index, y=training_df['Cantidad_siniestros']['20190901':'20191231'], mode="lines", name="Actual"),
            go.Scatter(x=x_time, y=mean_prediction, mode="lines", name="Predicted")
        ]
        layout = go.Layout(title="Average Sinisters", xaxis={"title": "Date"}, yaxis={"title": "# Siniestros"})
        fig = go.Figure(
            data=data,
            layout=layout
        )
        
        fig.update_xaxes(
            range=(training_df['20190901':'20191231'].index[0], x_time[-1])
        )

        print("exito")

        return [
            fig,
            str(average),
            "{}\nwith {} sinisters".format(day_least_sinisters, num_least_sinisters),
            "{}\nwith {} sinisters".format(day_most_sinisters, num_most_sinisters),
            mean_prediction,
            x_time
        ]


# @dash_app.callback(Output('download-link', 'href'),
#               [Input("predicted-data", "children"),
#               Input("time-data", "children")])
# def update_href(prediction, x_time):
#     df_to_save = pd.DataFrame(prediction, columns=['predictedSinisters'], index=x_time)
#     relative_filename = '{}-download.xlsx'.format(datetime.datetime.now().isoformat()[0:10])
#     absolute_filename = os.path.join(os.getcwd(), relative_filename)
#     df_to_save.to_csv(absolute_filename)
#     return '/{}'.format(relative_filename)


# @dash_app.server.route('/downloads/<path:path>')
# def serve_static(path):
#     root_dir = os.getcwd()
#     return flask.send_from_directory(
#         os.path.join(root_dir, 'downloads'), path
#     )

# if __name__ == '__main__':
#     dash_app.run_server(debug=True)
