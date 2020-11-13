import numpy as np

def get_lat_long(direcccion, all_locations_dict):
    '''
    Retorna las coordenadas como floats.

    INPUT:
    direccion: ubicación del registro
    all_locations_dict: diccionario con las coordenadas.
    '''
    coords = all_locations_dict.get(direcccion)
    lat, lon = coords.split(";")
    return float(lat), float(lon)

def get_all_lat_long(all_lat_lon):
    '''
        Retorna 2 listas representando la latitud y longitud con todas las coordenadas del mapa.
        
        INPUTS:
        all_lat_long: lista con todas las coordenadas en un formato lat;lon
    '''
    lat_list = []
    long_list = []
    for lat_long in all_lat_lon:
        lat_list.append(lat_long.split(";")[0])
        long_list.append(lat_long.split(";")[1])
    return lat_list, long_list

def fix_hours(hour):
    '''
    Realiza un padding de ceros a una hora. Función helper para el slider.

    INPUTS:
    hour: Hora del día. (ejemplo: 05:00 se recibe como 500)
    '''
    hour = hour.rjust(4,"0")
    hour = hour[0:2] + ":" + hour[2::]
    return hour

def get_round_hours(hours):
    '''
    Retorna todas las horas en punto (ejemplo, 5:00, 6:00, etc)

    INPUT:
    hours: lista con todas los momentos únicos horarios del dataset.
    '''
    return [hour for hour in hours if hour.endswith("00")]



def get_hour_with_max_volume(df, fecha, init, final):
    all_hour_ranges = []
    all_meditions = []
    while init < final:
        # print(df_monitoreo[(df_monitoreo["PERIODO"] >= init) & (df_monitoreo["PERIODO"] <= init+100) & (df_monitoreo["FECHA"] == fecha)])
        all_meditions.append(df[(df["PERIODO"] >= init) & (df["PERIODO"] <= init+100) & (df["FECHA"] == fecha)]["TOTAL VOLUME"].median())
        all_hour_ranges.append("{}-{}".format(init, init+100))
        init += 100
    hour_with_max_volume = all_hour_ranges[np.argmax(all_meditions)]
    return hour_with_max_volume