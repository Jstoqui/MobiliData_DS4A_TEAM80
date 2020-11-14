# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

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
# from utils import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server

mapbox_access_token =  'pk.eyJ1Ijoic2hlaWplciIsImEiOiJja2dnb3hnOG0wNXViMnpsaXVjcTBuZWRjIn0.GMG_9RrbQgCeIRToUf1YMA'
px.set_mapbox_access_token(mapbox_access_token)

meses = {1: 'Ene', 
                2: 'Feb', 
                3: 'Mar', 
                4: 'Abr',
                5: 'May',
                6: 'Jun',
                7: 'Jul',
                8: 'Ago',
                9: 'Sep',
                10: 'Oct',
                11: 'Nov',
                12: 'Dic'}

dias = {0: 'lun',
        1: 'mar',
        2: 'mie',
        3: 'jue',
        4: 'vie',
        5: 'sab',
        6: 'dom'}

df1 = pd.read_csv(
    r'siniestros_con_hipotesis.csv', 
    dtype={'CODIGO_CAUSA': str, 
           'CODIGO_CAUSA2': str, 
           'CODIGO_CAUSA3': str, 
           'CODIGO_CAUSA4': str}, index_col=False)

df2=df1.copy()

df2['Mes'].replace(meses, inplace=True)
df2['Dia'].replace(dias, inplace=True)
df2['Dia_mes']=pd.to_datetime(df2['FECHA']).dt.day


descripcion = df2.copy()
descripcion2 = pd.concat([
    descripcion['DESCRIPCION'],
    descripcion['DESCRIPCION2'],
    descripcion['DESCRIPCION3'],
    descripcion['DESCRIPCION4']
])

descripcion2 = descripcion2.reset_index()
p=pd.DataFrame(descripcion2.groupby('index')[0].value_counts().reset_index(name='count_rows'))
causas_top30 = list(p[0].value_counts().head(30).reset_index()['index'])

df3 = pd.read_csv(r'actor_vial.csv')
df3['CONDICION'] = df3['CONDICION'].str.capitalize()
df3['CONDICION'].replace('Peaton','Peatón', inplace=True)
df3['SEXO'] = df3['SEXO'].str.capitalize()
df3['SEXO'].replace('Sin informacion','Sin información', inplace=True)

df4 = pd.read_csv(r'vehiculo.csv')


xaxis = dict(
        tickmode = 'array',
        tickvals = df2['Mes'].unique(),
        ticktext = np.array(meses.values())
    )



