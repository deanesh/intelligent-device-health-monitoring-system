import streamlit as st
from services.data_service import load_devices, load_events
from components.filters import device_filter
from components.tables import render_event_table

st.title("🔍 Device Analysis")

devices = load_devices()
events = load_events()

selected_device = device_filter(devices)

device_info = devices[devices["device_id"] == selected_device]
device_events = events[events["device_id"] == selected_device]

st.subheader("Device Details")
st.dataframe(device_info)

render_event_table(device_events)