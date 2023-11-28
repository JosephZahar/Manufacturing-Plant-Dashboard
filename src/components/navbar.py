from dash import html
import dash_bootstrap_components as dbc

# Define the navbar structure
def Navbar():
    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.Button("Process Overview", href="/Composition", id="Composition", color="outline-secondary", className="mr-5")),
                dbc.NavItem(dbc.Button("Root Cause Analysis", href="/Comparative", id="Comparative", color="outline-secondary")),
            ],
            brand="Onsite Interviews Pre-Assessment - Intuitive",
            brand_href="/Composition",
            id="navbar",
            color="#072B54",
            dark=True,
        ),
    ])

    return layout


