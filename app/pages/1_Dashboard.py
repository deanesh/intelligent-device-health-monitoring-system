import streamlit as st
from services.data_service import load_dashboard_data, load_events
from components.kpis import render_kpis
from components.charts import render_event_distribution

st.title("📊 System Overview")

data = load_dashboard_data()
render_kpis(data)

events = load_events()
render_event_distribution(events)