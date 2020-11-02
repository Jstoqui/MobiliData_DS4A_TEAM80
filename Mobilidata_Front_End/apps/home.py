import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

#Create Layout
layout = html.Div(style={'background-image':'url(/assets/img/fondo5.png)'},children=[
    #html.Link(href="img/favicon.png",rel="icon"),
   html.Section(className="clearfix",id="intro", children=[
        html.Div(className='container',children=[
            html.Div(className="intro-img",children=[
                #html.Img(src="/assets/img/LogoM7.svg",className='img-fluid')
                html.Img(src="/assets/img/MobilidataS2.png",className='img-fluid')
            ]),
            html.Div(className="intro-info",children=[
                html.H2(["We are",html.Br(), html.Span("MobiliData"),html.Br(),"Team 80 DS4A v3"]),
                html.Div(children=[
                    html.A("Team Members",href="#team",className="btn-get-started scrollto")
                ])
            ])
        ])
    ]),    
    html.Section( className="about",children=[
        html.Div( className="container",children=[
            html.Header(className="section-header", children=[
                #html.H3('Bogotá fluye inteligentemente'),
                html.H3('Bogotá flows Smartly'),
                #html.P('La movilidad de la capital desde los datos (análisis y modelos)')
                html.P('The mobility of the capital watched from data (analysis and models)')
            ]),
            html.Div(className="row about-container",children=[
                html.Div(className="col-lg-6 content order-lg-1 order-2", children=[
                    html.P("Mobility in large cities is part of the problems that currently afflict the population, this application provides information on 3 key indicators implemented by the Secretaría de Movilidad to define actions and programs that allow knowing and improving mobility in the city of Bogotá."),
                    html.Div(className="icon-box wow fadeInUp",children=[
                        html.Div(className="icon",children=[
                            #html.I(className="fa fa-shopping-bag")
                        ]),
                        html.H4(className="title",children=[
                            #html.A("Siniestralidad")
                            html.A("Claims")

                        ]),
                        html.P("It corresponds to the set of accidents, claims and the road actors involved, additionally there is demographic information.",className="description")
                    ]),
                    html.Div(className="icon-box wow fadeInUp",children=[
                        html.Div(className="icon",children=[
                            #html.I(className="fa fa-photo")
                            # html.Img(src="/assets/img/testimonial-4.jpg", className="testimonial-img", alt="")
                        ]),
                        html.H4(className="title",children=[
                            #html.A("Velocidades")
                            html.A("Speed")
                        ]),
                        html.P("Information corresponding to the speeds registered with bitcarrier technology in the main road corridors of the city." )
                    ]),
                    html.Div(className="icon-box wow fadeInUp",children=[
                        html.Div(className="icon",children=[
                            #html.I(className="fa fa-photo")
                            # html.Img(src="/assets/img/testimonial-4.jpg", className="testimonial-img", alt="")
                        ]),
                        html.H4(className="title",children=[
                            #html.A("Volumenes")
                            html.A("Volumes")
                        ]),
                        html.P("Data registered in specific places in the city, corresponding to the number of vehicles by time intervals, classified according to their category." )
                    ])
                ]),
                html.Div(className="col-lg-6 background order-lg-2 order-1 wow fadeInUp", children=[
                    html.Img(src="/assets/img/mapa3.png",className="img-fluid")
                ])
            ])
        ])
    ]),
#    html.Section(className="section-bg",id="clients", children=[
    html.Section(className="wow fadeIn", id="why-us", children=[       
        dbc.Container( children=[
            html.Header(className="section-header", children=[
                #html.H3('Bogotá fluye inteligentemente'),
                html.H3('All about this project '),
                #html.P('La movilidad de la capital desde los datos (análisis y modelos)')
                html.P('Check up all the information and the codes that was made for this project')
            ]),
            html.Div(className="row row-eq-height justify-content-center",children=[
                html.Div(className="col-lg-4 mb-4",children=[
                    html.Div(className="card wow bounceInUp", children=[
                        html.I(className="fa fa-google"),
                        html.Div(className="card-body",children=[
                            html.H5("Read the detail documentation about the project",className="card-title"),
                            #html.P("aqui toca escribir algo",className="card-title"),
                            dbc.Button("Drive", href="", color="primary", className="mt-3")
                        ])                        
                    ])
                ]),
                html.Div(className="col-lg-4 mb-4",children=[
                    html.Div(className="card wow bounceInUp", children=[
                        html.I(className="fa fa-github"),
                        html.Div(className="card-body",children=[
                            html.H5("Access the code used to build this App",className="card-title"),
                            #html.P("aqui toca escribir algo",className="card-title"),
                            dbc.Button("GitHub", href="https://github.com", color="primary", className="mt-3")
                        ])                        
                    ])
                ]),
                html.Div(className="col-lg-4 mb-4",children=[
                    html.Div(className="card wow bounceInUp", children=[
                        html.I(className="fa fa-youtube"),
                        html.Div(className="card-body",children=[
                            html.H5("Watch the Youtube video lecture about the App",className="card-title"),
                            #html.P("aqui toca escribir algo",className="card-title"),
                            dbc.Button("Video", href="https://youtube.com", color="primary", className="mt-3")
                        ])                        
                    ])
                ])                                
            ]),
            html.Div(className="row counters",children=[
                html.Div(className="col-lg-3 col-6 text-center",children=[
                    html.Span("7",style={'data-toogle':'counter-up'}),
                    #html.Span("274",toogle='counter-up'),
                    html.P("Members")
                ]),
                html.Div(className="col-lg-3 col-6 text-center",children=[
                    html.Span("1",style={'data-toogle':'counter-up'}),
                    #html.Span("274",toogle='counter-up'),
                    html.P("Project")
                ]),                
                html.Div(className="col-lg-3 col-6 text-center",children=[
                    html.Span("12",style={'data-toogle':'counter-up'}),
                    #html.Span("274",toogle='counter-up'),
                    html.P("Weeks")
                ]),
                html.Div(className="col-lg-3 col-6 text-center",children=[
                    html.Span("1300",style={'data-toogle':'counter-up'}),
                    #html.Span("274",toogle='counter-up'),
                    html.P("Hard work Hours")
                ])                                
            ])            
        ])
    ]),
    html.Section(id='team',children=[
        html.Div(className="container",children=[
            html.Div(className="section-header", children=[
                html.H3('Team Members'),
                html.P("Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque")
            ]),
            html.Div(className="row seven cols", children=[
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/Hector.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Hector Florez'),
                                html.Span('team'),
                                html.Div(className="social",children=[
                                    html.A(href="",children=[
                                        html.I(className="fa fa-linkedin")
                                    ])
                                ])
                            ])
                        ])
                    ])                
                ]),
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/Johan.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Johan Quiroga'),
                                html.Span('Chief Executive Officer'),
                                html.Div(className="social",children=[
                                    html.A(href="https://www.linkedin.com/in/jsquirogacloudanalyst/",children=[
                                        html.I(className="fa fa-linkedin")
                                    ]),
                                    html.A(href="https://www.facebook.com/johan.sebastian.92775/",children=[
                                        html.I(className="fa fa-facebook")
                                    ]),
                                ])
                            ])
                        ])
                    ])                
                ]),
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/Marcela.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Marcela Garzon'),
                                html.Span('team'),
                                html.Div(className="social",children=[
                                    html.A(href="",children=[
                                        html.I(className="fa fa-linkedin")
                                    ])
                                ])
                            ])
                        ])
                    ])                
                ]),
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/Monica.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Mónica Otálora'),
                                html.Span('team'),
                                html.Div(className="social",children=[
                                    html.A(href="",children=[
                                        html.I(className="fa fa-linkedin")
                                    ])
                                ])
                            ])
                        ])
                    ])                
                ]),
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/Nicolas.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Nicolas Róldan'),
                                html.Span('team'),
                                html.Div(className="social",children=[
                                    html.A(href="",children=[
                                        html.I(className="fa fa-linkedin")
                                    ])
                                ])
                            ])
                        ])
                    ])                
                ]),
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/Sheijer2.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Sheijer Silva'),
                                html.Span('Team'),
                                html.Div(className="social",children=[
                                    html.A(href="",children=[
                                        html.I(className="fa fa-linkedin")
                                    ])
                                ])
                            ])
                        ])
                    ])                
                ]),
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/Vicente.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Vicente Castro'),
                                html.Span('Team'),
                                html.Div(className="social",children=[
                                    html.A(href="",children=[
                                        html.I(className="fa fa-linkedin")
                                    ])
                                ])
                            ])
                        ])
                    ])                
                ]),
                html.Div( className="col-lg-3 col-md-3 wow fadeInUp", children=[
                    html.Div(className='member', children=[
                        html.Img(src="/assets/img/TAS.jpg",className="img-fluid"),
                        html.Div(className="member-info", children=[
                            html.Div(className="member-info-content", children=[
                                html.H4('Nicolas/Karen'),
                                html.Span('Teacher Asistants'),
                                html.Div(className="social",children=[
                                    html.A(href="",children=[
                                        html.I(className="fa fa-linkedin")
                                    ])
                                ])
                            ])
                        ])
                    ])                
                ]),                                                                                                  
            ])
        ])
    ]),
    html.Footer(id="footer",children=[
        html.Div(className="container",children=[   
            html.Div(className='copyright',children=[
                html.P(["Copyright ",html.Strong('MobiliData',"All Rights Reserved")])
             ])
        ])
    ])



    #html.H1("Bienvenidos team 80", id='title'), #Creates the title of the app
    #html.H2("Esta es la pagina final", id='Subtitle'),
])

