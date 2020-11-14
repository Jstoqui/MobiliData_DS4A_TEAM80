import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

import google.auth
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import bigquery



credencial= service_account.Credentials.from_service_account_file(
    'key.json',
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# Construct a BigQuery client object.
client2 = bigquery.Client(
    credentials= credencial,
    project=credencial.project_id,
)

#Get bitcarrier_weekday from Big Query
query_mainroad = '''
SELECT tid, Corredor, complete_name, date, weekday, hour, speed, count, distance, Sentido 
FROM `ds4a-v3-team80.MOVILIDAD.BITCARRIER`
'''

df_bitcarrier_mainroad_weekday = client2.query(query_mainroad).to_dataframe()



#Create Layout
layout = html.Div([
    html.H1('Bienvenido al Dashboard del Modelo'),
    dcc.RadioItems(
        id='app2-radios',
        options=[{'label': i, 'value': i} for i in ['Prediccion', 'Regres', 'Loga']],
        value='Loga'
    ),
    html.Div(id='app4-content'),
    html.Br(),
    dcc.Link('Speed Dashborad', href='/apps/app1'),
    html.Br(),
    dcc.Link('Go back to home', href='/apps/home')
])