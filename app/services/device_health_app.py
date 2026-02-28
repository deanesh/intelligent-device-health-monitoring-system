# services/device_health_app.py
import pandas as pd
from pathlib import Path
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.simplefilter("ignore", FutureWarning)
warnings.simplefilter("ignore", pd.errors.DtypeWarning)

# ---------------------------
# Paths to CSV files
# ---------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent / "data/raw"
DEVICES_CSV = ROOT_DIR / "device/devices.csv"
ASSETS_CSV = ROOT_DIR / "asset/assets.csv"
ORG_CSV = ROOT_DIR / "organization/organization.csv"
INTERFACES_CSV = ROOT_DIR / "interface/interfaces.csv"
EVENTS_CSV = ROOT_DIR / "event/events.csv"

# ---------------------------
# Load CSV safely
# ---------------------------
def load_csv(path: Path):
    if not path.exists():
        print(f"ERROR: CSV not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Deduplicate duplicate column names
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        dup_idx = cols[cols == dup].index.tolist()
        for i, idx in enumerate(dup_idx[1:], start=1):
            cols[idx] = f"{dup}_dup{i}"
    df.columns = cols
    return df

# ---------------------------
# Loaders
# ---------------------------
def load_devices(): return load_csv(DEVICES_CSV)
def load_assets(): return load_csv(ASSETS_CSV)
def load_orgs(): return load_csv(ORG_CSV)
def load_interfaces(): return load_csv(INTERFACES_CSV)
def load_events(): return load_csv(EVENTS_CSV)

# ---------------------------
# Dashboard KPIs
# ---------------------------
def get_dashboard_counts():
    return {
        "orgs": len(load_orgs()),
        "assets": len(load_assets()),
        "devices": len(load_devices()),
        "interfaces": len(load_interfaces()),
        "events": len(load_events())
    }

# ---------------------------
# EDA-style graphs
# ---------------------------
def get_device_health_overview():
    devices = load_devices()
    if devices.empty:
        return go.Figure()
    # Assume health_score exists, else use first numeric
    if "health_score" in devices.columns:
        avg_health = devices["health_score"].mean()
    else:
        numeric_cols = devices.select_dtypes("number").columns
        avg_health = devices[numeric_cols[0]].mean() if len(numeric_cols) > 0 else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_health,
        title={'text': "Overall Device Health"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 50], 'color': 'red'},
                {'range': [50, 80], 'color': 'orange'},
                {'range': [80, 100], 'color': 'green'}
            ]
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20,r=20,t=40,b=40))
    return fig

def get_org_country_distribution():
    orgs = load_orgs()
    if orgs.empty: return go.Figure()
    fig = px.histogram(orgs, x="country", title="Organizations by Country", color="country")
    return fig

def get_assets_per_org():
    assets = load_assets()
    orgs = load_orgs()
    if assets.empty or orgs.empty: return go.Figure()
    merged = assets.merge(orgs[['organization_id','country']], on='organization_id', how='left')
    fig = px.histogram(merged, x="organization_id", y="asset_id", histfunc="count", 
                       title="Assets per Organization", labels={"asset_id":"Asset Count","organization_id":"Org ID"})
    return fig

def get_devices_per_asset():
    devices = load_devices()
    assets = load_assets()
    if devices.empty or assets.empty: return go.Figure()
    merged = devices.merge(assets[['asset_id','organization_id']], on='asset_id', how='left')
    fig = px.histogram(merged, x="asset_id", y="device_id", histfunc="count", 
                       title="Devices per Asset", labels={"device_id":"Device Count","asset_id":"Asset ID"})
    return fig

def get_interfaces_per_device():
    interfaces = load_interfaces()
    devices = load_devices()
    if interfaces.empty or devices.empty: return go.Figure()
    merged = interfaces.merge(devices[['device_id','asset_id']], on='device_id', how='left')
    fig = px.histogram(merged, x="device_id", y="interface_id", histfunc="count",
                       title="Interfaces per Device", labels={"interface_id":"Interface Count","device_id":"Device ID"})
    return fig

def get_events_over_time():
    events = load_events()
    if events.empty: return go.Figure()
    events['timestamp'] = pd.to_datetime(events['timestamp'])
    fig = px.histogram(events, x="timestamp", nbins=50, title="Events Over Time")
    return fig