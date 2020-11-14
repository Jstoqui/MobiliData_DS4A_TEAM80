import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString
import pandas as pd


from plotly.offline import iplot
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import shapely.geometry

#from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash
import dash_bootstrap_components as dbc
import dash_table

import google.auth
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import bigquery




#Llave movilidad
#llave_movilidad = pd.read_excel('/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/TramosCGT-REV.dbf - original.xlsx')
llave_movilidad = pd.read_excel('tramos.xlsx')


#----Traigo el query completo desde Big Query-------
#'''
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/Dash/secretaria-movilidad-d7884405beb2.json'

#client = bigquery.Client(project='secretaria-movilidad')
#'''

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


#Get weekday_grouped_sum from Big Query
query_weekday="""
SELECT *
FROM `ds4a-v3-team80.MOVILIDAD.WEEKDAY`
"""
weekday_grouped_sum = client2.query(query_weekday).to_dataframe()
 
weekday_grouped_sum.columns=['Corredor_x', 'tid', 'complete_name_x','date', 'Sentido','count_y', 'speed_ponderada' ]
weekday_grouped_sum =weekday_grouped_sum.groupby(['Corredor_x', 'tid', 'complete_name_x', 'date', 'Sentido', 'count_y'])['speed_ponderada'].agg('sum').reset_index()


#Agrupar la suma de 'count' por cada periodo agrupado. En este ejemplo es el día calendario.
weekday_grouped_count = df_bitcarrier_mainroad_weekday.groupby(['Corredor', 'tid', 'complete_name','date', 'Sentido'])['count'].agg('sum').reset_index()


#***********************Velocidad ponderada de cada tramo para el periodo evaluado *********************************
#Agrupar la suma de 'count' por cada tid en el periodo agrupado.
#weekday_grouped_count_tid_periodo = weekday_grouped_count.groupby(['Corredor','tid', 'complete_name', 'Sentido'])['count'].agg('sum').reset_index()
 
# Ahora hacemos un join de la información agrupada del conteo con la data original. Con esto obtenemos el valor total de conteo para cada agrupación.
#weekday_merged_tid_periodo = weekday_grouped_sum.merge(weekday_grouped_count_tid_periodo, left_on=['tid'], right_on=['tid'])
weekday_merged_tid_periodo = weekday_grouped_sum.merge(weekday_grouped_count.groupby(['Corredor',
                                                                                      'tid', 'complete_name', 'Sentido'])['count'].agg('sum'), left_on=['tid'], right_on=['tid'])


#Obtengo el peso de cada dia en el tid en el total del periodo agrupado, por cada sentido.
weekday_merged_tid_periodo['speed_ponderada_tid_periodo'] = weekday_merged_tid_periodo['speed_ponderada'] * weekday_merged_tid_periodo['count_y']/ weekday_merged_tid_periodo['count']
 
#Agrupo el valor final de cada tid para el periodo
weekday_grouped_sum_tid_periodo = weekday_merged_tid_periodo.groupby(['Corredor_x', 'tid', 'complete_name_x', 'Sentido'])['speed_ponderada_tid_periodo'].agg('sum').reset_index()
 


#***********************Ahora estimemos la velocidad ponderada de cada corredor en el tiempo**************************
 
#Agrupar la suma de 'count' por cada periodo agrupado. En este ejemplo es el día calendario.
weekday_grouped_count_corredor = weekday_grouped_sum.groupby(['Corredor_x','date', 'Sentido'])['count_y'].agg('sum').reset_index()
 
# Ahora hacemos un join de la información agrupada del conteo con la data original. Con esto obtenemos el valor total de conteo para cada agrupación.
 
weekday_merged_corredor = weekday_grouped_sum.merge(weekday_grouped_count_corredor, on =['Corredor_x','date', 'Sentido'])
 
#Obtengo el peso de cada medición de bitcarrier en el total del periodo agrupado, por cada sentido.
weekday_merged_corredor['speed_ponderada_corredor'] = weekday_merged_corredor['speed_ponderada']* weekday_merged_corredor['count_y_x']/ weekday_merged_corredor['count_y_y']
weekday_grouped_sum_corredor = weekday_merged_corredor.groupby(['Corredor_x','date', 'Sentido','count_y_y'])['speed_ponderada_corredor'].agg('sum').reset_index()
 



# ********************** Vel ponderada por corredor por sentido ***************************
 
#Ahora calculemos la velocidad ponderada del Corredor en ese periodo de tiempo
weekday_grouped_count_corredor_tiempo = weekday_grouped_count_corredor.groupby(['Corredor_x', 'Sentido'])['count_y'].agg('sum').reset_index()
 
# Ahora hacemos un join de la información agrupada del conteo con la data original. Con esto obtenemos el valor total de conteo para cada agrupación.
 
weekday_merged_corredor_tiempo = weekday_grouped_sum_corredor.merge(weekday_grouped_count_corredor_tiempo, on =['Corredor_x', 'Sentido'])
 
