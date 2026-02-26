import streamlit as st

def device_filter(devices_df):
    device_ids = devices_df["device_id"].unique()
    selected = st.sidebar.selectbox("Select Device", device_ids)
    return selected