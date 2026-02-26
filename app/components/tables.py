import streamlit as st

def render_device_table(devices_df):
    st.subheader("Device Overview")
    st.dataframe(devices_df, use_container_width=True)

def render_event_table(events_df):
    st.subheader("Event Logs")
    st.dataframe(events_df, use_container_width=True)