import joblib
import numpy as np
import os
import pandas as pd
import requests
import streamlit as st

AQI_BUCKETS = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
FORECAST_MODEL_DIR = os.path.join(BASE_DIR, "models_forecast")

def load_models(city):
    reg = joblib.load(os.path.join(MODEL_DIR, f"{city}_rf_reg.pkl"))
    clf = joblib.load(os.path.join(MODEL_DIR, f"{city}_rf_clf.pkl"))
    return reg,clf

def predict_aqi(city, inputs):
    reg, clf = load_models(city)

    inputs = np.array(inputs).reshape(1, -1)

    aqi_value = reg.predict(inputs)[0]
    aqi_class_num = clf.predict(inputs)[0]

    # Convert number to text label

    aqi_class = AQI_BUCKETS[int(aqi_class_num)]

    return round(aqi_value, 2), aqi_class


def aqi_style(category):
    styles = {
        "Good": ("#2ecc71", "😃"),
        "Satisfactory": ("#a3e635", "🙂"),
        "Moderate": ("#facc15", "😐"),
        "Poor": ("#fb923c", "😷"),
        "Very Poor": ("#ef4444", "🤢"),
        "Severe": ("#7f1d1d", "☠️"),
    }
    return styles.get(category, ("#e5e7eb", "❓"))

def health_tip(category):
    tips = {
        "Good": "Air quality is excellent. Enjoy your day!",
        "Satisfactory": "Air quality is acceptable.",
        "Moderate": "Sensitive individuals should reduce outdoor activity.",
        "Poor": "Avoid prolonged outdoor exposure.",
        "Very Poor": "Stay indoors. Wear a mask if necessary.",
        "Severe": "Health emergency. Avoid all outdoor activity!"
    }
    return tips.get(category, "")

def fetch_live_aqi(city):
        """
        Fetch real-time AQI and pollutant data using WAQI API
        City must be a valid WAQI city identifer.
        """
        token = st.secrets["WAQI_TOKEN"] # Securely retrieve token
        url = f"https://api.waqi.info/feed/{city}/?token={token}"

        try:
            response = requests.get(url)
            data = response.json()
        except Exception as e:
            return None

        if data["status"] != "ok":
            return None

        iaqi = data["data"]["iaqi"]

        def get_val(key):
            return iaqi[key]["v"] if key in iaqi else None

        return{
            "AQI": data["data"].get("aqi"),
            "PM2.5": get_val("pm25"),
            "PM10": get_val("pm10"),
            "NO2": get_val("no2"),
            "SO2": get_val("so2"),
            "CO": get_val("co"),
            "O3": get_val("o3"),
            "dominant": data["data"].get("dominentpol", None)
        }

def get_city_history(df, city):
    city_df = df[df["City"] == city].copy()
    city_df = city_df.sort_values("Date")
    return city_df[["Date", "AQI"]]

def load_forecast_model(city):
    model_path = os.path.join(FORECAST_MODEL_DIR, f"{city}_forecast.pkl")
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

def make_forecast_features(aqi_series, last_date):
    features = []
    lag1 = aqi_series[-1]
    lag2 = aqi_series[-2]
    lag3 = aqi_series[-3]

    roll3 = np.mean(aqi_series[-3:])
    roll7 = np.mean(aqi_series[-7:])

    next_date = last_date + pd.Timedelta(days=1)

    features = [
        lag1, lag2, lag3,
        roll3, roll7,
        next_date.day,
        next_date.month,
        next_date.weekday()
    ]

    return np.array(features).reshape(1, -1), next_date

def forecast_next_days(city, city_df, days=7):
    model = load_forecast_model(city)
    if model is None:
        return None

    history = city_df.sort_values("Date")
    aqi_series = list(history["AQI"].values)
    last_date = history["Date"].iloc[-1]

    forecasts = []

    for _ in range(days):
        X, next_date = make_forecast_features(aqi_series, last_date)
        next_aqi = model.predict(X)[0]

        forecasts.append((next_date, next_aqi))

        # update rolling history
        aqi_series.append(next_aqi)
        aqi_series.pop(0)
        last_date = next_date

    return forecasts

def init_settings():
    defaults = {
        "theme": "Light",
        "show_emojis": True,
        "font_size": 16,
        "aqi_standard": "India (CPCB)",
        "time_format": "24-hour",
        "confidence": "Medium",
        "forecast_days": 7
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_setting(key):
    return st.session_state.get(key)


def set_setting(key, value):
    st.session_state[key] = value


def init_settings():
    defaults = {
        "theme": "Light",
        "show_emojis": True,
        "font_size": 16,
        "aqi_standard": "India (CPCB)",
        "time_format": "24-hour",
        "confidence": "Medium",
        "forecast_days": 7
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_setting(key):
    return st.session_state.get(key)


def set_setting(key, value):
    st.session_state[key] = value
