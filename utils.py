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

# -------------------------------------------
# Theme
# -------------------------------------------

def apply_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    if st.session_state.theme == "Dark":
        st.markdown("""
        <style>
        /* 1. Completely hide the three-dot menu icon */
        #MainMenu {
            visibility: hidden;
            display: none;
        }

        /* Dark Theme */
        section[data-testid="stSidebar"] {
            background-color:  	#494949;
            border-right: 1px solid var(--sidebar-border);
        }
        div[data-testid="stSidebarHeader"] {
            border-bottom: 1px solid var(--sidebar-border);
            padding-bottom: 0.5rem;
        }
        /* Collapse icon */
        div[data-testid="stSidebarCollapseButton"] span {
            color: var(--sidebar-muted) !important;
        }
        a[data-testid="stSidebarNavLink"] {
            color: var(--sidebar-text) !important;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            margin: 0.15rem 0;
            transition: background-color 0.2s ease, color 0.2s ease;
            text-decoration: none;
        }
        /* Hover state */
        a[data-testid="stSidebarNavLink"]:hover {
            background-color: #6d6d6d;
        }
        /* Active page */
        a[data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: linear-gradient(135deg, #000108 0.000%, #091719 20.000%,
                                        #193036 40.000%, #304a4f 60.000%,
                                        #4e5f57 80.000%, #726e4a 100.000%);
            border-left: 4px solid var(--sidebar-active);
            font-weight: 600;
        }
        a[data-testid="stSidebarNavLink"] span {
            color: var(--sidebar-text) !important;
        }
        div[data-testid="stSidebarUserContent"] {
            border-top: 1px solid var(--sidebar-border);
            margin-top: 0.75rem;
            padding-top: 0.75rem;
        }

        div[data-testid="stToolbar"],
        .stAppToolbar {
            background: linear-gradient(135deg,
                rgba(0,1,8,0.85) 0%,
                rgba(9,23,25,0.85) 20%,
                rgba(25,48,54,0.85) 40%,
                rgba(48,74,79,0.85) 60%,
                rgba(78,95,87,0.85) 80%,
                rgba(114,110,74,0.85) 100%
            );
            position: sticky;
            top: 0;
            z-index: 999;
            backdrop-filter: saturate(180%) blur(6px);
            transition: transform 0.3s ease;
        }
        body:has(.main > div:nth-child(2)) div[data-testid="stToolbar"] {
        transform: translateY(-100%);
        }
        div[data-testid="stHeader"] {
            background: linear-gradient(135deg, #020617, #0f172a);
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        div[data-testid="stAppDeployButton"] button {
            background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 6px 14px !important;
            font-weight: 600 !important;
            box-shadow: 0 6px 20px rgba(37,99,235,0.35);
            transition: all 0.25s ease;
        }
        /* Deploy button */
        button[kind="header"] {
          border-radius: 8px;
          font-weight: 600;
        }

        /* Menu (three dots) */
        #MainMenu svg {
          opacity: 0.8;
        }
        .stApp {
            background: linear-gradient(135deg, #000108 0.000%, #091719 20.000%,
                                        #193036 40.000%, #304a4f 60.000%,
                                        #4e5f57 80.000%, #726e4a 100.000%);
            color: white;
        }
        h1, h2, h3, h4, p, span, label, div {
            color: white;
        }
        .main-title {
            font_size: 1.2rem;
            font_weight: 800;
            color: #fff;
            margin-bottom: 0.2em;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #fff;
            margin_bottom: 2em;
            padding-bottom: 20px;
        }
        div[data-testid="stDivider"] hr {
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, #ef4444, transparent);
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.6) !important;
            margin: 24px 0;
            border-color: white;
        }

        .hero {
            padding: 3rem 2rem;
            border-radius: 24px;
            background: linear-gradient(315deg, #070602 0.000%, #330c03 25.000%,
                                        #6f1c0b 50.000%, #b53719 75.000%,
                                        #ff5b2d 100.000%);
            color: white;
            margin-bottom: 2rem;
            border: 1px solid rgba(250, 250, 250, 0.25);
        }
        
        .aqi-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);

            border: 1px solid #fff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);

            padding: 1.5rem;
            
            border-radius: 16px;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.3s ease;
        }
        .card-desc {
            color: #fff;
            margin-top: 0.5rem;
        }

        .aqi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0px 15px 35px rgba(0,0,0,0.1);
        }
        div.stButton > button {
                background-color: #00c897;
                color: #0e1117;
            }
        div.stButton > button:hover {
                background-color: #02b386;
                transform: scale(1.03);
            }
        /* Selectbox container */
        div[data-baseweb="select"] > div {
            background-color: #1e293b !important;
            color: white !important;
        }

        /* Selected value text */
        div[data-baseweb="select"] span {
            color: white !important;
        }

        /* Dropdown menu */
        ul[role="listbox"] {
            background-color: #0f172a !important;
        }

        /* Dropdown options */
        li[role="option"] {
            color: white !important;
            background-color: #0f172a !important;
        }

        /* Hovered option */
        li[role="option"]:hover {
            background-color: #1e40af !important;
        }

        /* Input border */
        div[data-baseweb="select"] > div {
            border: 1px solid #ef4444 !important;
        }
        div[data-testid="stExpander"] {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
        }

        /* Normal (collapsed) */
        div[data-testid="stExpander"] summary {
            background: linear-gradient(135deg, #020617, #1e293b);
            padding: 8px 10px;
            border-radius: 12px;
            font-weight: 600;
            color: white !important;
            transition: all 0.3s ease;
        }

        /* Expanded state */
        div[data-testid="stExpander"] details[open] summary {
            background: linear-gradient(135deg, #7c2d12, #b91c1c);
            border-bottom-left-radius: 0;
            border-bottom-right-radius: 0;
            box-shadow: 0 6px 20px rgba(185, 28, 28, 0.5);
        }

        div[data-testid="stExpander"] svg {
            fill: white !important;
        }

        div[data-testid="stExpanderDetails"] {
            padding: 1rem;
        }

        div[data-testid="stJson"] {
            background: #020617 !important;
            border-radius: 10px;
            padding: 12px;
        }
        div[data-testid="stJson"] .react-json-view {
            background: transparent !important;
            color: white !important;
        }

        </style>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <style>
        /* 1. Completely hide the three-dot menu icon */
        #MainMenu {
            visibility: hidden;
            display: none;
        }
        /* Light Theme */
            background-color:  	#494949;
            border-right: 1px solid var(--sidebar-border);
        }
        div[data-testid="stSidebarHeader"] {
            border-bottom: 1px solid var(--sidebar-border);
            padding-bottom: 0.5rem;
        }
        /* Collapse icon */
        div[data-testid="stSidebarCollapseButton"] span {
            color: var(--sidebar-muted) !important;
        }
        a[data-testid="stSidebarNavLink"] {
            color: var(--sidebar-text) !important;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            margin: 0.15rem 0;
            transition: background-color 0.2s ease, color 0.2s ease;
            text-decoration: none;
        }
        /* Hover state */
        a[data-testid="stSidebarNavLink"]:hover {
            background-color: #6d6d6d;
        }
        /* Active page */
        a[data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: linear-gradient(135deg, #000108 0.000%, #091719 20.000%,
                                        #193036 40.000%, #304a4f 60.000%,
                                        #4e5f57 80.000%, #726e4a 100.000%);
            border-left: 4px solid var(--sidebar-active);
            font-weight: 600;
        }
        a[data-testid="stSidebarNavLink"] span {
            color: var(--sidebar-text) !important;
        }
        div[data-testid="stSidebarUserContent"] {
            border-top: 1px solid var(--sidebar-border);
            margin-top: 0.75rem;
            padding-top: 0.75rem;
        }
        .stApp {
            background: linear-gradient(to bottom, #f0f9ff 0%,#cbebff 47%,
            #a1dbff 100%);
            color: black;
        }
        .main-title {
            font_size: 1.2rem;
            font_weight: 800;
            color: #0f172a;
            margin-bottom: 0.2em;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #475569;
            margin_bottom: 2em;
            padding-bottom: 20px;
        }
        .aqi-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);

            border: 1px solid rgba(255, 255, 255, 0.25);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);

            padding: 1.5rem;
            
            border-radius: 16px;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.3s ease;
        }
        .aqi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0px 15px 35px rgba(0,0,0,0.1);
        }
        .hero {
            padding: 3rem 2rem;
            border-radius: 24px;
            background: linear-gradient(90deg, #07aeea 0.000%, #2bf598 100.000%);
            color: white;
            margin-bottom: 2rem;
        }
        .card-desc {
            color: #475569;
            margin-top: 0.5rem;
        }
        /* Label text */
        label {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
        }
        /* Text input box */
        input[type="text"] {
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 10px;
            font-size: 15px;
        }
        /* Focus effect */
        input[type="text"]:focus {
            border-color: #1abc9c;
            box-shadow: 0 0 5px rgba(26, 188, 156, 0.6);
            outline: none;
        }
        div.stButton > button {
                background-color: #1f77b4;
                color: white;
            }
        div.stButton > button:hover {
                background-color: #155a8a;
                transform: scale(1.03);
            }
                    div[data-testid="stToolbar"],
        .stAppToolbar {
            background: linear-gradient(to bottom,
                rgba(240,249,255,0.85) 0%,
                rgba(203,235,255,0.85) 47%,
                rgba(161,219,255,0.85) 100%);
            position: sticky;
            top: 0;
            z-index: 999;
            backdrop-filter: saturate(180%) blur(6px);
            transition: transform 0.3s ease;
        }
        </style>
        """, unsafe_allow_html=True)
        
