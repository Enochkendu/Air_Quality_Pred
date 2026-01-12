import streamlit as st
import datetime
from utils import predict_aqi, aqi_style, health_tip, init_settings
init_settings()

st.title("🧪 Manual AQI Prediction")

cities = [
    "Delhi", "Hyderabad", "Mumbai",
    "Kolkata", "Bengaluru",
    "Jaipur", "Visakhapatnam",
    "Thiruvananthapuram"
]

city = st.selectbox("Select City", cities)

PM25 = st.number_input("PM2.5", 0.0, 1000.0, 50.0)
PM10 = st.number_input("PM10", 0.0, 1000.0, 80.0)
NO2  = st.number_input("NO₂", 0.0, 500.0, 40.0)
SO2  = st.number_input("SO₂", 0.0, 500.0, 10.0)
CO   = st.number_input("CO", 0.0, 50.0, 1.0)
O3   = st.number_input("O₃", 0.0, 500.0, 30.0)

today = datetime.date.today()
month = today.month
dayofweek = today.weekday()

PM25_lag1 = st.number_input("Yesterday PM2.5", 0.0, 1000.0, PM25)
PM10_lag1 = st.number_input("Yesterday PM10", 0.0, 1000.0, PM10)

if st.button("Predict AQI"):
    try:
        aqi, category = predict_aqi(
            city,
            [
                PM25, PM10, NO2, SO2, CO, O3,
                month, dayofweek, PM25_lag1, PM10_lag1
            ]
        )


        color, emoji = aqi_style(category)
        tip = health_tip(category)
        
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

        st.warning(tip)
        
    except Exception as e:
        st.error(str(e))
