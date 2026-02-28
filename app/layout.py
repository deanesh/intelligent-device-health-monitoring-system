from dash import dcc, html
import dash_bootstrap_components as dbc

def get_layout():
    return dbc.Container([
        html.H1("Intelligent Device Health Monitoring System", className="text-center my-4 text-primary"),
        html.Hr(),
        # Auto-refresh
        dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0),
        # Tabs
        dcc.Tabs(id="tabs", value='tab-overview', children=[
            dcc.Tab(label='Overview', value='tab-overview', children=[]),
            dcc.Tab(label='Organizations', value='tab-org', children=[]),
            dcc.Tab(label='Assets', value='tab-assets', children=[]),
            dcc.Tab(label='Devices', value='tab-devices', children=[]),
            dcc.Tab(label='Interfaces', value='tab-interfaces', children=[]),
            dcc.Tab(label='Events', value='tab-events', children=[]),
        ]),
        html.Div(id='tabs-content', className="mt-3")
    ], fluid=True)