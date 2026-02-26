import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def render_event_distribution(events_df):
    st.subheader("Event Type Distribution")
    fig, ax = plt.subplots()
    sns.countplot(data=events_df, x="event_type", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

def render_events_over_time(events_df):
    st.subheader("Events Over Time")
    events_df["event_timestamp"] = pd.to_datetime(events_df["event_timestamp"])
    grouped = events_df.groupby(events_df["event_timestamp"].dt.date).size()

    fig, ax = plt.subplots()
    grouped.plot(ax=ax)
    st.pyplot(fig)