#Obtengo el peso de cada dia en el corredor en el total del periodo agrupado, por cada sentido.
weekday_merged_corredor_tiempo['speed_ponderada_corredor_tiempo'] = weekday_merged_corredor_tiempo['speed_ponderada_corredor']* weekday_merged_corredor_tiempo['count_y_y']/ weekday_merged_corredor_tiempo['count_y']
weekday_grouped_sum_corredor_tiempo = weekday_merged_corredor_tiempo.groupby(['Corredor_x', 'Sentido', 'count_y'])['speed_ponderada_corredor_tiempo'].agg('sum').reset_index()

#--- Obtener la velocidad de Bogota -----
contar_bogota = weekday_grouped_sum_corredor_tiempo['count_y'].sum()
weekday_grouped_sum_corredor_tiempo['speed_bogota'] = weekday_grouped_sum_corredor_tiempo['speed_ponderada_corredor_tiempo']*weekday_grouped_sum_corredor_tiempo['count_y']/weekday_grouped_sum_corredor_tiempo['count_y'].sum()
speed_bogota = round(weekday_grouped_sum_corredor_tiempo['speed_bogota'].sum(),1)


#***********************Velocidad ponderada de cada tramo para por cada hora en el periodo evaluado *********************************
weekday_grouped_count_hour = df_bitcarrier_mainroad_weekday.groupby(['Corredor', 'tid', 'complete_name', 'Sentido', 'hour'])['count'].agg('sum').reset_index()

#Agrupar la suma de 'count' por cada tid en el periodo agrupado.
weekday_merged_hour = df_bitcarrier_mainroad_weekday.merge(weekday_grouped_count_hour, on =['tid','Sentido', 'hour'])

#Obtengo el peso de cada medición de bitcarrier en el total del periodo agrupado.
weekday_merged_hour['peso'] = weekday_merged_hour['count_x']/ weekday_merged_hour['count_y']
weekday_merged_hour['speed_ponderada_hour'] = weekday_merged_hour['speed']* weekday_merged_hour['peso']


#Con la velocidad ponderada ya obtenida, agrupo la suma de velocidad de acuerdo por hora. 
weekday_grouped_sum_hour = weekday_merged_hour.groupby(['Corredor_x','tid', 'complete_name_x','hour', 'Sentido', 'count_y'])['speed_ponderada_hour'].agg('sum').reset_index()

#********************** Velocidad ponderada de cada corredor para cada hora en el periodo evaluado *******
weekday_grouped_count_corredor_hour = weekday_grouped_count_hour.groupby(['Corredor','Sentido','hour'])['count'].agg('sum').reset_index() #agregar filtro por horas

weekday_merged_corredor_hour = weekday_grouped_sum_hour.merge(weekday_grouped_count_corredor_hour, left_on =['Corredor_x','hour', 'Sentido'], right_on=['Corredor','hour', 'Sentido'])

#Obtengo el peso de cada tramo en el corredor en el total del periodo agrupado, por cada sentido por hora.
weekday_merged_corredor_hour['speed_ponderada_corredor_hour'] = weekday_merged_corredor_hour['speed_ponderada_hour']* weekday_merged_corredor_hour['count_y']/ weekday_merged_corredor_hour['count']
weekday_grouped_sum_corredor_hour = weekday_merged_corredor_hour.groupby(['Corredor_x',  'Sentido','hour','count'])['speed_ponderada_corredor_hour'].agg('sum').reset_index()




###################### Obtener velocidad ponderada de cada tramo en el rango de horas establecidas ########

weekday_grouped_sum_hour_count = weekday_grouped_sum_hour.groupby(['Corredor_x', 'tid','complete_name_x', 'Sentido'])['count_y'].agg('sum').reset_index()

merge_tramo_hour = weekday_grouped_sum_hour.merge(weekday_grouped_sum_hour_count, left_on=['tid'], right_on=['tid'])

merge_tramo_hour['speed_ponderada']= merge_tramo_hour['speed_ponderada_hour']* merge_tramo_hour['count_y_x']/merge_tramo_hour['count_y_y']

weekday_group_speed_tramo_horas = merge_tramo_hour.groupby(['Corredor_x_x', 'tid', 'complete_name_x_x', 'Sentido_x', 'count_y_y'])['speed_ponderada'].agg('sum').reset_index()

#------- Tabla por corredor y sentido ponderado por fecha--------------------

weekday_grouped_sum_corredor_tiempo['speed_ponderada_corredor_tiempo']= round(weekday_grouped_sum_corredor_tiempo['speed_ponderada_corredor_tiempo'],1)
 
pivot_table= weekday_grouped_sum_corredor_tiempo.pivot_table(index=['Corredor_x'], columns='Sentido',  values= 'speed_ponderada_corredor_tiempo').reset_index()
pivot_table.rename(columns={'Corredor_x':'Main road'}, inplace=True)


#********************** Velocidad ponderada de cada corredor para cada hora en el periodo evaluado *******
weekday_grouped_count_corredor_hour = weekday_grouped_count_hour.groupby(['Corredor','Sentido','hour'])['count'].agg('sum').reset_index() #agregar filtro por horas

weekday_merged_corredor_hour = weekday_grouped_sum_hour.merge(weekday_grouped_count_corredor_hour, left_on =['Corredor_x','hour', 'Sentido'], right_on=['Corredor','hour', 'Sentido'])

