import streamlit as st

def render_kpis(data):
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Devices", data["total_devices"])
    col2.metric("Total Events", data["total_events"])
    col3.metric("Avg Events / Device", round(data["avg_events_per_device"], 2))