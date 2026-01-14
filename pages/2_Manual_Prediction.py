import streamlit as st
import pandas as pd
import datetime
from utils import predict_aqi, aqi_style, health_tip, get_settings


st.set_page_config(page_title="Manual AQI Prediction", layout="centered")
st.title("🧪 Manual AQI Prediction")

@st.cache_data()
def load_data():
    return pd.read_csv("data/cleaned_station_day_with_station_info.csv",
                       parse_dates=["Date"])
df = load_data()

cities = sorted(df["City"].unique())

city = st.selectbox("Select City", cities)

st.markdown("### Enter pollutant values")

col1, col2, col3 = st.columns(3)

with col1:
    PM25 = st.number_input("PM2.5", 0.0, 1000.0, 50.0)

with col2:
    PM10 = st.number_input("PM10", 0.0, 1000.0, 80.0)

with col3:
    NO2  = st.number_input("NO₂", 0.0, 500.0, 40.0)

col4, col5, col6 = st.columns(3)

with col4:
    SO2  = st.number_input("SO₂", 0.0, 500.0, 10.0)

with col5:
    CO   = st.number_input("CO", 0.0, 50.0, 1.0)

with col6:
    O3   = st.number_input("O₃", 0.0, 500.0, 30.0)

today = datetime.date.today()
month = today.month
dayofweek = today.weekday()

col7, col8 = st.columns(2)
with col7:
    PM25_lag1 = st.number_input("Yesterday PM2.5", 0.0, 1000.0, PM25)

with col8:
    PM10_lag1 = st.number_input("Yesterday PM10", 0.0, 1000.0, PM10)

if st.button("🔍 Predict AQI"):
    try:
        inputs = [PM25, PM10, NO2, SO2, CO, O3,
                month, dayofweek, PM25_lag1, PM10_lag1]

        aqi, category = predict_aqi(city, inputs, df)
        
        if aqi is None:
            st.error("Not enough data to train model for this city.")
        else:
            color, emoji = aqi_style(category)
        
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
                    margin-top:20px;
                ">
                    <div style="font-size:50px;">{emoji}</div>
                    <div>AQI: {aqi}</div>
                    <div>{category}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.session_state.get("health_alerts", True):
                st.info(health_tip(category))

        
    except Exception as e:
            st.error(str(e))