#Obtengo el peso de cada tramo en el corredor en el total del periodo agrupado, por cada sentido por hora.
weekday_merged_corredor_hour['speed_ponderada_corredor_hour'] = weekday_merged_corredor_hour['speed_ponderada_hour']* weekday_merged_corredor_hour['count_y']/ weekday_merged_corredor_hour['count']


#Mapas
 
#Load bitcarrier shape file
#bitcarrier_shp = gpd.read_file('/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/Data_Final/Bitcarrier_5min/df_bctraveltimes_geom/df_bctraveltimes_geom.shp')
bitcarrier_shp = gpd.read_file('df_bctraveltimes_geom.shp')

#Merge shape file with main_roads key file
bitcarrier_merge=bitcarrier_shp.merge(llave_movilidad, on='tid', how='right' )
 
#Get Geopanda of bitcarrier with geometry of the Corredores and its average speeds
bitcarrier_shp_merged = bitcarrier_merge.merge(weekday_grouped_sum_tid_periodo, left_on='tid', right_on='tid')

#Geopanda por tramo por horas de dia
bitcarrier_shp_merged_hour = bitcarrier_merge.merge(weekday_group_speed_tramo_horas, left_on='tid', right_on='tid')

lats = []
lons = []
names = []
speed_map =[]

mark_values = {0:'0', 1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'10',11:'11',12:'12',
         13:'13',14:'14',15:'15',16:'16',17:'17',18:'18',19:'19',20:'20',21:'21',22:'22',23:'23'}
         
        
#app = JupyterDash(__name__, external_stylesheets = [dbc.themes.SANDSTONE])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "1rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div([
                    
html.H3('SMD', className='display-4'),
html.Hr(),
html.P('Options', className='lead'),
html.Hr(),

dbc.Nav([
         html.H6('Select the main road', className='display-6'),
          dcc.Dropdown(id='Corredor-dropdown', clearable = True, value ='', 
                       options =[
                                 {'label': c, 'value' :c}
                                 for c in weekday_grouped_sum.Corredor_x.unique()],
                       placeholder = 'Select main road',
                       style={'width': '90%'}),
         html.Hr(),
         html.H6('Select hour or date view', className='display-6'),
         dcc.Dropdown(id='Option-dia-hora', clearable =False, value ='Fecha',
                      options =[
                                {'label': 'by date', 'value': 'Fecha'},
                                {'label': 'by  hour', 'value': 'Hora'}],
                      placeholder='Selecciona la variable',
                      style={'width': '90%', 'display': 'block'}),
         html.Hr()

         
],
vertical = True,
pills = True,

),
],
style = SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)



app.layout= html.Div([dcc.Location(id='url'), sidebar,
    dbc.Container([
                           dcc.Store(id='store'),
                           html.H1('EDA Bitcarrier Speed'),
                           html.Hr(),
                           dbc.Tabs(
                               [
                                dbc.Tab(label='Speed', 
                                        tab_id='vel_ponderada', 
                                        children=[
                                                  html.Div([html.H2('Main roads Speed - (ago - oct)'),
                                                            dbc.Row([
                                                                     dbc.Col(dbc.Card([
                                                                                       dbc.CardHeader(html.H4('Speed by main road by direction')),
                                                                                       dbc.CardBody([
                                                                                                     html.P(
                                                                                                         dash_table.DataTable(
                                                                                                           id='table_speed' ,
                                                                                                           columns =[],
                                                                                                           #fixed_rows={ 'headers': True, 'data': 0 },
                                                                                                           data = [],
                                                                                                           style_data={
                                                                                                             'whiteSpace':'normal',
                                                                                                             'height':'auto'  
                                                                                                           },
                                                                                                           style_as_list_view=True,
                                                                                                           style_data_conditional =[
                                                                                                             {'if': {'row_index': 'odd'},
                                                                                                                                        'backgroundColor': 'rgb(92, 190, 228)'},
                                                                                                                                        {'if': {'row_index': 'even'},
                                                                                                                                        'backgroundColor': 'rgb(40, 171, 224)'},
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{NS}>=50' , 'column_id':'NS'}, 'color': 'rgb(0, 128, 0)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{SN}>=50' , 'column_id':'SN'}, 'color': 'rgb(0, 128, 0)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{EW}>=50' , 'column_id':'EW'}, 'color': 'rgb(0, 128, 0)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{WE}>=50' , 'column_id':'WE'}, 'color': 'rgb(0, 128, 0)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{NS}>=20 && {NS}<50', 'column_id':'NS'}, 'color': 'rgb(254, 244, 173)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{SN}>=20 && {SN}<50', 'column_id':'SN'}, 'color': 'rgb(254, 244, 173)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{EW}>=20 && {EW}<50', 'column_id':'EW'}, 'color': 'rgb(254, 244, 173)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{WE}>=20 && {WE}<50', 'column_id':'WE'}, 'color': 'rgb(254, 244, 173)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{NS}<20', 'column_id':'NS'}, 'color': 'rgb(213, 46, 37)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{SN}<20', 'column_id':'SN'}, 'color': 'rgb(213, 46, 37)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{EW}<20', 'column_id':'EW'}, 'color': 'rgb(213, 46, 37)'
                                                                                                                                           },
                                                                                                                                           {'if':{
                                                                                                                                           'filter_query':'{WE}<20', 'column_id':'WE'}, 'color': 'rgb(213, 46, 37)'
                                                                                                                                           }
                                                                                                                                                
                                                                                                                       ],
                                                                                                           style_cell={'padding': '5px', 'font_size': '15px', 'text_align': 'center' 
                                                                                                                       
                                                                                                                       },
                                                                                                           style_table={'minWidth': '50%', 'maxWidth': '100%'},
                                                                                                           sort_action="native",
                                                                                                           style_header={
                                                                                                               'backgroundColor': 'rgb(40, 171, 224)',
                                                                                                               'fontWeight': 'bold'},
                                                                                                               
                                                                                                           style_cell_conditional=[
                                                                                                                                  {'if': {'column_id':'Main road'}, 'width':'55%'},
                                                                                                                                  {'if': {'column_id':'EW'}, 'width':'15%'},
                                                                                                                                  {'if': {'column_id':'NS'}, 'width':'15%'},
                                                                                                                                  {'if': {'column_id':'SN'}, 'width':'15%'},
                                                                                                                                  {'if': {'column_id':'WE'}, 'width':'15%'}
                                                                                                           ]                    
                                                                                                         ), className ='card-text')
                                                                                                     ])
                                                                                       ], color='info', inverse=True)
                                                                     ),
                                                                     dbc.Col(
                                                                         dbc.Card([
                                                                                   dbc.CardHeader(html.H4('Bogotá speed')),
                                                                                   dbc.CardBody([dcc.Graph(id='speed_bogota')
                                                                                                 
                                                                                                 ])
                                                                                   ], color='info', inverse=True)
                                                                         )
                                                                     ]),
                                                            html.Hr(),
                                                            html.Div([
                                                                      html.H4('Selecciona el rango horario'),
                                                                      dbc.Row([
                                                                               dbc.Col(
                                                                               html.Div([
                                                                                         dcc.RangeSlider(id='hour_slider',
                                                                                                         min=0, max=23, marks = mark_values,
                                                                                                         value=[0,23])], style ={'width':'100%'})
                                                                      )])
                                                                      ],id = 'Div1', style ={'display':'none','width':'100%'}),
                                                            dbc.Row([
                                                                     dbc.Col(
                                                                         dcc.Graph(id='speed_map')
                                                                         ),
                                                                     dbc.Col(
                                                                         dcc.Graph(id='graph2')
                                                                         )
                                                                     ])
                                                            ]),
                                                  dcc.Graph(id='graph1')
                                                  ])
                                ], id = 'tabs',active_tab = 'vel_ponderada'
                                ),
                   html.Div(id='tab-content', className='p-4')
                   ])
    ])