layout1 = dict(boxmode = 'group',
               boxgap = 0.25,
               boxgroupgap = 0.25,
               height = 300,
               width = 600,
               paper_bgcolor = 'rgba(0,0,0,0)', 
               plot_bgcolor = 'rgba(0,0,0,0)',
               margin=dict(l=50, r=50, b=10, t=10, pad=10),
               legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

layout2 = dict(boxmode = 'group',
               boxgap = 0.25,
               boxgroupgap = 0.25,
               height = 220,
               width = 500,
               paper_bgcolor = 'rgba(0,0,0,0)', 
               plot_bgcolor = 'rgba(0,0,0,0)',
               margin=dict(l=50, r=50, b=0, t=0, pad=10)
)

layout3 = dict(height = 300,
               #width = 1500,
               title = dict(
                   text = "Time Series / Count of Road Incident by Day", 
                   xanchor='center', 
                   yanchor='top', 
                   y=0.9,
                   x=0.5),
               autosize=True,
               paper_bgcolor = 'rgba(0,0,0,0)', 
               plot_bgcolor = 'rgba(0,0,0,0)',
               margin = dict(l=50, r=50, b=50, t=50, pad=10),                                
               xaxis =  dict(visible = True, showgrid=True, gridcolor='rgb(150,150,150)'),
               yaxis = dict(visible = True, showgrid=True, gridcolor='rgb(150,150,150)',  rangemode = 'normal'),
)

mapa_layout = dict(mapbox_style="carto-positron",
                   width=600,
                   height=600,
                   autosize=False,
                   hovermode=False,
                   margin=dict(l=10, r=30, b=0, t=10, pad=10),
                   legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
                  )

localidades = [{'label': i, 'value': i} for i in df2['LOCALIDAD'].sort_values().unique()]
causas = [{'label': i, 'value': i} for i in causas_top30]

##################################################  Inicializar grafica 1    #########################################################

l = df2.groupby(['Hora','GRAVEDAD'])['CODIGO_SINIESTRO'].count().reset_index(name = 'Cantidad')

fig=px.bar(l, x='Hora', y='Cantidad',  color='GRAVEDAD')
fig.update_layout(layout1)

####################################################### inicializar  mapa ################################################################

fig2 = px.scatter_mapbox(df2[(
    df2['TOTAL_MUERTOS']>3) | (df2['TOTAL_HERIDOS']>5)],
    lat="lat", 
    lon="lon", 
    zoom=10,
    opacity=0, 
    color='GRAVEDAD')

fig2.update_layout(mapa_layout)

color_discrete_map={
                "Maculino": "magenta",
                "Femenino": "blue",
                "Sin información": "green"}

color_discrete_sequence=["MediumSpringGreen", "red", "CornflowerBlue", "goldenrod", "magenta", "Gold", "LightSeaGreen"]

################################################        Incicializar gráfica 2         ##################################################
zz = df3[df3['ESTADO']!='ILESO'].groupby(['CONDICION','SEXO'])['CODIGO_SINIESTRO'].count().reset_index(name='Cantidad')                                             

fig3=px.bar(zz, y="Cantidad", x="CONDICION",
             color='SEXO', barmode='stack', color_discrete_map= color_discrete_map)

   

#########################################################################################################################################

################################################        Incicializar gráfica 3         ##################################################
def serie_temporal2(data):    
    
    TS2 = data.copy()
    TS2['FECHA'] = pd.to_datetime(TS2['FECHA'])
    TS2 = TS2.sort_values(by=['FECHA'])
    ts_siniestros2 = pd.DataFrame(TS2.groupby('FECHA')['CODIGO_SINIESTRO'].count(
    ).reset_index(name='Cantidad_siniestros').set_index('FECHA'))
    
    return ts_siniestros2

fig4 = go.Figure([go.Scatter(x=serie_temporal2(df2).index, 
                        y=serie_temporal2(df2)['Cantidad_siniestros'])])


fig4.update_layout(layout3)
   

##########################################################################################################################################


def kpi_component(header, body, id_header, id_body, color):
    card_content = [
        dbc.CardHeader(header, id=id_header),
        dbc.CardBody(html.H2(children=body, id=id_body, className="card-title")),
    ]
    return dbc.Card(card_content, color=color, inverse=True)
    
    

dash_app.layout = dbc.Container(
    [
        html.Div([

            html.Div([

                dbc.Row([
                        dbc.Col([
                                html.Div([
                                    html.H2("Filter by"),
                                ], style={'marginBottom': 30, 'marginTop': 30, "color": "white", "text-align": "center"}),
                                html.Div([
                                    html.H3("Borough"),
                                    dcc.Dropdown(id="dropdown", options=localidades, multi=True, 
                                                 style={'marginBottom': 30, 'marginTop': 10, "color": "gray"})
                                ],  style={'marginBottom': 30, 'marginTop': 25, "color": "white"}),
                                html.Div([
                                    html.H3("Address"),
                                    dcc.Dropdown(id="dropdown2", options=[], multi=True, 
                                                 style={'marginBottom': 30, 'marginTop': 10, "color": "gray"})
                                ], style={'marginBottom': 30, 'marginTop': 25, "color": "white"}),
                                html.Div([
                                    html.H3("Hypothesis"),
                                    dcc.Dropdown(id="dropdown3", options=causas, multi=True, 
                                                 style={'marginBottom': 30, 'marginTop': 10, "color": "gray"})
                                ],  style={'marginBottom': 30, 'marginTop': 25, "color": "white"}),
                                html.Div([
                                    html.H3("Time"),                                    
                                    dbc.RadioItems(id='radio_items', options=[{'label': 'Month', 'value': 'Mes'},
                                                                              {'label': 'Day of the Week', 'value': 'Dia'},                                                                                               {'label': 'Day of the Month', 'value': 'Dia_mes'},
                                                                              {'label': 'Hour','value': 'Hora'}],
                                                   value='Hora')
                                                                
                                ],  style={'marginBottom': 30, 'marginTop': 25, "color": "white"}),
                                html.Div([
                                    html.H3("Classification"),                                    
                                    dbc.RadioItems(id='radio_items2', options=[{'label': 'Severity', 'value': 'GRAVEDAD'},
                                                                              {'label': 'Type','value': 'CLASE'},
                                                                              {'label': 'Hour','value': 'Hora'}], 
                                                   value='GRAVEDAD',
                                                                              style={"display":"inline-block"})
                                                                
                                ],  style={'marginBottom': 30, 'marginTop': 25, "color": "white"}),
                                html.Div([
                                    html.H3("Time range"),                                    
                                  dcc.RangeSlider(id='fecha', marks= {
                                      i: {'label':str(i), 'style': {'color': 'white'}} 
                                      for i in range(df2['ANO'].min(), df2['ANO'].max()+2)},
                                                  min=df2['ANO'].min(), 
                                                  max=df2['ANO'].max()+1, 
                                                  value=[df2['ANO'].min(), df2['ANO'].max()+1],
                                                  pushable=1)      

                                ],  style={'marginBottom': 30, 'marginTop': 25, "color": "white"}),
                             ],
                            width={"size":2},
                            style={"background-color":"#0d47a1"}
                        ),
                        dbc.Col([
 ########################################## ********** CARDS KPI **********#######################################################

                            dbc.Row([
                                dbc.Col(
                                    kpi_component(
                                        header="Siniestros:",
                                        body='???',
                                        id_header="header3",
                                        id_body="cantidad_siniestros",
                                        color="primary")
                                ),
                                dbc.Col(
                                    kpi_component(
                                        header="Fallecidos: ",
                                        body='???',
                                        id_header="header2",
                                        id_body="cantidad_fallecidos",
                                        color="danger")
                                ),
                                dbc.Col(
                                    kpi_component(
                                        header="Heridos: ",
                                        body='???',
                                        id_header="header-volume3",
                                        id_body="cantidad_heridos",
                                        color="warning")
                                ),
                                dbc.Col(
                                    kpi_component(
                                        header="Vehículos: ",
                                        body='???',
                                        id_header="header",
                                        id_body="cantidad_vehiculos",
                                        color="info")
                                ),
                            ], style={'marginBottom': 50, 'marginTop': 25}),
                            dbc.Row([
                                dbc.Col(
                                    html.Div(
                                        dcc.Graph(id="mapa", figure=fig2, style={"height": "100%"}), style={"height": "100%"},
                                    ), width =6,
                                ),
                                dbc.Col([
                                    html.Div(dcc.Graph(id="grafico", figure=fig)),
                                    html.Div(dcc.Graph(id="grafico2", figure=fig3)),
                                ]),
                            ]),
                           html.Div([
                                 dbc.Row(dbc.Col(
                                    html.Div(dcc.Graph(id="serie", figure=fig4)),width=12
                                 )),
                             ]),

                        ]
                    )
                ]),

            ])
        ])
    ],
    fluid=True
)


################################################   actualizar gráfico 2    ##############################################################

@dash_app.callback(
    Output('grafico2', 'figure'),
    [Input('fecha', 'value')],
    [Input('radio_items', 'value')],
    [Input('dropdown', 'value')],
    [Input('dropdown2', 'value')],
    [Input('dropdown3', 'value'),])
def update_grafico2(fecha_value, 
                    radio_items_value, 
                    dropdown_value, 
                    dropdown_value2, 
                    dropdown_value3):
    
    victimas = df3[df3['ESTADO']!='ILESO'].copy()
     
    if (dropdown_value3 != None) & (dropdown_value3 != []):
        df_con_hipotesis = df2[(df2['DESCRIPCION'].isin(dropdown_value3)) |
                              (df2['DESCRIPCION2'].isin(dropdown_value3)) |
                              (df2['DESCRIPCION3'].isin(dropdown_value3)) |
                               (df2['DESCRIPCION4'].isin(dropdown_value3))].copy()
    else:
        df_con_hipotesis=df2.copy()
    
    df_con_hipotesis= df_con_hipotesis[
        (df_con_hipotesis['ANO']>=fecha_value[0]) & (df_con_hipotesis['ANO']<=fecha_value[1])]
    
    
    xaxis={'title': "Heridos y fallecidos"}
    
    if (dropdown_value == None) | (dropdown_value == []):
        
        z = victimas[victimas['CODIGO_SINIESTRO'].isin(
            df_con_hipotesis['CODIGO_SINIESTRO'])].groupby(
            ['CONDICION','SEXO'])['CODIGO_SINIESTRO'].count().reset_index(name='Cantidad')                                             

        try: 
            fig=px.bar(z, y="Cantidad", x="CONDICION",
                 color='SEXO', barmode='stack', color_discrete_map=color_discrete_map)
        except:
            fig=px.bar(z, y="Cantidad", x="CONDICION",
                  barmode='stack', color_discrete_map=color_discrete_map)
                        
    
    else:

        if dropdown_value2 == []:
        
            l = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)]['CODIGO_SINIESTRO']
            grupo = victimas[victimas['CODIGO_SINIESTRO'].isin(l)]
            z = grupo.groupby(['CONDICION','SEXO'])['CODIGO_SINIESTRO'].count().reset_index(name='Cantidad')                                             

            try: 
                fig=px.bar(z, y="Cantidad", x="CONDICION",
                 color='SEXO', barmode='stack', color_discrete_map=color_discrete_map)
            except:
                fig=px.bar(z, y="Cantidad", x="CONDICION",
                  barmode='stack', color_discrete_map=color_discrete_map)
                                    
        else:
           
            l = df_con_hipotesis[(
                df_con_hipotesis['LOCALIDAD'].isin(
                    dropdown_value)) & (df_con_hipotesis['DIRECCION'].isin(dropdown_value2))]['CODIGO_SINIESTRO']
            grupo = victimas[victimas['CODIGO_SINIESTRO'].isin(l)]
            
            
            z = grupo.groupby(['CONDICION','SEXO'])['CODIGO_SINIESTRO'].count().reset_index(name='Cantidad')                                             
            try: 
                fig=px.bar(z, y="Cantidad", x="CONDICION",
                 color='SEXO', barmode='stack', color_discrete_map=color_discrete_map)
            except:
                fig=px.bar(z, y="Cantidad", x="CONDICION",
                  barmode='stack', color_discrete_map=color_discrete_map)
                        
            

    fig.update_layout(layout1, xaxis=xaxis)  
     
    
    return  fig



