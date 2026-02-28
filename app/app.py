# app.py
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.device_health_app import load_orgs, load_assets, load_devices, load_interfaces, load_events

# ------------------------
# Initialize app
# ------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Intelligent Device Health Monitoring Dashboard"

# ------------------------
# Layout
# ------------------------
app.layout = dbc.Container([
    html.H1("Intelligent Device Health Monitoring", className="text-center my-3"),

    # Tabs row
    dbc.Row([dbc.Col(dcc.Tabs(id="tabs", value='tab-overview', children=[
        dcc.Tab(label='Overview', value='tab-overview'),
        dcc.Tab(label='Country KPI', value='tab-country-kpi'),
        dcc.Tab(label='Assets', value='tab-assets'),
        dcc.Tab(label='Devices', value='tab-devices'),
        dcc.Tab(label='Interfaces', value='tab-interfaces'),
        dcc.Tab(label='Events', value='tab-events'),
    ]), width=12)], className="mb-3"),

    # Tabs content
    html.Div(id="tabs-content"),

    # Auto-refresh every 60 seconds
    dcc.Interval(id='refresh-interval', interval=60*1000, n_intervals=0)
], fluid=True)


# ------------------------
# Helper functions
# ------------------------
def get_top_countries(df, col='country', top_n=10):
    if df.empty or col not in df.columns:
        return df
    top = df[col].value_counts().nlargest(top_n).index
    return df[df[col].isin(top)]


def get_kpi_cards(orgs, assets, devices, interfaces, events):
    kpi_style = {"font-size": "0.85rem", "margin": "0.1rem 0"}
    return dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Organizations"), dbc.CardBody(html.P(len(orgs), style=kpi_style))],
                         color="primary", inverse=True), width="auto"),
        dbc.Col(dbc.Card([dbc.CardHeader("Assets"), dbc.CardBody(html.P(len(assets), style=kpi_style))],
                         color="info", inverse=True), width="auto"),
        dbc.Col(dbc.Card([dbc.CardHeader("Devices"), dbc.CardBody(html.P(len(devices), style=kpi_style))],
                         color="success", inverse=True), width="auto"),
        dbc.Col(dbc.Card([dbc.CardHeader("Interfaces"), dbc.CardBody(html.P(len(interfaces), style=kpi_style))],
                         color="warning", inverse=True), width="auto"),
        dbc.Col(dbc.Card([dbc.CardHeader("Events"), dbc.CardBody(html.P(len(events), style=kpi_style))],
                         color="danger", inverse=True), width="auto"),
    ])


# ------------------------
# Single callback for tabs-content
# ------------------------
@app.callback(Output("tabs-content", "children"),
              [Input("tabs", "value"), Input("refresh-interval", "n_intervals")])