#----- Actualiza tarjeta con velocidad de Bogota -----

@app.callback(Output('speed_bogota', 'figure'), [Input("Option-dia-hora", "value")],
              [Input('hour_slider','value')]  )

def update_bogota (opcion, Rango_hora):
  if opcion=='Fecha':
    fig = go.Figure(go.Indicator(mode = 'gauge + number', value =speed_bogota, title = {'text':'km/h'},
                               gauge = {'axis':{'range':[None, 65]},
                                        'threshold':{'line':{'color':'red','width':4},'thickness':0.75, 'value':60}
                                        
                                        }))
  else: #Escogen hora
    hour_min = Rango_hora[0]
    hour_max = Rango_hora[1]
#********************** Velocidad ponderada de cada corredor para cada hora en el periodo evaluado *******

    weekday_grouped_sum_corredor_hour = weekday_merged_corredor_hour[(weekday_merged_corredor_hour['hour']>=hour_min) & (weekday_merged_corredor_hour['hour']<=hour_max) ].groupby(['Corredor_x',  'Sentido','hour','count'])['speed_ponderada_corredor_hour'].agg('sum').reset_index()

#--- Obtener la velocidad de Bogota -----
    weekday_grouped_sum_corredor_hour['speed_bogota'] = weekday_grouped_sum_corredor_hour['speed_ponderada_corredor_hour']*weekday_grouped_sum_corredor_hour['count']/weekday_grouped_sum_corredor_hour['count'].sum()
    speed_bogota_hour = round(weekday_grouped_sum_corredor_hour['speed_bogota'].sum(),1)
    fig = go.Figure(go.Indicator(mode = 'gauge + number', value =speed_bogota_hour, title = {'text':'km/h'},
                               gauge = {'axis':{'range':[None, 65]},
                                        'threshold':{'line':{'color':'red','width':4},'thickness':0.75, 'value':60}
                                        
                                        }))


  return fig


