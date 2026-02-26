import streamlit as st

def configure_layout():
    st.set_page_config(
        page_title="Device Health Monitoring",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )