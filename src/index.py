from dash import html, dcc, Dash
from dash.dependencies import Input, Output

# Connect to your src pages
from src.pages import Composition, Comparative
import dash_bootstrap_components as dbc

# Connect the navbar to the index
from src.components import navbar
from src.pages.Comparative import comparative_dash
from src.pages.Composition import composition_dash


import pathlib
# Define the navbar
nav = navbar.Navbar()

app = Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=0.7"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Define the index page layout
app.layout = html.Div(id='body', className='fullscreen', children=[
    dcc.Location(id='url', refresh=False),
    nav,
    html.Div(id='page-content', children=[]),
])


@app.callback(
    [Output("Composition", "color"),
     Output("Comparative", "color")],
    [Input('url', 'pathname')]
)
def update_button_color(pathname):
    if pathname == '/Composition':
        return "light", "outline-secondary"
    elif pathname == '/Comparative':
        return "outline-secondary", "light"
    else:
        return "light", "outline-secondary"


# Create the callback to handle mutlipage inputs
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Composition':
        return Composition.layout
    if pathname == '/Comparative':
        return Comparative.layout
    else:
        return Composition.layout


fig1, fig2, fig3 = composition_dash()

@app.callback([Output(component_id="fig1d", component_property="figure"),
               Output(component_id="fig2d", component_property="figure"),
               Output(component_id="fig3d", component_property="figure"),
               Output(component_id="fig4d", component_property="figure"),
               Output(component_id="fig5d", component_property="figure")],
              [Input(component_id="line_namee", component_property="value")])
def callback_function(line_number):
    fig1, fig2, fig3, fig4, fig5 = comparative_dash(line_number)
    return fig1, fig2, fig3, fig4, fig5


# Run the src on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=True)