#-----Actualiza tabla main roads -------
def update_columns(corredor):
  if corredor=='Av. Calle 26':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'EW', 'name': 'EW'},
                 {'id': 'WE', 'name': 'WE'}]
  if corredor=='Autopista Norte':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}]
  if corredor=='Av. Boyacá':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}]
  if corredor=='Av. Caracas':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}]        
  if corredor=='Av. Carrera 7ma':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}]           
  if corredor=='Av. Ciudad de Cali':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}]      
  if corredor=='Av. NQS':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}] 
  if corredor=='Av. Suba':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}] 
  if corredor=='Av. Calle 80':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'EW', 'name': 'EW'},
                 {'id': 'WE', 'name': 'WE'}]
  if corredor=='Av. Centenario (Calle 13)':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'EW', 'name': 'EW'},
                 {'id': 'WE', 'name': 'WE'}]
  if corredor=='Av. de las Américas':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'EW', 'name': 'EW'},
                 {'id': 'WE', 'name': 'WE'}]
  if corredor=='Av. Primero de Mayo':
      columns = [{'id': 'Main road', 'name': 'Main road'},
                  {'id': 'EW', 'name': 'EW'},
                 {'id': 'WE', 'name': 'WE'},
                  {'id': 'NS', 'name': 'NS'},
                 {'id': 'SN', 'name': 'SN'}]
  return columns


@app.callback([Output('table_speed', 'data'), Output('table_speed', 'columns')], 
              [Input("Corredor-dropdown", "value")],
              [Input("Option-dia-hora", "value")],
              [Input('hour_slider','value')]  )

def update_table (corredor, opcion, Rango_hora):
  #dff=pivot_table
  
  if opcion=='Fecha':
    if corredor=='' or corredor == None:
      dff=pivot_table
      columns =[{'id':c, 'name': c } for c in pivot_table.columns]
    
      
    else:
      dff=pivot_table.loc[pivot_table['Main road']== corredor]
      columns=update_columns(corredor)

    return dff.to_dict('records'), columns

  else: #Calculo por horas
    hour_min = Rango_hora[0]
    hour_max = Rango_hora[1]

    if corredor=='' or corredor == None:
      #********************** Velocidad ponderada de cada corredor para cada hora en el periodo evaluado *******

      weekday_grouped_sum_corredor_hour = weekday_merged_corredor_hour[(weekday_merged_corredor_hour['hour']>=hour_min) & (weekday_merged_corredor_hour['hour']<=hour_max)].groupby(['Corredor_x',  'Sentido','hour','count'])['speed_ponderada_corredor_hour'].agg('sum').reset_index()
      #Con base en la estimación anterior
      conteo_corredor_todas_horas = weekday_grouped_sum_corredor_hour.groupby(['Corredor_x', 'Sentido'])['count'].agg('sum').reset_index()
      merge_corredor_horas = weekday_grouped_sum_corredor_hour.merge(conteo_corredor_todas_horas,on=['Corredor_x', 'Sentido'] )
      merge_corredor_horas['speed_corredor']= merge_corredor_horas['speed_ponderada_corredor_hour'] * merge_corredor_horas['count_x']/merge_corredor_horas['count_y']
      speed_corredor_horas = merge_corredor_horas.groupby(['Corredor_x', 'Sentido', 'count_y'])['speed_corredor'].agg('sum').reset_index()
      #------- Tabla por corredor y sentido ponderado por fecha--------------------

      speed_corredor_horas['speed_corredor']= round(speed_corredor_horas['speed_corredor'],1)
 
      pivot_table_hora= speed_corredor_horas.pivot_table(index=['Corredor_x'], columns='Sentido',  values= 'speed_corredor').reset_index()
      pivot_table_hora.rename(columns={'Corredor_x':'Main road'}, inplace=True)
      columns =[{'id':c, 'name': c } for c in pivot_table.columns]
      #return pivot_table_hora.to_dict('records'), columns

    else:
            #********************** Velocidad ponderada de cada corredor para cada hora en el periodo evaluado *******
      
      weekday_grouped_sum_corredor_hour = weekday_merged_corredor_hour[(weekday_merged_corredor_hour['Corredor']==corredor) & (weekday_merged_corredor_hour['hour']>=hour_min) & (weekday_merged_corredor_hour['hour']<=hour_max)].groupby(['Corredor_x',  'Sentido','hour','count'])['speed_ponderada_corredor_hour'].agg('sum').reset_index()
      #Con base en la estimación anterior
      conteo_corredor_todas_horas = weekday_grouped_sum_corredor_hour.groupby(['Corredor_x', 'Sentido'])['count'].agg('sum').reset_index()
      merge_corredor_horas = weekday_grouped_sum_corredor_hour.merge(conteo_corredor_todas_horas,on=['Corredor_x', 'Sentido'] )
      merge_corredor_horas['speed_corredor']= merge_corredor_horas['speed_ponderada_corredor_hour'] * merge_corredor_horas['count_x']/merge_corredor_horas['count_y']
      speed_corredor_horas = merge_corredor_horas.groupby(['Corredor_x', 'Sentido', 'count_y'])['speed_corredor'].agg('sum').reset_index()
      #------- Tabla por corredor y sentido ponderado por fecha--------------------

      speed_corredor_horas['speed_corredor']= round(speed_corredor_horas['speed_corredor'],1)
 
      pivot_table_hora= speed_corredor_horas.pivot_table(index=['Corredor_x'], columns='Sentido',  values= 'speed_corredor').reset_index()
      pivot_table_hora.rename(columns={'Corredor_x':'Main road'}, inplace=True)
      
      columns=update_columns(corredor)
    return pivot_table_hora.to_dict('records'), columns



#****** Función para crear mapa y pintar en el dashboard *************