########################################################          dropdown2           #################################################



@dash_app.callback(
    Output('dropdown2', 'options'),
    Output('dropdown2', 'value'),
    [Input('dropdown', 'value'),])
def update_dropdown2(dropdown_value):
    if (dropdown_value == None) | (dropdown_value == []):
        direccion = []
    elif (len(dropdown_value)==1):
        direccion = [{'label': i, 'value': i} for i in df2[
            df2['LOCALIDAD'].isin(dropdown_value)]['DIRECCION'].value_counts(
        ).sort_values(ascending=False).head(40).reset_index()['index']]
    else:
        direccion = []
    return direccion, []



################################################   actualizar gráfico 1    ##############################################################




@dash_app.callback(
    Output('grafico', 'figure'),
    Output('cantidad_siniestros', 'children'),
    Output('cantidad_fallecidos', 'children'),
    Output('cantidad_heridos', 'children'),
    Output('cantidad_vehiculos', 'children'),  
    [Input('fecha', 'value')],
    [Input('radio_items', 'value')],
    [Input('radio_items2', 'value')],
    [Input('dropdown', 'value')],
    [Input('dropdown2', 'value'),],
    [Input('dropdown3', 'value'),])
def update_grafico(fecha_value, 
                   radio_items_value, 
                   radio_items_value2, 
                   dropdown_value, 
                   dropdown_value2, 
                   dropdown_value3):
    
    if radio_items_value2 == 'Hora':
        radio_items_value2 = 'GRAVEDAD'
        
    if (dropdown_value3 != None) & (dropdown_value3 != []):
        df_con_hipotesis = df2[(df2['DESCRIPCION'].isin(dropdown_value3)) |
                               (df2['DESCRIPCION2'].isin(dropdown_value3)) |
                               (df2['DESCRIPCION3'].isin(dropdown_value3)) |
                               (df2['DESCRIPCION4'].isin(dropdown_value3))].copy()
    else:
        df_con_hipotesis=df2.copy()
    
    df_con_hipotesis= df_con_hipotesis[
        (df_con_hipotesis['ANO']>=fecha_value[0]) & (df_con_hipotesis['ANO']<fecha_value[1])]
    
    yaxis={'title': "Cantidad de siniestos"}
    
    if (radio_items_value == 'Mes'):
        xaxis={'categoryorder':'array', 'categoryarray':list(meses.values()), 'title': "Meses"}
    elif  (radio_items_value == 'Dia'):
        xaxis={'categoryorder':'array', 'categoryarray':list(dias.values()), 'title': "Dias"}
    else:
        xaxis={'title': "Horas"}
        
    if (dropdown_value == None) | (dropdown_value == []):
        
        l = df_con_hipotesis.groupby([radio_items_value,radio_items_value2])['CODIGO_SINIESTRO'].count().reset_index(name = 'Cantidad')
        
        fig = px.bar(l, x=radio_items_value, y='Cantidad', color=radio_items_value2, 
                     color_discrete_sequence=color_discrete_sequence)
        
        siniestros = len(df_con_hipotesis)
        fallecidos = df_con_hipotesis['TOTAL_MUERTOS'].sum()
        heridos = df_con_hipotesis['TOTAL_HERIDOS'].sum()
        vehiculos = len(df4[df4['CODIGO_SINIESTRO'].isin(df_con_hipotesis['CODIGO_SINIESTRO'])]['SERVICIO'].dropna())            
    
    else:
        if dropdown_value2 == []:
        
            l = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)].groupby(
                [radio_items_value,radio_items_value2])['CODIGO_SINIESTRO'].count().reset_index(name = 'Cantidad')
            
            fig = px.bar(l, x=radio_items_value, y='Cantidad', color=radio_items_value2, 
                         color_discrete_sequence=color_discrete_sequence)
            
            siniestros = len(df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)])
            fallecidos = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)]['TOTAL_MUERTOS'].sum()
            heridos = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)]['TOTAL_HERIDOS'].sum()
            l2 = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)]
            vehiculos = len(df4[df4['CODIGO_SINIESTRO'].isin(l2['CODIGO_SINIESTRO'])]['SERVICIO'].dropna())
            
        else:           
            l = df_con_hipotesis[(df_con_hipotesis['LOCALIDAD'].isin(
                dropdown_value)) & (df_con_hipotesis['DIRECCION'].isin(dropdown_value2))].groupby(
                [radio_items_value,radio_items_value2])['CODIGO_SINIESTRO'].count().reset_index(name = 'Cantidad')
            
            fig = px.bar(l, x=radio_items_value, y='Cantidad', color=radio_items_value2, 
                         color_discrete_sequence=color_discrete_sequence)
            
            siniestros = len(df_con_hipotesis[(df_con_hipotesis['LOCALIDAD'].isin(
                dropdown_value)) & (df2['DIRECCION'].isin(dropdown_value2))])
            fallecidos = df_con_hipotesis[(df_con_hipotesis['LOCALIDAD'].isin(
                dropdown_value)) & (df_con_hipotesis['DIRECCION'].isin(dropdown_value2))]['TOTAL_MUERTOS'].sum()
            heridos = df_con_hipotesis[(df_con_hipotesis['LOCALIDAD'].isin(
                dropdown_value)) & (df_con_hipotesis['DIRECCION'].isin(dropdown_value2))]['TOTAL_HERIDOS'].sum()
            l2 = df_con_hipotesis[(df_con_hipotesis['LOCALIDAD'].isin(
                dropdown_value)) & (df_con_hipotesis['DIRECCION'].isin(dropdown_value2))]
            vehiculos = len(df4[df4['CODIGO_SINIESTRO'].isin(l2['CODIGO_SINIESTRO'])]['SERVICIO'].dropna())
            

    fig.update_layout(layout1, xaxis=xaxis, yaxis=yaxis)   
     
    
    return  fig, "{:,.0f}".format(siniestros), "{:,.0f}".format(fallecidos), "{:,.0f}".format(heridos), "{:,.0f}".format(vehiculos)


