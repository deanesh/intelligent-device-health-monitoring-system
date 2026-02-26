from dash import dcc, html

def get_layout():
    return html.Div([
        html.H2("Intelligent Device Health Monitoring Dashboard", style={'textAlign': 'center'}),
        dcc.Tabs(id="tabs", value='tab-overview', children=[
            dcc.Tab(label='Overview', value='tab-overview'),
            dcc.Tab(label='Anomalies', value='tab-anomalies'),
            dcc.Tab(label='Alerts', value='tab-alerts'),
            dcc.Tab(label='Logs', value='tab-logs')
        ]),
        html.Div(id='tabs-content', style={'marginTop': '20px'}),
        # Auto-refresh every 120 seconds
        dcc.Interval(id='refresh-interval', interval=120*1000, n_intervals=0)
    ])