@app.callback(Output('speed_map', 'figure'),
    [Input("Corredor-dropdown", "value")],
    [Input("Option-dia-hora", "value")],
    [Input('hour_slider','value')]    )


def update_map(corredor, opcion, Rango_hora):
  lats = []
  lons = []
  names = []
  speed_map =[]
  fig=[]

  if opcion=='Fecha':
    if corredor=='' or corredor == None:
     
      for feature, name, speed in zip(bitcarrier_shp_merged.geometry, 
                                      bitcarrier_shp_merged.complete_name_x, 
                                      bitcarrier_shp_merged.speed_ponderada_tid_periodo):
          if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
          elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
          else:
            continue
          for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, [name]*len(y))
            speed_map = np.append(speed_map, [speed]*len(y))
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, "a")
            speed_map = np.append(speed_map, 0)
    
    else: 
      for feature, name, speed in zip(bitcarrier_shp_merged[bitcarrier_shp_merged['Corredor_x']==corredor].geometry, 
                                      bitcarrier_shp_merged[bitcarrier_shp_merged['Corredor_x']==corredor].complete_name_x, 
                                      bitcarrier_shp_merged[bitcarrier_shp_merged['Corredor_x']==corredor].speed_ponderada_tid_periodo):
          if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
          elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
          else:
            continue
          for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, [name]*len(y))
            speed_map = np.append(speed_map, [speed]*len(y))
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, "a")
            speed_map = np.append(speed_map, 0)
       
    
    fig = px.scatter_mapbox( lat=lats, lon=lons, mapbox_style="carto-positron", zoom=10.7, width=600, height=800, center={'lat': 4.64 , 'lon': -74.11}, 
                            hover_name = names, color = speed_map, color_continuous_scale='RdYlGn', range_color=[0,60], labels ={'color':'speed'})
    fig.update_layout(title_text='Map of main road by date' , margin=dict(t=90,l=0,b=0,r=110))
    return fig
  #Cuando se escoja la opción por hora
  else:
    hour_min = Rango_hora[0]
    hour_max = Rango_hora[1]
    
    if corredor=='' or corredor == None:
      #Con la velocidad ponderada ya obtenida, agrupo la suma de velocidad de acuerdo por hora. 
      weekday_grouped_sum_hour = weekday_merged_hour[(weekday_merged_hour['hour']>=hour_min) & (weekday_merged_hour['hour']<=hour_max)].groupby(['Corredor_x','tid', 'complete_name_x','hour', 'Sentido', 'count_y'])['speed_ponderada_hour'].agg('sum').reset_index()

###################### Obtener velocidad ponderada de cada tramo en el rango de horas establecidas ########

      weekday_grouped_sum_hour_count = weekday_grouped_sum_hour.groupby(['Corredor_x', 'tid','complete_name_x', 'Sentido'])['count_y'].agg('sum').reset_index()

      merge_tramo_hour = weekday_grouped_sum_hour.merge(weekday_grouped_sum_hour_count, left_on=['tid'], right_on=['tid'])

      merge_tramo_hour['speed_ponderada']= merge_tramo_hour['speed_ponderada_hour']* merge_tramo_hour['count_y_x']/merge_tramo_hour['count_y_y']

      weekday_group_speed_tramo_horas = merge_tramo_hour.groupby(['Corredor_x_x', 'tid', 'complete_name_x_x', 'Sentido_x', 'count_y_y'])['speed_ponderada'].agg('sum').reset_index()

      bitcarrier_shp_merged_hour = bitcarrier_merge.merge(weekday_group_speed_tramo_horas, left_on='tid', right_on='tid')

     
      for feature, name, speed in zip(bitcarrier_shp_merged_hour.geometry, 
                                      bitcarrier_shp_merged_hour.complete_name_x_x, 
                                      bitcarrier_shp_merged_hour.speed_ponderada):
          if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
          elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
          else:
            continue
          for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, [name]*len(y))
            speed_map = np.append(speed_map, [speed]*len(y))
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, "a")
            speed_map = np.append(speed_map, 0)
    
    else: 
            #Con la velocidad ponderada ya obtenida, agrupo la suma de velocidad de acuerdo por hora. 
      weekday_grouped_sum_hour = weekday_merged_hour[(weekday_merged_hour['hour']>=hour_min) & (weekday_merged_hour['hour']<=hour_max)].groupby(['Corredor_x','tid', 'complete_name_x','hour', 'Sentido', 'count_y'])['speed_ponderada_hour'].agg('sum').reset_index()