##########################################################################################################################################

#################################################      actualizar mapa         ##########################################################


@dash_app.callback(
    Output('mapa', 'figure'),
    [Input('fecha', 'value')],
    [Input('radio_items2', 'value')],
    [Input('radio_items', 'value')],
    [Input('dropdown', 'value')],
    [Input('dropdown2', 'value')],
    [Input('dropdown3', 'value'),])
def update_mapa(fecha_value, 
                radio_items_value2, 
                radio_items_value, 
                dropdown_value, 
                dropdown_value2, 
                dropdown_value3):
     
    if (dropdown_value3 != None) & (dropdown_value3 != []):
        df_con_hipotesis = df2[(df2['DESCRIPCION'].isin(dropdown_value3)) |
                              (df2['DESCRIPCION2'].isin(dropdown_value3)) |
                              (df2['DESCRIPCION3'].isin(dropdown_value3)) |
                               (df2['DESCRIPCION4'].isin(dropdown_value3))].copy()
    else:
        df_con_hipotesis=df2.copy()
   
    zoom=10
    df_con_hipotesis= df_con_hipotesis[
        (df_con_hipotesis['ANO']>=fecha_value[0]) & (df_con_hipotesis['ANO']<=fecha_value[1])]
    
    hover_name = "CODIGO_SINIESTRO"    
    if (dropdown_value == None) | (dropdown_value == []):
        
        fig = px.scatter_mapbox(df_con_hipotesis,
            lat="lat", 
            lon="lon",
            color=radio_items_value2,
            opacity=0,                    
            zoom=10)
    else:
        hover_name = "CODIGO_SINIESTRO"
        if dropdown_value2 == []:
        
            l = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)].copy()
            hover_name = "CODIGO_SINIESTRO"
            
            if (len(dropdown_value)==1):
                zoom=12
            else:
                zoom=10
            fig = px.scatter_mapbox(l,
                lat="lat", 
                lon="lon",
                hover_name = hover_name,                  
                color=radio_items_value2,
                zoom=zoom)
            
        else:

            hover_name = "DIRECCION"

            if (len(dropdown_value2)==1):
                zoom=14
            else:
                zoom=12
            
            l = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(
                dropdown_value) & (df_con_hipotesis['DIRECCION'].isin(
                dropdown_value2))].copy()
            
            try:
                fig = px.scatter_mapbox(l,
                  lat="lat", 
                  lon="lon",
                  hover_name="CODIGO_SINIESTRO",                  
                  color=radio_items_value2,
                  zoom=zoom) 
             
            except:
                fig = px.scatter_mapbox(l,
                  lat="lat", 
                  lon="lon",
                  hover_name="CODIGO_SINIESTRO",                  
                  zoom=zoom) 
                             
    fig.update_layout(mapa_layout) 
    
    return fig

###############################################       actualizar gráfico 2     #########################################################

@dash_app.callback(
    Output('serie', 'figure'),    
    [Input('dropdown', 'value')],
    [Input('dropdown3', 'value'),])
def update_grafico3(dropdown_value, dropdown_value2):
    
    if (dropdown_value2 != None) & (dropdown_value2 != []):
        df_con_hipotesis = df2[(df2['DESCRIPCION'].isin(dropdown_value2)) |
                               (df2['DESCRIPCION2'].isin(dropdown_value2)) |
                               (df2['DESCRIPCION3'].isin(dropdown_value2))|
                               (df2['DESCRIPCION4'].isin(dropdown_value2))].copy()
    else:
        df_con_hipotesis=df2.copy()
        
    if (dropdown_value != None) & (dropdown_value != []):
        df_con_hipotesis = df_con_hipotesis[df_con_hipotesis['LOCALIDAD'].isin(dropdown_value)]
        
    
    fig=go.Figure([go.Scatter(x=serie_temporal2(df_con_hipotesis).index, 
                        y=serie_temporal2(df_con_hipotesis)['Cantidad_siniestros'])])
    fig.update_layout(layout3)   
    
    return  fig




if __name__ == '__main__':
    dash_app.run_server(debug=True)

