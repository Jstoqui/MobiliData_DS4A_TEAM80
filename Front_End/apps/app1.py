import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H4('Bienvenido al DashBoard de Velocidades', className="section-header"),
    dcc.Dropdown(
        id='app-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'Corredor 1', 'Corredor 2', 'Corredor 3'
            ]
        ]
    ),
    html.P(''),   
    html.Div(id='app-1-display-value', className="intro-info"),
    html.P(''),  
    dcc.Link('Go to App 2', href='/apps/app2')
#    dcc.Link('Go to App 2', href='/app2')
])


@app.callback(
    Output('app-1-display-value', 'children'),
    [Input('app-1-dropdown', 'value')])

def display_value(value):
    return 'Velocidades para "{}"'.format(value)