# services/device_health_app.py
import pandas as pd
from pathlib import Path
from dash import html, dcc
import plotly.graph_objects as go
import warnings

# Suppress warnings
warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", pd.errors.DtypeWarning)

# Dynamic paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent / "data/raw"
DEVICES_CSV = ROOT_DIR / "device/devices.csv"
ASSETS_CSV = ROOT_DIR / "asset/assets.csv"
ORG_CSV = ROOT_DIR / "organization/organization.csv"
INTERFACES_CSV = ROOT_DIR / "interface/interfaces.csv"
EVENTS_CSV = ROOT_DIR / "event/events.csv"

def load_csv(path: Path):
    if not path.exists():
        print(f"ERROR: CSV not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return df

def load_devices(): return load_csv(DEVICES_CSV)
def load_assets(): return load_csv(ASSETS_CSV)
def load_orgs(): return load_csv(ORG_CSV)
def load_interfaces(): return load_csv(INTERFACES_CSV)
def load_events(): return load_csv(EVENTS_CSV)

# KPI Counts
def get_dashboard_counts():
    return {
        "orgs": len(load_orgs()),
        "assets": len(load_assets()),
        "devices": len(load_devices()),
        "interfaces": len(load_interfaces())
    }

# Device Health Gauge
def get_device_health_overview():
    devices = load_devices()
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
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 50], 'color': 'red'},
                {'range': [50, 80], 'color': 'orange'},
                {'range': [80, 100], 'color': 'green'}
            ],
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig

# Anomalies Table
def get_anomalies_table():
    devices = load_devices()
    if devices.empty:
        return [html.Tr([html.Td("No devices found", colSpan=4)])]

    # Dynamic device name
    str_cols = devices.select_dtypes("object").columns
    device_col = str_cols[0] if len(str_cols) > 0 else devices.columns[0]

    # Dynamic numeric columns
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

# Alerts List
def get_alerts_list():
    events = load_events()
    devices = load_devices()
    assets = load_assets()
    orgs = load_orgs()

    if events.empty:
        return [html.Li("No alerts found")]

    merged = events.merge(devices, on="device_id", how="left") \
                   .merge(assets, on="asset_id", how="left") \
                   .merge(orgs, left_on="organization_id", right_on="organization_id", how="left")

    merged["timestamp"] = pd.to_datetime(merged["timestamp"], errors='coerce').fillna(pd.Timestamp.now())
    merged["description"] = merged["description"].astype(str)

    merged = merged.sort_values("timestamp", ascending=False).head(10)

    alerts = []
    for _, row in merged.iterrows():
        dev = row.get("name_x", row.get("name", "Unknown Device"))
        org = row.get("name_y", row.get("name", "Unknown Organization"))
        alerts.append(html.Li(f"{row['timestamp']} - {org} / {dev}: {row['description']}"))
    return alerts

# Logs List
def get_logs_list():
    events = load_events()
    devices = load_devices()
    assets = load_assets()
    orgs = load_orgs()

    if events.empty:
        return [html.Li("No logs found")]

    merged = events.merge(devices, on="device_id", how="left") \
                   .merge(assets, on="asset_id", how="left") \
                   .merge(orgs, left_on="organization_id", right_on="organization_id", how="left")

    merged["timestamp"] = pd.to_datetime(merged["timestamp"], errors='coerce').fillna(pd.Timestamp.now())
    merged["description"] = merged["description"].astype(str)

    merged = merged.sort_values("timestamp", ascending=False).head(20)

    logs = []
    for _, row in merged.iterrows():
        dev = row.get("name_x", row.get("name", "Unknown Device"))
        org = row.get("name_y", row.get("name", "Unknown Organization"))
        logs.append(html.Li(f"{row['timestamp']} - {org} / {dev}: {row['description']}"))
    return logs