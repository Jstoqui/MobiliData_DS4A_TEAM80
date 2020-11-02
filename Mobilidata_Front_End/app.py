import dash
import dash_bootstrap_components as dbc

external_scripts = [
    {
        'src': '/assets/lib/jquery/jquery.min.js'
    },
    {
        'src': '/assets/lib/jquery/jquery-migrate.min.js'
    },
    {
        'src': '/assets/lib/bootstrap/js/bootstrap.bundle.min.js'
    },
    {
        'src': '/assets/lib/easing/easing.min.js'
    },
    {
        'src': '/assets/lib/mobile-nav/mobile-nav.js'
    },
    {
        'src': '/assets/lib/wow/wow.min.js'
    },
    {
        'src': '/assets/lib/waypoints/waypoints.min.js'
    },
    {
        'src': '/assets/lib/counterup/counterup.min.js'
    },
    {
        'src': '/assets/lib/owlcarousel/owl.carousel.min.js'
    },
    {
        'src': '/assets/lib/isotope/isotope.pkgd.min.js'
    },
    {
        'src': '/assets/lib/lightbox/js/lightbox.min.js'
    },
    {
        'src': '/assets/js/main.js'
    }        
]


external_stylesheets = [
    {
        'href': '/assets/img/favicon.png',
        'rel': 'icon'
    },
    {
        'href': 'https://fonts.googleapis.com/css?family=Open+Sans:300,300i,400,400i,700,700i|Montserrat:300,400,500,700',
        'rel': 'stylesheet'
    },
    {
        'href': '/assets/lib/bootstrap/css/bootstrap.min.css',
        'rel': 'stylesheet'
    },
    {
        'href': '/assets/lib/font-awesome/css/font-awesome.min.css',
        'rel': 'stylesheet'
    },
    {
        'href': '/assets/lib/animate/animate.min.css',
        'rel': 'stylesheet'
    },    
    {
        'href': '/assets/lib/ionicons/css/ionicons.min.css',
        'rel': 'stylesheet'
    },
    {
        'href': '/assets/lib/owlcarousel/assets/owl.carousel.min.css',
        'rel': 'stylesheet'
    },
    {
        'href': '/assets/lib/lightbox/css/lightbox.min.css',
        'rel': 'stylesheet'
    },
    {
        'href': '/assets/css/style.css',
        'rel': 'stylesheet'
    },            
]

# bootstrap theme
# https://bootswatch.com/lux/
#external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)
app.title = 'Mobilidata App'

server = app.server
app.config.suppress_callback_exceptions = True


#app = dash.Dash(__name__, suppress_callback_exceptions=True)
#server = app.server