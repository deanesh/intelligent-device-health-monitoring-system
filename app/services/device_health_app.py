# app/device_health_app.py
import pandas as pd
from pathlib import Path
from dash import html, dcc
import plotly.graph_objects as go

# =========================
# Root data directory
# =========================
ROOT_DIR = Path(__file__).resolve().parent.parent / "data/raw"

# CSV Paths
DEVICES_CSV = ROOT_DIR / "device/devices.csv"
ASSETS_CSV = ROOT_DIR / "asset/assets.csv"
ORG_CSV = ROOT_DIR / "organization/organization.csv"
INTERFACES_CSV = ROOT_DIR / "interface/interfaces.csv"
EVENTS_CSV = ROOT_DIR / "event/events.csv"

# =========================
# Helper function to load CSV safely
# =========================
def load_csv(path: Path):
    if not path.exists():
        print(f"WARNING: CSV not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Convert numeric columns automatically
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    return df

# =========================
# Load DataFrames
# =========================
def load_devices():
    return load_csv(DEVICES_CSV)

def load_assets():
    return load_csv(ASSETS_CSV)

def load_orgs():
    return load_csv(ORG_CSV)

def load_interfaces():
    return load_csv(INTERFACES_CSV)

def load_events():
    return load_csv(EVENTS_CSV)

# =========================
# Device Health Overview
# =========================
def get_device_health_overview():
    devices = load_devices()
    assets = load_assets()
    orgs = load_orgs()

    if devices.empty or assets.empty or orgs.empty:
        # default gauge if no data
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=75,
            title={"text": "Overall Device Health (No Data)"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "green"}}
        ))
        return fig

    # Merge devices -> assets -> organizations
    merged = devices.merge(assets, on="asset_id", how="left") \
                    .merge(orgs, left_on="organization_id", right_on="organization_id", how="left")
    
    # Compute average health per organization
    health_col = "health_score" if "health_score" in merged.columns else merged.select_dtypes("number").columns[0]
    merged[health_col] = pd.to_numeric(merged[health_col], errors='coerce').fillna(0)

    avg_health = merged[health_col].mean()

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_health,
        title={"text": "Overall Device Health Across All Organizations"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "green"}}
    ))
    return fig

# =========================
# Anomalies Table
# =========================
def get_anomalies_table():
    devices = load_devices()
    if devices.empty:
        return [html.Tr([html.Td("No devices found", colSpan=4)])]

    # Detect anomalies on CPU and Temperature (if columns exist)
    cpu_col = "cpu_usage" if "cpu_usage" in devices.columns else None
    temp_col = "temperature" if "temperature" in devices.columns else None
    device_col = "device_name" if "device_name" in devices.columns else devices.columns[0]

    anomalies = []
    for _, row in devices.iterrows():
        device_name = row.get(device_col, "Unknown")
        if cpu_col and row.get(cpu_col, 0) > 90:
            anomalies.append({"device": device_name, "metric": "CPU", "value": row[cpu_col], "status": "Critical"})
        if temp_col and row.get(temp_col, 0) > 85:
            anomalies.append({"device": device_name, "metric": "Temperature", "value": row[temp_col], "status": "Warning"})
    
    rows = []
    for a in anomalies:
        color = "red" if a["status"] == "Critical" else "orange"
        rows.append(html.Tr([
            html.Td(a["device"]),
            html.Td(a["metric"]),
            html.Td(a["value"]),
            html.Td(a["status"], style={"color": color})
        ]))
    if not rows:
        rows.append(html.Tr([html.Td("No anomalies detected", colSpan=4)]))
    return rows

# =========================
# Alerts List
# =========================
def get_alerts_list():
    events = load_events()
    devices = load_devices()
    assets = load_assets()
    orgs = load_orgs()

    if events.empty:
        return [html.Li("No alerts found")]

    # Merge to get device & organization names
    merged = events.merge(devices, on="device_id", how="left") \
                   .merge(assets, on="asset_id", how="left") \
                   .merge(orgs, left_on="organization_id", right_on="organization_id", how="left")
    
    timestamp_col = "timestamp" if "timestamp" in merged.columns else merged.columns[0]
    message_col = "description" if "description" in merged.columns else merged.columns[1]

    merged[timestamp_col] = pd.to_datetime(merged[timestamp_col], errors='coerce').fillna(pd.Timestamp.now())
    merged[message_col] = merged[message_col].astype(str)

    # Sort by most recent
    merged = merged.sort_values(timestamp_col, ascending=False).head(10)

    alerts = []
    for _, row in merged.iterrows():
        device_name = row.get("device_name", "Unknown Device")
        org_name = row.get("name", "Unknown Organization")
        alerts.append(html.Li(f"{row[timestamp_col]} - {org_name} / {device_name}: {row[message_col]}"))
    return alerts

# =========================
# Logs List
# =========================
def get_logs_list():
    events = load_events()
    devices = load_devices()
    assets = load_assets()
    orgs = load_orgs()

    if events.empty:
        return [html.Li("No logs available")]

    merged = events.merge(devices, on="device_id", how="left") \
                   .merge(assets, on="asset_id", how="left") \
                   .merge(orgs, left_on="organization_id", right_on="organization_id", how="left")
    
    timestamp_col = "timestamp" if "timestamp" in merged.columns else merged.columns[0]
    message_col = "description" if "description" in merged.columns else merged.columns[1]

    merged[timestamp_col] = pd.to_datetime(merged[timestamp_col], errors='coerce').fillna(pd.Timestamp.now())
    merged[message_col] = merged[message_col].astype(str)

    merged = merged.sort_values(timestamp_col, ascending=False).tail(20)

    logs = []
    for _, row in merged.iterrows():
        device_name = row.get("device_name", "Unknown Device")
        org_name = row.get("name", "Unknown Organization")
        logs.append(html.Li(f"{row[timestamp_col]} - {org_name} / {device_name}: {row[message_col]}"))
    return logs