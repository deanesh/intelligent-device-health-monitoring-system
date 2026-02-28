# layout.py
from dash import dcc, html
import dash_bootstrap_components as dbc

def get_layout():
    return dbc.Container([
        html.H1(
            "Intelligent Device Health Monitoring System",
            className="text-center my-4 text-primary"
        ),
        html.Hr(),

        # Auto-refresh interval
        dcc.Interval(id='refresh-interval', interval=60*1000, n_intervals=0),

        # Tabs
        dcc.Tabs(id="tabs", value='tab-overview', children=[
            dcc.Tab(label='Overview', value='tab-overview'),
            dcc.Tab(label='Country KPI', value='tab-country-kpi'),
            dcc.Tab(label='Assets', value='tab-assets'),
            dcc.Tab(label='Devices', value='tab-devices'),
            dcc.Tab(label='Interfaces', value='tab-interfaces'),
            dcc.Tab(label='Events', value='tab-events'),
        ]),

        html.Div(id='tabs-content', className="mt-3")
    ], fluid=True)