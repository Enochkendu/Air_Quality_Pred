import joblib
import numpy as np
import os
import pandas as pd
import requests
import streamlit as st
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error

AQI_BUCKETS = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
FORECAST_MODEL_DIR = os.path.join(BASE_DIR, "models_forecast")

# -------------------------------------------
# AQI Styling
# -------------------------------------------

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
# -------------------------------------------
# Feature Engineering
# -------------------------------------------

def create_features(df):
    df = df.sort_values("Date").copy()
    df["Month"] = df["Date"].dt.month
    df["Dayofweek"] = df["Date"].dt.dayofweek

    for col in ["PM2.5", "PM10"]:
        df[f"{col}_lag1"] = df[col].shift(1)

    df = df.dropna()

    features = ["PM2.5", "PM10", "NO2", "SO2",
                "CO", "O3", "Month", "Dayofweek",
                "PM2.5_lag1", "PM10_lag1"]
    return df, features
    
# -------------------------------------------
# City Model Trainer (Cached)
# -------------------------------------------
@st.cache_resource
def train_city_models(city, df):
    city_df = df[df["City"] == city].copy()

    if len(city_df) < 300:
        return None, None

    city_df, features = create_features(city_df)

    X = city_df[features]
    y_reg = city_df["AQI"]
    y_clf = city_df["AQI_Bucket"].map({
        "Good": 0,
        "Satisfactory": 1,
        "Moderate": 2,
        "Poor": 3,
        "Very Poor": 4,
        "Severe": 5
    })

    split = int(len(city_df) * 0.8)

    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_reg_train, y_reg_test = y_reg.iloc[:split], y_reg.iloc[split:]
    y_clf_train, y_clf_test = y_clf.iloc[:split], y_clf.iloc[split:]

    reg = RandomForestRegressor(
        n_estimators=500,
        max_depth=25,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )

    clf = RandomForestClassifier(
        n_estimators=400,
        max_depth=20,
        min_samples_leaf=2,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    reg.fit(X_train, y_reg_train)
    clf.fit(X_train, y_clf_train)

    return reg, clf

# -------------------------------------------
# Prediction
# -------------------------------------------
def predict_aqi(city, inputs, df):
    models = train_city_models(city, df)

    if models == (None, None):
        return None, None

    reg, clf = models

    X = np.array(inputs).reshape(1, -1)

    aqi_value = reg.predict(X)[0]
    aqi_class_num = clf.predict(X)[0]

    aqi_class = AQI_BUCKETS[int(aqi_class_num)]

    return round(aqi_value, 2), aqi_class

# -------------------------------------------
# Live AQI
# -------------------------------------------
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
# -------------------------------------------
# History
# -------------------------------------------
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

# -------------------------------------------
# Settings 
# -------------------------------------------
def get_settings():
    # Ensure defaults
    defaults = {
        "theme": "Light",
        "show_grid": True,
        "forecast_days": 7,
        "health_alerts": True
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    return {
        "theme": st.session_state.theme,
        "show_grid": st.session_state.show_grid,
        "forecast_days": st.session_state.forecast_days,
        "health_alerts": st.session_state.health_alerts
    }

