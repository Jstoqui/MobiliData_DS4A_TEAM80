import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import os
import pandas as pd
import numpy as np

import google.auth
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import bigquery


from app import app
from apps import  Siniestros, Volumes, Model, Home, Speed

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href="apps/Home"),
        dbc.DropdownMenuItem("Travel Speed ", href="/apps/Speed"),
        dbc.DropdownMenuItem("Traffic incidents", href="/apps/Siniestros"),
        dbc.DropdownMenuItem("Traffic Volumes", href="/apps/Volumes"),
        dbc.DropdownMenuItem("Prediction Model", href="/apps/Model"),        
    ],
    nav = True,
    in_navbar = True,
    label = "Explore",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="/assets/img/MobilidataS2.png", height="40px")),                        
                        dbc.Col(html.Img(src="/assets/img/Correlation.png", height="70px")),
                        #dbc.Col(dbc.NavbarBrand(" App movilidad Bogotá", className="ml-3")),
                        dbc.Col(dbc.NavbarBrand("Bogotá MobiliData App 1.0 ", className="ml-3")),
                        #dbc.Col(html.Img(src="/assets/img/MobilidataS2.png", height="40px")),
                        
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/Home",
            ),
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    # right align dropdown menu with ml-auto className
                    [dropdown], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
    #sticky='top'
    fixed='top'
)

def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

for i in [2]:
    app.callback(
        Output(f"navbar-collapse{i}", "is_open"),
        [Input(f"navbar-toggler{i}", "n_clicks")],
        [State(f"navbar-collapse{i}", "is_open")],
    )(toggle_navbar_collapse)


app.layout = html.Div([
    #html.Link(href="/assets/img/favicon.png",rel="shortcut icon"),
    #html.H1('Super App movilidad Secretaria'),
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content'),
    html.Footer(id="footer",children=[
        html.Div(className="container",children=[   
            html.Div(className='copyright',children=[
                html.P(["Copyright ",html.Strong('MobiliData',"All Rights Reserved")])
             ])
        ])
    ])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    #pathname = '/apps/app2'
    if pathname == '/apps/Speed':
        return Speed.layout
    elif pathname == '/apps/Siniestros':
        return Siniestros.layout
    elif pathname == '/apps/Volumes':
        return Volumes.layout
    elif pathname == '/apps/Model':
        return Model.layout                
    else:
        #return '404'
        return Home.layout

#if __name__ == '__main__':
#    app.run_server(debug=True)

#Initiate the server where the app will work
if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port='8080',debug=False)