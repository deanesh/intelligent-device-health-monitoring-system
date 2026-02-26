from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc

# Import functions from device_health_app
from services.device_health_app import (
    get_device_health_overview,
    get_anomalies_table,
    get_alerts_list,
    get_logs_list
)

# -------------------------------
# Initialize Dash app
# -------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Intelligent Device Health Monitoring Dashboard"

# -------------------------------
# Layout
# -------------------------------
app.layout = dbc.Container([
    html.H1("Intelligent Device Health Monitoring Dashboard", className="text-center my-4"),
    
    # Interval component for auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 seconds
        n_intervals=0
    ),

    # Tabs
    dcc.Tabs(id="tabs", value='tab-overview', children=[
        dcc.Tab(label='Overview', value='tab-overview'),
        dcc.Tab(label='Anomalies', value='tab-anomalies'),
        dcc.Tab(label='Alerts', value='tab-alerts'),
        dcc.Tab(label='Logs', value='tab-logs')
    ], className="mb-3"),

    # Tab content
    html.Div(id='tabs-content')
], fluid=True)

# -------------------------------
# Callbacks
# -------------------------------
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('interval-component', 'n_intervals')
)
def render_tab_content(tab, n_intervals):
    """
    Render the content for each tab and auto-refresh every interval.
    """
    if tab == 'tab-overview':
        # Device Health Overview
        return dbc.Row([
            dbc.Col(dcc.Graph(figure=get_device_health_overview()), width=12)
        ])
    
    elif tab == 'tab-anomalies':
        # Anomalies Table
        table_header = [
            html.Thead(html.Tr([html.Th(col) for col in ["Device", "Metric", "Value", "Status"]]))
        ]
        table_body = html.Tbody(get_anomalies_table())
        return dbc.Row([
            dbc.Col(html.Table(table_header + [table_body], className="table table-striped"), width=12)
        ])
    
    elif tab == 'tab-alerts':
        # Alerts List
        alerts = get_alerts_list()
        return dbc.Row([
            dbc.Col([
                html.H5("Latest Alerts"),
                html.Ul(alerts)
            ], width=12)
        ])
    
    elif tab == 'tab-logs':
        # Logs List
        logs = get_logs_list()
        return dbc.Row([
            dbc.Col([
                html.H5("System Logs (latest 20)"),
                html.Ul(logs)
            ], width=12)
        ])
    
    else:
        return html.P("Tab not found.")

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)