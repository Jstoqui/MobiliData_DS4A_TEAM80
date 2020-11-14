#@title
import geopandas as gpd
#import geojson as gjs
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString
import pandas as pd
#import matplotlib.pyplot as plt
#import json
#import contextily as ctx
import re
import numpy as np
 
from plotly.offline import iplot
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import shapely.geometry
 
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc
import dash_table
 
from pandas import json_normalize


from google.cloud import bigquery
import os
from google.colab import data_table
from google.colab import drive
drive.mount('/content/drive/')
%reload_ext google.colab.data_table
%load_ext google.cloud.bigquery


#----Traigo el query completo desde Big Query-------

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/Dash/secretaria-movilidad-d7884405beb2.json'

client = bigquery.Client(project='secretaria-movilidad')

df_bitcarrier = client.query('''
SELECT * FROM `secretaria-movilidad.bitcarrier.bitcarrier`
''').to_dataframe()


####Loading data######
#df_bitcarrier_ago = gpd.read_file('/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/Data_Final/Bitcarrier_5min/velAgosto2020_24h.csv')
#df_bitcarrier_sep = gpd.read_file('/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/Data_Final/Bitcarrier_5min/velseptiembre2020_24h.csv')
#df_bitcarrier = df_bitcarrier_ago.append( df_bitcarrier_sep).reset_index()
#df_bitcarrier=df_bitcarrier_ago

#Converting types
df_bitcarrier['tid'] = df_bitcarrier['tid'].astype('int64')
df_bitcarrier['speed'] = df_bitcarrier['speed'].astype('float64')
df_bitcarrier['count'] = df_bitcarrier['count'].astype('int')
#Converting time to Date Time type
df_bitcarrier['Datetime'] = pd.to_datetime(df_bitcarrier['fecha'])
 
#Llave movilidad
llave_movilidad = pd.read_excel('/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/TramosCGT-REV.dbf - original.xlsx')
 
#Asignar nombres corredores del archivo llave al Dataframe de Bitcarrier
df_bitcarrier_mainroad = pd.merge(df_bitcarrier,llave_movilidad, left_on='tid' ,right_on='tid', how='right')
 
df_bitcarrier_mainroad['complete_name'] = df_bitcarrier_mainroad['name_from'] + ' - ' + df_bitcarrier_mainroad['name_to']
 
#Tag and eliminate the main roads in bitcarrier. We have to eliminate because this "segments" have average speed, count of vehicules of all main road. 
#For our analysis this is not good.
 
b_dict =[{'complete_name':'AUTONORTE - SANTA.FE;CL80', 'complete_road':'yes'},
         {'complete_name':'AUTONORTE - CL80;SANTA.FE', 'complete_road':'yes'},
{'complete_name':'KR72 - CL43AS;CL170', 'complete_road':'yes'},
{'complete_name':'KR72 - CL170;CL43AS', 'complete_road':'yes'},
{'complete_name':'AV.CARACAS - DIAG48SUR;CL80', 'complete_road':'yes'},
{'complete_name':'AV.CARACAS - CL80;DIAG48SUR', 'complete_road':'yes'},
{'complete_name':'KR7 - CL32;CL188', 'complete_road':'yes'},
{'complete_name':'KR7 - CL188;CL32', 'complete_road':'yes'},
{'complete_name':'NQS - CL100;CL59SUR', 'complete_road':'yes'},
{'complete_name':'NQS - CL59SUR;CL100', 'complete_road':'yes'},
{'complete_name':'AV.P.MAYO - KR80;KR3E', 'complete_road':'yes'},
{'complete_name':'AV.P.MAYO - KR3E;KR80', 'complete_road':'yes'},
{'complete_name':'AV.SUBA - KR94;SAN.MARTIN', 'complete_road':'yes'},
{'complete_name':'AV.SUBA - SAN.MARTIN;KR94', 'complete_road':'yes'},
{'complete_name':'CL26 - AV.CARACAS;MODELIA', 'complete_road':'yes'},
{'complete_name':'CL26 - MODELIA;AV.CARACAS', 'complete_road':'yes'},
{'complete_name':'CL80 - AV.CARACAS;KR119', 'complete_road':'yes'},
{'complete_name':'CL80 - KR119;AV.CARACAS', 'complete_road':'yes'},
{'complete_name':'CL13 - KR128;AV.CARACAS', 'complete_road':'yes'},
{'complete_name':'CL13 - AV.CARACAS;KR128', 'complete_road':'yes'},
{'complete_name':'AV.AMERICAS;CL34 - KR80;KR5', 'complete_road':'yes'},
{'complete_name':'KR86 - TV79D;CL90', 'complete_road':'yes'}
]
 
bit_main_roads = pd.DataFrame.from_dict(b_dict)
 
df_bitcarrier_mainroad_2 = df_bitcarrier_mainroad.merge(bit_main_roads, on='complete_name', how='left')
df_bitcarrier_mainroad = df_bitcarrier_mainroad_2[(df_bitcarrier_mainroad_2.complete_road)!='yes']
 
#Getting Hour and validanting average speed by tid, Hour and level of service
df_bitcarrier_mainroad['hour'] = df_bitcarrier_mainroad['Datetime'].dt.hour
df_bitcarrier_mainroad['minute'] = df_bitcarrier_mainroad['Datetime'].dt.minute
df_bitcarrier_mainroad['day'] = df_bitcarrier_mainroad['Datetime'].dt.day
df_bitcarrier_mainroad['weekday'] = df_bitcarrier_mainroad['Datetime'].dt.weekday
df_bitcarrier_mainroad['date'] = df_bitcarrier_mainroad['Datetime'].dt.date
 
