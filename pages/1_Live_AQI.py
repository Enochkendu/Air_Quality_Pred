import streamlit as st
import pandas as pd
from utils import fetch_live_aqi, predict_aqi, aqi_style, health_tip, get_settings
from utils import apply_theme

# ------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Live AQI",
    layout="centered"
)
st.title("📍 Live Air Quality")

apply_theme()

st.markdown("""
Get **real-time air quality** for cities using the WAQI API.
""")

city_input = st.text_input(
    "Enter City Name (for live AQI)",
    "Delhi"
)

@st.cache_data()
def load_data():
    return pd.read_csv("data/cleaned_station_day_with_station_info.csv",
                       parse_dates=["Date"])
df = load_data()

cities = sorted(df["City"].unique())

if st.button("🚀 Fetch Live AQI"):
    with st.spinner("Fetching live data..."):
        live_data = fetch_live_aqi(city_input)

    if not live_data:
        st.error("Could not fetch live data for this city.")
    else:
        # Show API AQI
        aqi_live = live_data["AQI"]
        pm25_live = live_data["PM2.5"]
        pm10_live = live_data["PM10"]
        no2_live  = live_data["NO2"]
        so2_live  = live_data["SO2"]
        co_live   = live_data["CO"]
        o3_live   = live_data["O3"]
        dominant  = live_data["dominant"]

        st.subheader(f"📍 Live AQI for {city_input.title()}")

        color, emoji = aqi_style(
            "Good" if aqi_live <= 50 else
            "Satisfactory" if aqi_live <= 100 else
            "Moderate" if aqi_live <= 200 else
            "Poor" if aqi_live <= 300 else
            "Very Poor" if aqi_live <= 400 else
            "Severe"
        )

        h_tip = health_tip(
            "Good" if aqi_live <= 50 else
            "Satisfactory" if aqi_live <= 100 else
            "Moderate" if aqi_live <= 200 else
            "Poor" if aqi_live <= 300 else
            "Very Poor" if aqi_live <= 400 else
            "Severe"
        )
        
        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:25px;
                border-radius:15px;
                text-align:center;
                color:white;
                font-size:24px;
                font-weight:bold;
            ">
                <div style="font-size:50px;">{emoji}</div>
                Live AQI: {aqi_live}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.info(f"{h_tip}")
        
        st.write("**Dominant Pollutant:**", dominant)

        st.write("### Pollutant Concentrations (Live API)")
        st.write(f"PM2.5: {pm25_live}")
        st.write(f"PM10: {pm10_live}")
        st.write(f"NO₂: {no2_live}")
        st.write(f"SO₂: {so2_live}")
        st.write(f"CO: {co_live}")
        st.write(f"O₃: {o3_live}")

        # 🚀 Optional: Compare with your model’s prediction
        try:
            predicted_value, predicted_cat = predict_aqi(
                city_input.title(),
                [
                    pm25_live, pm10_live,
                    no2_live, so2_live,
                    co_live, o3_live,
                    live_data["AQI"] % 12 + 1,  # simple proxy for month/day
                    0,
                    pm25_live,
                    pm10_live
                ],
                df
            )

            st.write("---")
            st.info(f"📊 Model Predicted AQI: {predicted_value}")
            st.info(f"📊 Model Predicted Category: {predicted_cat}")
        except Exception as e:
            st.warning("Model prediction unavailable for this city.")
            st.error(f"Debug info: {e}")

