import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

#Create Layout
layout = html.Div([
    html.H1('Bienvenido al Dashboard de Volumenes'),
    dcc.RadioItems(
        id='app2-radios',
        options=[{'label': i, 'value': i} for i in ['Bicicletas', 'Caminones', 'Aviones']],
        value='Aviones'
    ),
    html.Div(id='app3-content'),
    html.Br(),
    dcc.Link('Speed Dashborad', href='/apps/app1'),
    html.Br(),
    dcc.Link('Go back to home', href='/apps/home')
])