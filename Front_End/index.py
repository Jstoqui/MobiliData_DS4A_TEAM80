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

from app import app
from apps import app1, app2, app3, app4, home

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home", href="apps/home"),
        dbc.DropdownMenuItem("Velocidades", href="/apps/app1"),
        dbc.DropdownMenuItem("Siniestralidad", href="/apps/app2"),
        dbc.DropdownMenuItem("Volumenes", href="/apps/app3"),
        dbc.DropdownMenuItem("Modelo", href="/apps/app4"),        
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
                        dbc.Col(html.Img(src="/assets/img/Correlation.png", height="70px")),
                        #dbc.Col(dbc.NavbarBrand(" App movilidad Bogotá", className="ml-3")),
                        dbc.Col(dbc.NavbarBrand("Bogotá Mobility Data App 1.0 ", className="ml-3")),
                        dbc.Col(html.Img(src="/assets/img/MobilidataS2.png", height="25px")),
                        
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/home",
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
    #fixed='top'
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
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    #pathname = '/apps/app2'
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    elif pathname == '/apps/app3':
        return app3.layout
    elif pathname == '/apps/app4':
        return app4.layout                
    else:
        #return '404'
        return home.layout

#if __name__ == '__main__':
#    app.run_server(debug=True)

#Initiate the server where the app will work
if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port='8050',debug=True)