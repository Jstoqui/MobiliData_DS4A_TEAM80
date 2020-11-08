import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


def multiLine(df, tipology, direccion, hora):
    '''
    Genera un figure de los volumenes a lo largo de un día
    por tipologia, dirección y rango horario, esto para todos
    los días disponibles para la fecha escogida.

    INPUTS
    df: dataframe con los datos de monitoreo.
    tipology: tipologia vehicular
    direccion: ubicación donde se registraron los datos.
    hora: Rango de horas para limitar el x_axes.
    '''
    all_registered_dates_monitoring = df["FECHA"].astype(str).unique()
    # for each date
    all_plots = []
    for d in all_registered_dates_monitoring:
        df_filt = df[ (df["FECHA"].astype(str) == d) & (df["DIRECCION CATASTRO"] == direccion) ]
        all_plots.append(go.Scatter(x=df_filt["PERIODO"], y=df_filt[tipology], mode="lines", name=d))

    layout = go.Layout(title="Vehicles Volume in all registered dates", xaxis={"title": "Hour of day"})

    fig = go.Figure(
        data=all_plots,
        layout=layout
    )
    fig.update_xaxes(
        range=(hora[0], hora[1])
    )
    return fig


# def staked_by_topology_plotly(df_volumes, d):
#     '''
#     Genera un stacked area plot por 
#     '''
#     tipologies = ["LIVIANOS", "INTERMUNICIPALES", "BUSES", "MOTOS", "BICICLETAS CALZADA", "C2 C3", ">=C4"]

#     df_filt = df_volumes[df_volumes["FECHA"].astype(str) == d]
#     total_vehicles_per_hour = df_filt[tipologies].sum(axis=1)
#     data = []
#     for i in tipologies:
#         data.append( go.Bar(name=i, x=df_filt["PERIODO"], y=(df_filt[i]/total_vehicles_per_hour)) )

#     layout = go.Layout(
#         title="Proportion of vehicles by tologies along a day for {}".format(d),
#         xaxis={"title": "Hour of day"},
#         yaxis={"title": "Proportion"}  
#     )

#     fig = go.Figure(data=data, layout=layout)
#     fig.update_layout(barmode='stack')
#     return fig


def staked_plot_by_topology_plotly(df_volumes, fecha, direccion, hora):
    '''
    Genera un stacked area plot para todas las tipologias en una fecha
    especifica, dirección y rango horario.

    INPUTS
    df_volumes: dataframes con los datos de monitoreo.
    fecha: fecha en la cuál se registraron los datos.
    direccion: ubicación donde se registraron los datos.
    hora: Rango de horas para limitar el x_axes.
    '''

    tipologies = ["LIVIANOS", "INTERMUNICIPALES", "BUSES", "MOTOS", "BICICLETAS CALZADA", "C2 C3", ">=C4"]


    df_filt = df_volumes[(df_volumes["FECHA"].astype(str) == fecha) & (df_volumes["DIRECCION CATASTRO"] == direccion)]
    total_vehicles_per_hour = df_filt[tipologies].sum(axis=1)

    layout = go.Layout(title="Proportion of vehicules by tologies along a day for {}".format(fecha), xaxis={"title": "Hour of day"})
    fig = go.Figure(layout=layout)
    for i in tipologies:
        fig.add_trace(go.Scatter(name=i, x=df_filt["PERIODO"], y=(df_filt[i]/total_vehicles_per_hour), mode="lines", stackgroup="one"))


    fig.update_xaxes(
        range=(hora[0], hora[1])
    )
    return fig


def kpi_component(header, body, id_header, id_body, color):
    '''
    Genera un card para mostrar los KPI.

    INPUTS
    header: header del card
    body: body del card
    id_header: id del header
    id_body: id del body
    color: color deseado para el card
    '''
    card_content = [
        dbc.CardHeader(header, id=id_header),
        dbc.CardBody(html.H2(body, id=id_body, className="card-title")),
    ]
    return dbc.Card(card_content, color=color, inverse=True,className="card wow bounceInUp")
 

def bogota_map(mapa, lat, lon, mapbox_token):
    '''
    Retorna el mapa de Bogotá.

    INPUTS:
    mapa: scattermapbox con todas las localizaciones registradas.
    lat: latitud del centro
    lon: longitud del centro
    mapbox_token: access token de mapbox.
    '''
    fig = go.Figure()
    fig.add_trace(mapa)
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_token,
            bearing=0,
            center=dict(
                lat=lat,
                lon=lon
            ),
            pitch=0,
            zoom=16,
            style='outdoors'
        )
    )
    return fig