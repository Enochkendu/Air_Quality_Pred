import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import fetch_live_aqi, get_city_history, init_settings
import plotly.graph_objects as go
init_settings()

st.title("📊 Historical vs Live AQI Comparison")

@st.cache_data
def load_data():
    return pd.read_csv("data/station_day_with_station_info.csv", parse_dates=["Date"])

df = load_data()

cities = sorted(df["City"].unique())
city = st.selectbox("Select City", cities)

if st.button("Compare"):
    history = get_city_history(df, city)
    live = fetch_live_aqi(city)

    if not live:
        st.error("Could not fetch live AQI.")
    else:
        live_aqi = live["AQI"]

        st.subheader(f" 📍 {city}")

        col1, col2 = st.columns(2)
        col1.metric("Live AQI", live_aqi)
        col2.metric("Last Historical AQI", round(history["AQI"].iloc[-1], 1))

        fig = go.Figure()

        # Historical line
        fig.add_trace(go.Scatter(
            x=history["Date"],
            y=history["AQI"],
            mode="lines",
            name="Historical AQI"

        ))

        #Live point
        fig.add_trace(go.Scatter(
            x=[history["Date"].iloc[-1]],
            y=[live_aqi],
            mode="markers",
            marker=dict(size=12, color="red"),
            name="Live AQI"
        ))

        fig.update_layout(
            title=f"{city} AQI Trend",
            xaxis_title="Date",
            yaxis_title="AQI",
            hovermode="x unified",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🌫️ Live Pollutant Values")

        c1, c2, c3 = st.columns(3)
        c1.metric("PM2.5", live["PM2.5"])
        c2.metric("PM10", live["PM10"])
        c3.metric("NO2", live["NO2"])

        c4, c5, c6 = st.columns(3)
        c4.metric("SO2", live["SO2"])
        c5.metric("CO", live["CO"])
        c6.metric("O3", live["O3"])
