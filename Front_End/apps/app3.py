import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
# from google.cloud import storage
# from google.cloud import bigquery
import os
import pandas as pd
import numpy as np
import datetime
import math
# from decouple import config
from utils import *
from app import app

tipologies = ["LIVIANOS", "INTERMUNICIPALES", "BUSES", "MOTOS", "BICICLETAS CALZADA", "C2 C3", ">=C4"]
#mapbox_token = config("MAP_BOX_TOKEN", "hola")
mapbox_token = 'pk.eyJ1Ijoic2hlaWplciIsImEiOiJja2dnb3hnOG0wNXViMnpsaXVjcTBuZWRjIn0.GMG_9RrbQgCeIRToUf1YMA'

file_key_mon = "base_volumenes_monitoreo.xlsx"

# LECTURA DEL ARCHIVO
df_volumes_monitoring = pd.read_excel(file_key_mon, sheet_name=0) # MONITOREO DE LAS PERSONAS
df_volumes_sensors = pd.read_excel(file_key_mon, sheet_name=1)# INFORMACION DE LOS SENSORES


# LATITUDE AND LONGITUDE
all_locations = df_volumes_monitoring["DIRECCION CATASTRO"].unique().tolist()
all_locations_options = [{"label": direccion, "value": direccion} for direccion in all_locations]

all_lat_lon = ["4.694410;-74.168855", "4.696095;-74.172643", "4.695489;-74.170179"]
all_locations_coordinates = dict(zip(all_locations, all_lat_lon))

# CAR TIPOLOGIES
tipology_options = [{"label": tipo, "value": tipo} for tipo in tipologies]
all_registered_dates_monitoring = df_volumes_monitoring["FECHA"].astype(str).unique()
all_hours_raw = df_volumes_monitoring["PERIODO"].astype(str).unique()
all_hours_rounded = get_round_hours(all_hours_raw)
all_hours = [fix_hours(i) for i in all_hours_rounded]

df_volumes_monitoring["TOTAL VOLUME"] = df_volumes_monitoring[tipologies].sum(axis=1)
fecha_options = [{"label": fecha, "value": fecha} for fecha in all_registered_dates_monitoring]

# HORA OPTIONS
range_slider_marks = {i: '{}'.format(hour) for i,hour in enumerate(all_hours_rounded)}
min_hour_index = 0
max_hour_index = len(all_hours_rounded)-1

# Plots de los volumenes de todas las fechas por topologia
fig_monitoring = multiLine(df_volumes_monitoring, tipologies[0], all_locations[0], (all_hours_rounded[min_hour_index], all_hours_rounded[max_hour_index]) )
# Stacked area plot de los volumenes de todas las tipologías para una fecha
fig_stacked = staked_plot_by_topology_plotly(df_volumes_monitoring, all_registered_dates_monitoring[0], all_locations[0], (all_hours_rounded[min_hour_index], all_hours_rounded[max_hour_index]) )
# Stacked area plot de las reas de todas las tipologias
fig_stacked_car_area = staked_plot_by_topology_area_plotly(df_volumes_monitoring, all_registered_dates_monitoring[0], all_locations[0], (all_hours_rounded[min_hour_index], all_hours_rounded[max_hour_index]))

# DESCRIPTION TEXT
tipologies_description_dict = {
    ">=C4": "Correspond to trucks, dump trucks with four or more axles.",
    "C2 C3": "Correspond to small and median freight vehicles with two or three axles.",
    "BICICLETAS CALZADA": "Non-motorized 2-wheel vehicles or assisted by a motor.",
    "MOTOS": "Motorized 2-wheel vehicles.",
    "BUSES": "City transport (SITP and SITP Provisional) and School Buses.",
    "INTERMUNICIPALES": "Vehicles that transport people through regional roadways.",
    "LIVIANOS": "Correspond to Sedans, Wagons, Vans."
}
# COMPONENTE PARA LA DESCRIPCIÓN CONSTRUIDO CON LI DE HTML
description_topologies = [html.Li("{}: {}".format(item[0], item[1])) for item in tipologies_description_dict.items()]

# KPI VALUES
mean_volume = "{:.2f}".format(df_volumes_monitoring[tipologies[0]].mean())

# HOUR WITH GREATER VOLUME AM AND PM
init_am, init_pm = 500, 1200
final_am, final_pm = 1200, 2300

max_volume_hour_am = get_hour_with_max_volume(df_volumes_monitoring, all_registered_dates_monitoring[0], init_am, final_am)
max_volume_hour_pm = get_hour_with_max_volume(df_volumes_monitoring, all_registered_dates_monitoring[0], init_pm, final_pm)


# MAP
ubicacion = "Bogotá D.C. Map"# HARDCODED
first_location = all_locations[0]
lat, lon = get_lat_long(first_location, all_locations_coordinates)

