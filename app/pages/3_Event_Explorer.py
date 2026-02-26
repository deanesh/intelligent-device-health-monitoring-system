import streamlit as st
from services.data_service import load_events
from components.tables import render_event_table

st.title("🚨 Event Explorer")

events = load_events()

event_type = st.selectbox("Filter by Event Type", events["event_type"].unique())
filtered = events[events["event_type"] == event_type]

render_event_table(filtered)