df_bitcarrier_mainroad_weekday = df_bitcarrier_mainroad[(df_bitcarrier_mainroad['weekday']<=4)]
df_bitcarrier_mainroad_weekend = df_bitcarrier_mainroad[(df_bitcarrier_mainroad['weekday']>=5)]
 
#Group to obtain average speed by tramo
#df_bitcarrier_grouped=df_bitcarrier_mainroad.groupby(['Corredor','complete_name','name_to', 'weekday', 'hour','tid', 'Sentido'])['speed'].mean().reset_index()
 
#Agrupar la suma de 'count' por cada periodo agrupado. En este ejemplo es el día calendario.
weekday_grouped_count = df_bitcarrier_mainroad_weekday.groupby(['Corredor', 'tid', 'complete_name','date', 'Sentido'])['count'].agg('sum').reset_index()


#******************************De aquí para abajo, son procedimeintos para asegurar las gráficas *************************

# Ahora hacemos un join de la información agrupada del conteo con la data original. Con esto obtenemos el valor total de conteo para cada agrupación.
weekday_merged = df_bitcarrier_mainroad_weekday.merge(weekday_grouped_count, on =['tid','date', 'Sentido'])
#Obtengo el peso de cada medición de bitcarrier en el total del periodo agrupado.
weekday_merged['peso'] = weekday_merged['count_x']/ weekday_merged['count_y']
weekday_merged['speed_ponderada'] = weekday_merged['speed']* weekday_merged['peso']
 
#Con la velocidad ponderada ya obtenida, agrupo la suma de velocidad de acuerdo con el periodo. En este ejemplo por dia
weekday_grouped_sum = weekday_merged.groupby(['Corredor_x','tid', 'complete_name_x','date', 'Sentido', 'count_y'])['speed_ponderada'].agg('sum').reset_index()
 
#weekday_grouped_simple = df_bitcarrier_mainroad_weekday.groupby(['Corredor','tid', 'complete_name','date', 'Sentido'])['speed'].agg('mean').reset_index()
 



#***********************Velocidad ponderada de cada tramo para el periodo evaluado *********************************
#Agrupar la suma de 'count' por cada tid en el periodo agrupado.
weekday_grouped_count_tid_periodo = weekday_grouped_count.groupby(['Corredor','tid', 'complete_name', 'Sentido'])['count'].agg('sum').reset_index()
 
# Ahora hacemos un join de la información agrupada del conteo con la data original. Con esto obtenemos el valor total de conteo para cada agrupación.
weekday_merged_tid_periodo = weekday_grouped_sum.merge(weekday_grouped_count_tid_periodo, left_on=['tid'], right_on=['tid'])
 
#Obtengo el peso de cada dia en el tid en el total del periodo agrupado, por cada sentido.
weekday_merged_tid_periodo['speed_ponderada_tid_periodo'] = weekday_merged_tid_periodo['speed_ponderada'] * weekday_merged_tid_periodo['count_y']/ weekday_merged_tid_periodo['count']
 
#Agrupo el valor final de cada tid para el periodo
weekday_grouped_sum_tid_periodo = weekday_merged_tid_periodo.groupby(['Corredor', 'tid', 'complete_name_x', 'Sentido_y'])['speed_ponderada_tid_periodo'].agg('sum').reset_index()
 




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

#--------

#-------------- Tablas para el modelo ---------------
#Definir rangos pico y placa

df_bitcarrier_mainroad_pico = df_bitcarrier_mainroad_weekday

df_bitcarrier_mainroad_pico.loc[(df_bitcarrier_mainroad['hour']>=6) & (df_bitcarrier_mainroad['hour']<=8) & (df_bitcarrier_mainroad['minute']<=30), 'PICO_PLACA']  = 'AM'
df_bitcarrier_mainroad_pico.loc[(df_bitcarrier_mainroad['hour']>=15) & (df_bitcarrier_mainroad['hour']<=19) & (df_bitcarrier_mainroad['minute']<=30), 'PICO_PLACA']  = 'PM'
df_bitcarrier_mainroad_pico.fillna(value = {'PICO_PLACA':'VALLE'}, inplace=True)

df_bitcarrier_mainroad_solopico = df_bitcarrier_mainroad_pico[df_bitcarrier_mainroad_pico['PICO_PLACA']!='VALLE'].reset_index()

#------------------------ Calcular velocidad ponderada por tid por fecha por pico y paca ------------------
df_bitcarrier_mainroad_solopico_count= df_bitcarrier_mainroad_solopico.groupby(['tid', 'PICO_PLACA','date'])['count'].agg('sum').reset_index()
weekday_picoplaca = df_bitcarrier_mainroad_solopico.merge(df_bitcarrier_mainroad_solopico_count, left_on=['tid', 'PICO_PLACA','date'], right_on=['tid', 'PICO_PLACA','date'])
weekday_picoplaca['vel_ponderada'] = weekday_picoplaca['count_x']* weekday_picoplaca['speed'] / weekday_picoplaca['count_y']
weekday_picoplaca_velpond = weekday_picoplaca.groupby(['PICO_PLACA','Corredor', 'tid', 'complete_name', 'Sentido', 'count_y','date'])['vel_ponderada'].agg('sum').reset_index()


#Mapas
 
#Load bitcarrier shape file
bitcarrier_shp = gpd.read_file('/content/drive/My Drive/Team 80 DS4A/Secretaría de Movilidad - SGV/Data_Final/Bitcarrier_5min/df_bctraveltimes_geom/df_bctraveltimes_geom.shp')
 
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



