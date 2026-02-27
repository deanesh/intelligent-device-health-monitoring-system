# app.py
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from services.device_health_app import (
    get_dashboard_counts,
    get_device_health_overview,
    get_anomalies_table,
    load_orgs,
    load_assets,
    load_devices
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
            dcc.Tab(label='Anomalies', value='tab-anomalies'),
            dcc.Tab(label='Organizations KPI', value='tab-org-kpi')
        ]), width=6)  # Reduced width for cleaner look
    ], className="mb-3"),

    # Tabs content
    html.Div(id="tabs-content"),

    # Auto-refresh interval
    dcc.Interval(id='refresh-interval', interval=60*1000, n_intervals=0)
], fluid=True)

# KPI cards callback (top dashboard)
@app.callback(Output("kpi-cards", "children"), Input("refresh-interval", "n_intervals"))
def update_kpi(n):
    counts = get_dashboard_counts()
    kpi_style = {"font-size": "0.85rem", "margin": "0.1rem 0"}  # smaller font and margin
    return [
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader("Organizations"), dbc.CardBody(html.P(counts["orgs"], style=kpi_style))],
                color="primary", inverse=True
            ), width="auto"
        ),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader("Assets"), dbc.CardBody(html.P(counts["assets"], style=kpi_style))],
                color="info", inverse=True
            ), width="auto"
        ),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader("Devices"), dbc.CardBody(html.P(counts["devices"], style=kpi_style))],
                color="success", inverse=True
            ), width="auto"
        ),
        dbc.Col(
            dbc.Card(
                [dbc.CardHeader("Interfaces"), dbc.CardBody(html.P(counts["interfaces"], style=kpi_style))],
                color="warning", inverse=True
            ), width="auto"
        ),
    ]

# Tabs content callback
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"), Input("refresh-interval", "n_intervals")]
)
def update_tabs(tab, n):
    if tab == "tab-overview":
        return html.Div([
            html.H5("Device Health Overview"),
            dcc.Graph(figure=get_device_health_overview())
        ])
    
    elif tab == "tab-anomalies":
        table_header = [html.Thead(html.Tr([html.Th(col) for col in ["Device", "Metric", "Value", "Status"]]))]
        table_body = html.Tbody(get_anomalies_table())
        return html.Table(table_header + [table_body], className="table table-striped table-sm")  # compact table

    elif tab == "tab-org-kpi":
        orgs = load_orgs()
        assets = load_assets()
        devices = load_devices()

        kpi_cards = []
        for _, org in orgs.iterrows():
            org_id = org.get("organization_id")
            org_name = org.get("name", "Unknown Org")
            org_assets = len(assets[assets["organization_id"] == org_id])
            org_devices = len(devices[devices["organization_id"] == org_id])

            kpi_cards.append(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(org_name),
                        dbc.CardBody([
                            html.P(f"Assets: {org_assets}", style={"margin": "0.2rem 0", "font-size": "0.9rem"}),
                            html.P(f"Devices: {org_devices}", style={"margin": "0.2rem 0", "font-size": "0.9rem"})
                        ])
                    ], color="secondary", inverse=True),
                    width="auto"
                )
            )
        return dbc.Row(kpi_cards, className="mb-2")

    return html.P("Tab not found")

if __name__ == "__main__":
    app.run(debug=True)