###################### Obtener velocidad ponderada de cada tramo en el rango de horas establecidas ########

      weekday_grouped_sum_hour_count = weekday_grouped_sum_hour.groupby(['Corredor_x', 'tid','complete_name_x', 'Sentido'])['count_y'].agg('sum').reset_index()

      merge_tramo_hour = weekday_grouped_sum_hour.merge(weekday_grouped_sum_hour_count, left_on=['tid'], right_on=['tid'])

      merge_tramo_hour['speed_ponderada']= merge_tramo_hour['speed_ponderada_hour']* merge_tramo_hour['count_y_x']/merge_tramo_hour['count_y_y']

      weekday_group_speed_tramo_horas = merge_tramo_hour.groupby(['Corredor_x_x', 'tid', 'complete_name_x_x', 'Sentido_x', 'count_y_y'])['speed_ponderada'].agg('sum').reset_index()

      bitcarrier_shp_merged_hour = bitcarrier_merge.merge(weekday_group_speed_tramo_horas, left_on='tid', right_on='tid')


      for feature, name, speed in zip(bitcarrier_shp_merged_hour[bitcarrier_shp_merged_hour['Corredor_x_x']==corredor].geometry, 
                                      bitcarrier_shp_merged_hour[bitcarrier_shp_merged_hour['Corredor_x_x']==corredor].complete_name_x_x, 
                                      bitcarrier_shp_merged_hour[bitcarrier_shp_merged_hour['Corredor_x_x']==corredor].speed_ponderada):
          if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
          elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
          else:
            continue
          for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, [name]*len(y))
            speed_map = np.append(speed_map, [speed]*len(y))
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, "a")
            speed_map = np.append(speed_map, 0)
       
    
    fig = px.scatter_mapbox( lat=lats, lon=lons, mapbox_style="carto-positron", zoom=10.7, width=600, height=800, center={'lat': 4.64 , 'lon': -74.11}, 
                            hover_name = names, color = speed_map, color_continuous_scale='RdYlGn', range_color=[0,60], labels ={'color':'speed'})
    fig.update_layout(title_text='Map of main road by hour ( ' +  str(hour_min) + ' - ' + str(hour_max) + ' hours)'  , margin=dict(t=90,l=0,b=0,r=110))
    return fig

    

@app.callback(
    Output('graph1', 'figure'),
    [Input("Corredor-dropdown", "value")],
    [Input("Option-dia-hora", "value")]
)

def update_graph1(corredor, opcion):

  if opcion=='Fecha':
    if corredor=='' or corredor == None:
      fig = px.line(weekday_grouped_sum, x='date', y='speed_ponderada', color='complete_name_x', facet_col='Sentido', facet_col_wrap=2,
                    title='Velocidad ponderada de todos los tramos de todos los corredores', render_mode="webgl" , template = 'simple_white', 
                    labels={'speed_ponderada':'speed', 'date':'date','complete_name_x': 'segment'}) 
      #fig.update_layout(xaxis_title='Fecha', yaxis_title='Velocidad')
      return fig
    else: 
      fig = px.line(weekday_grouped_sum[weekday_grouped_sum['Corredor_x']==corredor], x='date', y='speed_ponderada', color='complete_name_x', facet_col='Sentido', facet_col_wrap=2,
                    title='Weigthed speed by segemnts for ' + corredor, render_mode="webgl" , template = 'simple_white', labels={'speed_ponderada':'speed', 'date':'date','complete_name_x': 'segment'}) 
      #fig.update_layout(xaxis_title='Fecha', yaxis_title='Velocidad') 
      return fig

  else: #si selecciona hora
    if corredor=='' or corredor == None: 
      fig = px.line(weekday_grouped_sum_hour, x='hour', y='speed_ponderada_hour', color='complete_name_x', facet_col='Sentido',
                    title='Velocidad ponderada del tramo ' , render_mode="webgl", 
                    template = 'simple_white', labels={'Corredor_x': 'main road', 'speed_ponderada':'speed', 'date':'date','complete_name_x': 'segment'} 
                  ) 
      #fig.update_layout(xaxis_title='Hora', yaxis_title='Velocidad') 
      return fig
    else: 
      fig = px.line(weekday_grouped_sum_hour[weekday_grouped_sum_hour['Corredor_x']==corredor], x='hour', y='speed_ponderada_hour', color='complete_name_x', facet_col='Sentido', facet_col_wrap=2,
                    title='Velocidad ponderada del tramo ' , render_mode="webgl", template = 'simple_white', labels={'speed_ponderada_hour':'speed', 'hour':'hour','Corredor_x': 'main road','complete_name_x': ''}
                    ) 
      #fig.update_layout(xaxis_title='Hora', yaxis_title='Velocidad') 
      return fig 


@app.callback(
    Output('graph2', 'figure'),
    [Input("Corredor-dropdown", "value")],
    [Input("Option-dia-hora", "value")],
    [Input('hour_slider','value')]
)

def update_graph2(corredor, opcion, Rango_hora):
  if opcion =='Fecha':
    print(corredor)

    if corredor=='' or corredor == None :
      
      fig = px.line(weekday_grouped_sum_corredor, x='date', y='speed_ponderada_corredor', color='Corredor_x', facet_col='Sentido', facet_col_wrap=1,
                    title='Velocidad ponderada de todos los corredores', render_mode="webgl",
                    template = 'simple_white', labels={'speed_ponderada_corredor':'speed', 'date':'date', 'Corredor_x': 'main road'}, height=800)
      
                    
      fig.update_layout(margin=dict(t=90,l=0,b=0,r=0))
      
      return fig
    else:
      pivot_table
    
    
      fig=px.line(weekday_grouped_sum_corredor[weekday_grouped_sum_corredor['Corredor_x']==corredor], x='date', y='speed_ponderada_corredor', color='Corredor_x', facet_col='Sentido', facet_col_wrap=1,
                    title='Velocidad ponderada del corredor ' + corredor, 
                    template = 'simple_white', labels={'speed_ponderada_corredor':'speed', 'date':'date', 'Corredor_x': 'main road'} , height=800  )
      fig.update_layout(margin=dict(t=90,l=0,b=0,r=0))

      return fig

  else:# si escogen hora
    hour_min = Rango_hora[0]
    hour_max = Rango_hora[1]
    if corredor=='' or corredor == None:
      #Con la velocidad ponderada ya obtenida, agrupo la suma de velocidad de acuerdo por hora. 
      weekday_grouped_sum_hour = weekday_merged_hour[(weekday_merged_hour['hour']>=hour_min) & (weekday_merged_hour['hour']<=hour_max)].groupby(['Corredor_x','tid', 'complete_name_x','hour', 'Sentido', 'count_y'])['speed_ponderada_hour'].agg('sum').reset_index()

