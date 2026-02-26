import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path("../data/processed")

@st.cache_data
def load_devices():
    return pd.read_csv(DATA_PATH / "devices_snapshot.csv")

@st.cache_data
def load_events():
    return pd.read_csv(DATA_PATH / "events_snapshot_sample.csv")

def load_dashboard_data():
    devices = load_devices()
    events = load_events()

    return {
        "total_devices": len(devices),
        "total_events": len(events),
        "avg_events_per_device": devices["num_events"].mean()
    }