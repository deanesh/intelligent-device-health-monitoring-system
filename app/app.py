# app/app.py

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SERVICES_DIR = APP_DIR / "services"

# Add both folders to Python path
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(SERVICES_DIR))

from device_health_app import (
    load_orgs,
    load_assets,
    load_devices,
    load_interfaces,
    load_events,
    compute_device_health
)

from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Intelligent Device Health Monitoring"


def get_kpis(orgs, assets, devices, interfaces, events):
    return dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Organizations"),
                          dbc.CardBody(html.H4(len(orgs)))],
                         color="primary", inverse=True)),
        dbc.Col(dbc.Card([dbc.CardHeader("Assets"),
                          dbc.CardBody(html.H4(len(assets)))],
                         color="info", inverse=True)),
        dbc.Col(dbc.Card([dbc.CardHeader("Devices"),
                          dbc.CardBody(html.H4(len(devices)))],
                         color="success", inverse=True)),
        dbc.Col(dbc.Card([dbc.CardHeader("Interfaces"),
                          dbc.CardBody(html.H4(len(interfaces)))],
                         color="warning", inverse=True)),
        dbc.Col(dbc.Card([dbc.CardHeader("Events"),
                          dbc.CardBody(html.H4(len(events)))],
                         color="danger", inverse=True)),
    ])


app.layout = dbc.Container([
    html.H2("Intelligent Device Health Monitoring"),
    dcc.Tabs(id="tabs", value="overview", children=[
        dcc.Tab(label="Overview", value="overview"),
        dcc.Tab(label="Country KPI", value="country"),
        dcc.Tab(label="Devices", value="devices"),
        dcc.Tab(label="Events", value="events"),
    ]),
    html.Div(id="content")
], fluid=True)


@app.callback(Output("content", "children"),
              Input("tabs", "value"))
def render(tab):

    orgs = load_orgs()
    assets = load_assets()
    devices = load_devices()
    interfaces = load_interfaces()
    events = load_events()

    if "country" not in orgs.columns:
        orgs["country"] = "Unknown"

    assets = assets.merge(
        orgs[["organization_id", "country"]],
        on="organization_id",
        how="left"
    )

    devices = devices.merge(
        assets[["asset_id", "country"]],
        on="asset_id",
        how="left"
    )

    devices["country"] = devices["country"].fillna("Unknown")

    health_status, health_counts = compute_device_health(devices, events)

    kpis = get_kpis(orgs, assets, devices, interfaces, events)

    # ---------------- OVERVIEW ----------------
    if tab == "overview":

        fig = go.Figure(data=[
            go.Bar(name="Critical", x=["Devices"],
                   y=[health_counts["Critical"]],
                   marker_color="red"),
            go.Bar(name="Warning", x=["Devices"],
                   y=[health_counts["Warning"]],
                   marker_color="orange"),
            go.Bar(name="Healthy", x=["Devices"],
                   y=[health_counts["Healthy"]],
                   marker_color="green"),
        ])

        fig.update_layout(barmode="stack",
                          title="Device Health Overview")

        return html.Div([kpis, dcc.Graph(figure=fig)])

    # ---------------- COUNTRY KPI ----------------
    elif tab == "country":

        df = pd.DataFrame({
            "Organizations": orgs.groupby("country")["organization_id"].nunique(),
            "Assets": assets.groupby("country")["asset_id"].nunique(),
            "Devices": devices.groupby("country")["device_id"].nunique(),
        }).fillna(0).reset_index()

        return html.Div([
            kpis,
            dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10
            )
        ])

    # ---------------- DEVICES ----------------
    elif tab == "devices":

        devices["HealthStatus"] = devices["device_id"].map(health_status)

        return html.Div([
            kpis,
            dash_table.DataTable(
                data=devices.to_dict("records"),
                columns=[{"name": i, "id": i} for i in devices.columns],
                page_size=10
            )
        ])

    # ---------------- EVENTS (NEW) ----------------
    elif tab == "events":

        # Optional: sort latest events first if timestamp exists
        if "timestamp" in events.columns:
            events = events.sort_values(by="timestamp", ascending=False)

        return html.Div([
            kpis,
            dash_table.DataTable(
                data=events.to_dict("records"),
                columns=[{"name": i, "id": i} for i in events.columns],
                page_size=15,
                style_table={"overflowX": "auto"}
            )
        ])


if __name__ == "__main__":
    app.run(debug=True)