#********************** Velocidad ponderada de cada corredor para cada hora en el periodo evaluado *******
      weekday_grouped_count_corredor_hour = weekday_grouped_count_hour[(weekday_grouped_count_hour['hour']>=hour_min) & (weekday_grouped_count_hour['hour']<=hour_max)].groupby(['Corredor','Sentido','hour'])['count'].agg('sum').reset_index()

      weekday_merged_corredor_hour = weekday_grouped_sum_hour.merge(weekday_grouped_count_corredor_hour, left_on =['Corredor_x','hour', 'Sentido'], right_on=['Corredor','hour', 'Sentido'])

#Obtengo el peso de cada tramo en el corredor en el total del periodo agrupado, por cada sentido por hora.
      weekday_merged_corredor_hour['speed_ponderada_corredor_hour'] = weekday_merged_corredor_hour['speed_ponderada_hour']* weekday_merged_corredor_hour['count_y']/ weekday_merged_corredor_hour['count']
      weekday_grouped_sum_corredor_hour = weekday_merged_corredor_hour.groupby(['Corredor_x',  'Sentido','hour','count'])['speed_ponderada_corredor_hour'].agg('sum').reset_index()





      fig = px.line(weekday_grouped_sum_corredor_hour, x='hour', y='speed_ponderada_corredor_hour', color='Corredor_x', facet_col='Sentido',facet_col_wrap=1,
                    title='Velocidad ponderada de todos los corredores' , render_mode="webgl",
                    template = 'simple_white', labels={'speed_ponderada_corredor_hour':'speed', 'hour':'Hour', 'Corredor_x': 'main road'} , height=800
                  )
      fig.update_layout(margin=dict(t=90,l=0,b=0,r=0))
      return fig
    else:
            #Con la velocidad ponderada ya obtenida, agrupo la suma de velocidad de acuerdo por hora. 
      weekday_grouped_sum_hour = weekday_merged_hour[(weekday_merged_hour['hour']>=hour_min) & (weekday_merged_hour['hour']<=hour_max)].groupby(['Corredor_x','tid', 'complete_name_x','hour', 'Sentido', 'count_y'])['speed_ponderada_hour'].agg('sum').reset_index()

#********************** Velocidad ponderada de cada corredor para cada hora en el periodo evaluado *******
      weekday_grouped_count_corredor_hour = weekday_grouped_count_hour[(weekday_grouped_count_hour['hour']>=hour_min) & (weekday_grouped_count_hour['hour']<=hour_max)].groupby(['Corredor','Sentido','hour'])['count'].agg('sum').reset_index()

      weekday_merged_corredor_hour = weekday_grouped_sum_hour.merge(weekday_grouped_count_corredor_hour, left_on =['Corredor_x','hour', 'Sentido'], right_on=['Corredor','hour', 'Sentido'])

#Obtengo el peso de cada tramo en el corredor en el total del periodo agrupado, por cada sentido por hora.
      weekday_merged_corredor_hour['speed_ponderada_corredor_hour'] = weekday_merged_corredor_hour['speed_ponderada_hour']* weekday_merged_corredor_hour['count_y']/ weekday_merged_corredor_hour['count']
      weekday_grouped_sum_corredor_hour = weekday_merged_corredor_hour.groupby(['Corredor_x',  'Sentido','hour','count'])['speed_ponderada_corredor_hour'].agg('sum').reset_index()

      fig = px.line(weekday_grouped_sum_corredor_hour[weekday_grouped_sum_corredor_hour['Corredor_x']==corredor], x='hour', y='speed_ponderada_corredor_hour', color='Corredor_x', facet_col='Sentido', facet_col_wrap=1,
                    title='Velocidad ponderada del Corredor ' + corredor , render_mode="webgl",
                    template = 'simple_white', labels={'speed_ponderada_corredor_hour':'Speed', 'hour':'Hour', 'Corredor_x': 'Main Road'} , height=800
                  )
      fig.update_layout(margin=dict(t=90,l=0,b=0,r=0))
    
    
      return fig

#-------------------- Hide/show hourly slider -----------------

@app.callback(Output(component_id='Div1', component_property = 'style'),
[Input(component_id='Option-dia-hora', component_property='value')])

def show_hide_element(visibility_state):
  if visibility_state=='Fecha':
    return {'display':'none', 'width':'100%'}
  else:
    return {'display': 'inline-block', 'width':'100%'}



#app.run_server(mode='external', debug = True)