all_lat_lon = get_all_lat_long(all_lat_lon)
mapa2 = go.Scattermapbox(
    lat=all_lat_lon[0],
    lon=all_lat_lon[1],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=30,
        color="MediumPurple"
    ),
    text=all_locations,
)

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#app = dash_app.server

#****************************************************************************

layout = dbc.Container(style={'background-image':'url(/assets/img/fondo4.png)'},fluid=True, children=[
        html.Div(style={'height':"90px"}),        
        html.Div([
            html.Div([
                # ROW PRINCIPAL
                dbc.Row([

                        # COLUMNA IZQUIERDA
                        dbc.Col([
                                html.Div(className="icon-box wow fadeInUp",children=[
                                    html.H2("Filter by"),
                                ], style={'marginBottom': 50, 'marginTop': 30, "color": "white", "text-align": "center"}),
                                html.Div(className="icon-box wow fadeInUp",children=[
                                    html.H3("Vehicle Topology", style={"color": "white"}),
                                    dcc.Dropdown(id="tipology-picker", options=tipology_options, value=min(tipologies))
                                ],  style={'marginBottom': 50, 'marginTop': 25}),
                                html.Div(className="icon-box wow fadeInUp",children=[
                                    html.H3("Address", style={"color": "white"}),
                                    dcc.Dropdown(id="direccion-picker", options=all_locations_options, value=min(all_locations))
                                ], style={'marginBottom': 50, 'marginTop': 25}),
                                html.Div(className="icon-box wow fadeInUp",children=[
                                    html.H3("Date", style={"color": "white"}),
                                    dcc.Dropdown(id="fecha-picker", options=fecha_options, value=min(all_registered_dates_monitoring))
                                ], style={'marginBottom': 50, 'marginTop': 25})
                            ],
                            width={"size":2},
                            style={"background-color": "#42456f"}
                        ),
                        # COLUMNA DERECHA
                        dbc.Col([
                            html.Header(className="section-header", children=[
                                html.H3('Explore the Traffic Volumes in especifics points of Bogotá '),
                            ]),
                            # ********** CARDS KPI ROW **********
                            dbc.Row([
                                dbc.Col(
                                    kpi_component(
                                        header="Average Volume",
                                        body=mean_volume,
                                        id_header="header-volume",
                                        id_body="mean-volume",
                                        color="primary")
                                ),
                                dbc.Col(
                                    kpi_component(
                                        header="Peak volume hour in AM period",
                                        body=max_volume_hour_am,
                                        id_header="header-volume2",
                                        id_body="hour-greater-vol-am",
                                        color="secondary")
                                ),
                                dbc.Col(
                                    kpi_component(
                                        header="Peak volume hour in PM period",
                                        body=max_volume_hour_pm,
                                        id_header="header-volume3",
                                        id_body="hour-greater-vol-pm",
                                        color="info")
                                ),
                                dbc.Col(
                                    kpi_component(
                                        header="Volumen Promedio: {}".format(min(tipologies)),
                                        body=mean_volume,
                                        id_header="header-volume4",
                                        id_body="mean-volume4",
                                        color="danger")
                                ),
                            ], style={'marginBottom': 50, 'marginTop':0}),
                            # ********** ROW DEL SLIDER DE HORA *********
                            html.Div([
                                html.Header(className="section-header", children=[
                                html.H3('Move bar to filter the hour of the day between 5:00 to 22:00'),
                                ]),
                            ]),
                            dbc.Row([
                                # *********** SLIDER DE HORA **********
                                dbc.Col(
                                    html.Div(
                                        dcc.RangeSlider(
                                            id="hour-slider",
                                            marks=range_slider_marks,
                                            min=min_hour_index,
                                            max=max_hour_index,
                                            value=[min_hour_index, max_hour_index]
                                        ), style={'marginBottom': 25, 'marginTop': 25})
                                )
                            ]),
                            # ************ ROW DE LOS PLOT Y EL mapa2 **********
                            dbc.Row([
                                # COLUMNA DEL mapa2 (IZQUIERDA)
                                dbc.Col(
                                    html.Div(
                                        dcc.Graph(className="icon-box wow fadeInUp",id="mapa2", figure=bogota_map(mapa2, lat, lon, mapbox_token), style={"height": "100%"}), style={"height": "100%", "border":"2px #6c757d solid", "border-radius": "4px"}
                                    )
                                ),
                                # COLUMNA DE LOS PLOTS (DERECHA)
                                dbc.Col([
                                    html.Div(dcc.Graph(className="icon-box wow fadeInUp",id="monitoreo-bar", figure=fig_stacked), style={"border":"2px #6c757d solid", "border-radius": "4px"}),
                                    html.Div(dcc.Graph(className="icon-box wow fadeInUp", id="monitoreo-area", figure=fig_stacked_car_area), style={'marginTop': 25, "border":"2px #6c757d solid", "border-radius": "4px"}),
                                    html.Div(dcc.Graph(className="icon-box wow fadeInUp",id="monitoreo-time", figure=fig_monitoring), style={'marginTop': 25, "border":"2px #6c757d solid", "border-radius": "4px"}),
                                ]),
                            ]),

                            # CARD PARA LAS DESCRIPCIONES
                            html.Div(style={'height':"30px"}),                            
                            html.Div(style={'marginTop': 0, "marginBottom": 25},children=[
                                dbc.Card(className="icon-box wow fadeInUp", color="info", inverse=True,children=[
                                    dbc.CardHeader("Vehicular topologies description"),
                                    dbc.CardBody([
                                        html.P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam sapien ante, laoreet quis magna vitae, lacinia dignissim neque. Donec ultricies.", className="card-text"),
                                        html.Ul(description_topologies)
                                    ])
                                ])
                            ])                                
                        ])
                ]),

            ])
        ])
    ]
)


