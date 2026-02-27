# services/device_health_app.py
import pandas as pd
from pathlib import Path
from dash import html, dcc
import plotly.graph_objects as go
import warnings

warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", pd.errors.DtypeWarning)

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent / "data/raw"
DEVICES_CSV = ROOT_DIR / "device/devices.csv"
ASSETS_CSV = ROOT_DIR / "asset/assets.csv"
ORG_CSV = ROOT_DIR / "organization/organization.csv"
INTERFACES_CSV = ROOT_DIR / "interface/interfaces.csv"
EVENTS_CSV = ROOT_DIR / "event/events.csv"

# --- Modern CSV loader ---
def load_csv(path: Path):
    if not path.exists():
        print(f"ERROR: CSV not found at {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Deduplicate column names
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        dup_idx = cols[cols == dup].index.tolist()
        for i, idx in enumerate(dup_idx[1:], start=1):
            cols[idx] = f"{dup}_dup{i}"
    df.columns = cols

    # Convert numeric safely
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return df

# --- Loaders ---
def load_devices(): return load_csv(DEVICES_CSV)
def load_assets(): return load_csv(ASSETS_CSV)
def load_orgs(): return load_csv(ORG_CSV)
def load_interfaces(): return load_csv(INTERFACES_CSV)
def load_events(): return load_csv(EVENTS_CSV)

# --- Dashboard KPIs ---
def get_dashboard_counts():
    return {
        "orgs": len(load_orgs()),
        "assets": len(load_assets()),
        "devices": len(load_devices()),
        "interfaces": len(load_interfaces())
    }

# --- Device Health Overview (Corrected Gauge) ---
def get_device_health_overview():
    devices = load_devices()
    # Determine average health
    if "health_score" in devices.columns and not devices.empty:
        avg_health = devices["health_score"].mean()
    else:
        numeric_cols = devices.select_dtypes("number").columns
        avg_health = devices[numeric_cols[0]].mean() if len(numeric_cols) > 0 else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=avg_health,
        delta={'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        title={'text': "Overall Device Health"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "rgba(0,0,0,0)"},
            'steps': [
                {'range': [0, 50], 'color': 'red'},
                {'range': [50, 80], 'color': 'orange'},
                {'range': [80, 100], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': float(avg_health)
            }
        }
    ))

    # Add color legend
    fig.add_annotation(dict(
        x=0.1, y=-0.15,
        showarrow=False,
        text="Red: Poor | Orange: Moderate | Green: Good",
        xref="paper",
        yref="paper"
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=40))
    return fig

# --- Anomalies Table ---
def get_anomalies_table():
    devices = load_devices()
    if devices.empty:
        return [html.Tr([html.Td("No devices found", colSpan=4)])]

    str_cols = devices.select_dtypes("object").columns
    device_col = str_cols[0] if len(str_cols) > 0 else devices.columns[0]
    numeric_cols = devices.select_dtypes("number").columns
    cpu_col = "cpu_usage" if "cpu_usage" in numeric_cols else (numeric_cols[0] if len(numeric_cols) > 0 else None)
    temp_col = "temperature" if "temperature" in numeric_cols else (numeric_cols[1] if len(numeric_cols) > 1 else None)

    anomalies = []
    for _, row in devices.iterrows():
        dev_name = row.get(device_col, "Unknown")
        if cpu_col and row.get(cpu_col, 0) > 90:
            anomalies.append({"device": dev_name, "metric": "CPU Usage", "value": row[cpu_col], "status": "Critical"})
        if temp_col and row.get(temp_col, 0) > 85:
            anomalies.append({"device": dev_name, "metric": "Temperature", "value": row[temp_col], "status": "Warning"})

    if not anomalies:
        return [html.Tr([html.Td("No anomalies detected", colSpan=4)])]

    rows = []
    for a in anomalies:
        color = "red" if a["status"] == "Critical" else "orange"
        rows.append(html.Tr([
            html.Td(a["device"]),
            html.Td(a["metric"]),
            html.Td(a["value"]),
            html.Td(a["status"], style={"color": color})
        ]))
    return rows

# --- Alerts Table (device_id, ip_address, message) ---
def get_alerts_list():
    events = load_events()
    devices = load_devices()
    assets = load_assets()
    orgs = load_orgs()

    if events.empty:
        return [html.Tr([html.Td("No alerts found", colSpan=3)])]

    # Merge using asset bridge
    devices_clean = devices[['device_id', 'asset_id', 'ip_address']].copy()
    assets_clean = assets[['asset_id', 'organization_id']].copy()
    merged = events.merge(devices_clean, on='device_id', how='left') \
                   .merge(assets_clean, on='asset_id', how='left') \
                   .merge(orgs[['organization_id','name']], on='organization_id', how='left', suffixes=('','_org'))

    merged['device_ip'] = merged['ip_address'].fillna("Unknown IP")
    merged['organization_name'] = merged['name'].fillna("Unknown Org")
    merged_sorted = merged.sort_values('timestamp', ascending=False).head(10)

    table_rows = []
    for _, row in merged_sorted.iterrows():
        table_rows.append(html.Tr([
            html.Td(row.get('device_id', 'Unknown')),
            html.Td(row.get('device_ip', 'Unknown IP')),
            html.Td(row.get('description', ''))
        ]))
    return table_rows

# --- Organizations KPI Table (skip zero assets) ---
def get_org_kpi_table():
    orgs = load_orgs()
    assets = load_assets()
    devices = load_devices()

    org_rows = []
    for _, org in orgs.iterrows():
        org_id = org.get("organization_id")
        org_name = org.get("name", "Unknown Org")
        org_assets = assets[assets['organization_id'] == org_id]
        if len(org_assets) == 0:
            continue  # skip orgs with zero assets
        org_devices = devices[devices['asset_id'].isin(org_assets['asset_id'])]
        org_rows.append(html.Tr([
            html.Td(org_name),
            html.Td(len(org_assets)),
            html.Td(len(org_devices))
        ]))
    return org_rows