def update_tabs(tab, n):

    # --- Load all data ---
    orgs = load_orgs()        # must have 'organization_id', 'name', 'country'
    assets = load_assets()    # 'asset_id', 'organization_id'
    devices = load_devices()  # 'device_id', 'asset_id', 'device_class_id', etc.
    interfaces = load_interfaces()  # 'interface_id', 'device_id'
    events = load_events()    # 'event_id', 'device_id', 'interface_id'

    # --- Merge country info everywhere ---
    assets = assets.merge(orgs[['organization_id', 'country']], on='organization_id', how='left')
    devices = devices.merge(assets[['asset_id', 'country']], on='asset_id', how='left')
    interfaces = interfaces.merge(devices[['device_id', 'country']], on='device_id', how='left')
    events = events.merge(devices[['device_id', 'country']], on='device_id', how='left')

    # --- Compute stored vs actual counts ---
    assets['num_devices'] = devices.groupby('asset_id')['device_id'].transform('count').fillna(0)
    devices['num_interfaces'] = interfaces.groupby('device_id')['interface_id'].transform('count').fillna(0)
    interfaces['num_events'] = events.groupby('interface_id')['event_id'].transform('count').fillna(0)

    # --- KPI cards ---
    kpi_row = get_kpi_cards(orgs, assets, devices, interfaces, events)

    tab_content = html.P("No data available")

    try:
        # -------------------- Overview --------------------
        if tab == "tab-overview":
            avg_health = devices['health_score'].mean() if 'health_score' in devices.columns else 0
            fig_health = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=avg_health,
                delta={'reference': 80},
                title={'text': "Overall Device Health"},
                gauge={'axis': {'range': [0, 100]},
                       'steps': [{'range': [0, 50], 'color': 'red'},
                                 {'range': [50, 80], 'color': 'orange'},
                                 {'range': [80, 100], 'color': 'green'}],
                       'threshold': {'line': {'color': "black", 'width': 4},
                                     'thickness': 0.75,
                                     'value': avg_health}}
            ))

            fig_org = orgs['country'].value_counts().nlargest(10).reset_index()
            fig_org.columns = ['country', 'count']
            fig_org_plot = px.bar(fig_org, x='country', y='count', title="Top 10 Countries by Organizations")
            fig_org_plot.update_layout(xaxis_tickangle=-45)

            tab_content = dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_health), width=6),
                dbc.Col(dcc.Graph(figure=fig_org_plot), width=6)
            ])

        # -------------------- Country KPI --------------------
        elif tab == "tab-country-kpi":
            country_df = pd.DataFrame()
            country_df['Country'] = orgs.groupby('country')['organization_id'].nunique().index
            country_df['Organizations'] = orgs.groupby('country')['organization_id'].nunique().values
            country_df['Assets'] = assets.groupby('country')['asset_id'].nunique().reindex(country_df['Country'], fill_value=0).values
            country_df['Devices'] = devices.groupby('country')['device_id'].nunique().reindex(country_df['Country'], fill_value=0).values
            country_df['Interfaces'] = interfaces.groupby('country')['interface_id'].nunique().reindex(country_df['Country'], fill_value=0).values
            country_df['Events'] = events.groupby('country')['event_id'].nunique().reindex(country_df['Country'], fill_value=0).values

            table_header = [html.Thead(html.Tr([html.Th(col) for col in country_df.columns]))]
            table_body = [html.Tr([html.Td(country_df.iloc[i][col]) for col in country_df.columns])
                          for i in range(len(country_df))]
            tab_content = html.Div([
                html.H5("Country-wise KPIs"),
                html.Table(table_header + [html.Tbody(table_body)], className="table table-striped table-sm")
            ])

        # -------------------- Assets --------------------
        elif tab == "tab-assets":
            merged = assets.merge(
                devices.groupby('asset_id')['device_id'].count().reset_index(name='actual_device_count'),
                on='asset_id', how='left'
            )
            merged['actual_device_count'] = merged['actual_device_count'].fillna(0)
            fig = px.scatter(merged, x='num_devices', y='actual_device_count', color='country',
                             hover_data=['name'], title="Asset: Stored vs Actual Device Count per Country")
            tab_content = dcc.Graph(figure=fig)

        # -------------------- Devices --------------------
        elif tab == "tab-devices":
            merged = devices.merge(
                interfaces.groupby('device_id')['interface_id'].count().reset_index(name='actual_interface_count'),
                on='device_id', how='left'
            )
            merged['actual_interface_count'] = merged['actual_interface_count'].fillna(0)
            fig = px.scatter(merged, x='num_interfaces', y='actual_interface_count', color='country',
                             hover_data=['device_id'], title="Device: Stored vs Actual Interface Count per Country")
            tab_content = dcc.Graph(figure=fig)

        # -------------------- Interfaces --------------------
        elif tab == "tab-interfaces":
            merged = interfaces.merge(
                events.groupby('interface_id')['event_id'].count().reset_index(name='actual_event_count'),
                on='interface_id', how='left'
            )
            merged['actual_event_count'] = merged['actual_event_count'].fillna(0)
            fig = px.scatter(merged, x='num_events', y='actual_event_count', color='country',
                             hover_data=['interface_id'], title="Interface: Stored vs Actual Event Count per Country")
            tab_content = dcc.Graph(figure=fig)

        # -------------------- Events --------------------
        elif tab == "tab-events":
            if not events.empty:
                events['timestamp'] = pd.to_datetime(events['timestamp'], errors='coerce')
                fig = px.histogram(events, x='timestamp', color='country', nbins=50,
                                   title="Events Over Time (Top Countries)")
                tab_content = dcc.Graph(figure=fig)

    except Exception as e:
        tab_content = html.P(f"Error generating tab: {e}")

    return html.Div([kpi_row, html.Hr(), tab_content])


# ------------------------
# Run app
# ------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)