# app.py
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from services.device_health_app import (
    get_dashboard_counts,
    get_device_health_overview,
    get_anomalies_table,
    get_alerts_list,
    get_org_kpi_table
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Intelligent Device Health Dashboard"

app.layout = dbc.Container([
    html.H1("Intelligent Device Health Monitoring", className="text-center my-3"),

    # KPI cards
    dbc.Row(id="kpi-cards", className="mb-2", justify="start"),

    # Tabs row
    dbc.Row([
        dbc.Col(dcc.Tabs(id="tabs", value='tab-overview', children=[
            dcc.Tab(label='Device Health Overview', value='tab-overview'),
            dcc.Tab(label='Anomalies', value='tab-anomalies'),
            dcc.Tab(label='Organizations KPI', value='tab-org-kpi'),
            dcc.Tab(label='Events', value='tab-alerts')
        ]), width=12)
    ], className="mb-3"),

    # Tabs content
    html.Div(id="tabs-content"),

    # Auto-refresh
    dcc.Interval(id='refresh-interval', interval=60*1000, n_intervals=0)
], fluid=True)

# --- KPI cards ---
@app.callback(Output("kpi-cards", "children"), Input("refresh-interval", "n_intervals"))
def update_kpi(n):
    counts = get_dashboard_counts()
    kpi_style = {"font-size": "0.85rem", "margin": "0.1rem 0"}
    return [
        dbc.Col(dbc.Card([dbc.CardHeader("Organizations"), dbc.CardBody(html.P(counts["orgs"], style=kpi_style))],
                         color="primary", inverse=True), width="auto"),
        dbc.Col(dbc.Card([dbc.CardHeader("Assets"), dbc.CardBody(html.P(counts["assets"], style=kpi_style))],
                         color="info", inverse=True), width="auto"),
        dbc.Col(dbc.Card([dbc.CardHeader("Devices"), dbc.CardBody(html.P(counts["devices"], style=kpi_style))],
                         color="success", inverse=True), width="auto"),
        dbc.Col(dbc.Card([dbc.CardHeader("Interfaces"), dbc.CardBody(html.P(counts["interfaces"], style=kpi_style))],
                         color="warning", inverse=True), width="auto"),
    ]

# --- Tabs content ---
@app.callback(Output("tabs-content", "children"),
              [Input("tabs", "value"), Input("refresh-interval", "n_intervals")])
def update_tabs(tab, n):
    if tab == "tab-overview":
        return html.Div([
            html.H5("Device Health Overview"),
            dcc.Graph(figure=get_device_health_overview())
        ])
    elif tab == "tab-anomalies":
        table_header = [html.Thead(html.Tr([html.Th(col) for col in ["Device", "Metric", "Value", "Status"]]))]
        table_body = html.Tbody(get_anomalies_table())
        return html.Table(table_header + [table_body], className="table table-striped table-sm")
    elif tab == "tab-org-kpi":
        table_header = [html.Thead(html.Tr([html.Th("Organization"), html.Th("Assets"), html.Th("Devices")]))]
        table_body = html.Tbody(get_org_kpi_table())
        return html.Table(table_header + [table_body], className="table table-striped table-sm")
    elif tab == "tab-alerts":
        table_header = [html.Thead(html.Tr([html.Th("Device ID"), html.Th("IP Address"), html.Th("Message")]))]
        table_body = html.Tbody(get_alerts_list())
        return html.Table(table_header + [table_body], className="table table-striped table-sm")
    return html.P("Tab not found")

if __name__ == "__main__":
    app.run(debug=True)