# ************** CALLBACKS ****************************************

# DROPDOWN LA TIPOLOGIA DE VEHÍCULO
@app.callback(
    Output("monitoreo-time", "figure"), 
    [Input("tipology-picker", "value"), Input("direccion-picker", "value"), Input("hour-slider", "value")])
def update_figure_monitoring(tipology, direccion, hora):
    return multiLine(df_volumes_monitoring, tipology, direccion, (all_hours_rounded[hora[0]], all_hours_rounded[hora[1]] ))

# SLIDER DE LAS HORAS
@app.callback(
    [Output("monitoreo-bar", "figure"), Output("monitoreo-area", "figure")],
    [Input("fecha-picker", "value"), Input("direccion-picker", "value"), Input("hour-slider", "value")])
def update_figure_monitoring_stacked_plot(fecha, direccion, hora_ind):
    return staked_plot_by_topology_plotly(df_volumes_monitoring, fecha, direccion, (all_hours_rounded[hora_ind[0]], all_hours_rounded[hora_ind[1]])), staked_plot_by_topology_area_plotly(df_volumes_monitoring, fecha, direccion, (all_hours_rounded[hora_ind[0]], all_hours_rounded[hora_ind[1]]))

# DROPDOWN DE LAS FECHAS
@app.callback([Output("fecha-picker", "options"), Output("fecha-picker", "value")], Input("direccion-picker", "value"))
def update_dropdown_fechas(direccion):
    date_list = df_volumes_monitoring[df_volumes_monitoring["DIRECCION CATASTRO"] == direccion]["FECHA"].astype(str).unique()
    return [ [{"label": date, "value": date} for date in date_list], min(date_list)]

# CARDS DE KPI (PRIMERO)
@app.callback(
    [Output("mean-volume", "children"), Output("header-volume", "children")],
    [Input("tipology-picker", "value"), Input("direccion-picker", "value"), Input("fecha-picker", "value"), Input("hour-slider", "value")])
def update_kpi_volume(tipology, direccion, fecha, hora):
    promedio = df_volumes_monitoring[(df_volumes_monitoring["DIRECCION CATASTRO"] == direccion) & (df_volumes_monitoring["FECHA"] == fecha)][tipology].mean()
    # REVISE QUE NO SEA NULO
    if math.isnan(promedio):
        promedio_string = "No existen datos para calcularlo"
    else:    
        promedio_string = "{:.2f}".format(promedio)
    return [promedio_string, "Average Volume"]


# CARDS KPI HOUR WITH GREATER VOLUME
@app.callback([Output("hour-greater-vol-am", "children"), Output("hour-greater-vol-pm", "children")], Input("fecha-picker", "value"))
def update_kpi_max_volume_hour(fecha):
    return get_hour_with_max_volume(df_volumes_monitoring, fecha, 500, 1200), get_hour_with_max_volume(df_volumes_monitoring, fecha, 1200, 2300)


# CENTRADO DEL mapa2
@app.callback(Output("mapa2", "figure"), Input("direccion-picker", "value"))
def update_map_coordinates(direccion):
    lat, lon = get_lat_long(direccion, all_locations_coordinates)
    
    mapa2 = go.Scattermapbox(
        lat=all_lat_lon[0],
        lon=all_lat_lon[1],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=30,
            color="MediumPurple"
        ),
        text=all_locations,
    )
    return bogota_map(mapa2, lat, lon, mapbox_token)


# ******************** ******************** ********************


#if __name__ == '__main__':
#    dash_app.run_server(host='0.0.0.0',port='8050',debug=True)
