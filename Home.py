import streamlit as st
import pandas as pd
from utils import predict_aqi, get_settings, apply_theme
import datetime


# ------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Air Quality Intelligence",
    page_icon="🌍",
    layout="wide"
)

apply_theme()

# ------------- CUSTOM CSS ----------------
st.markdown("""
<style>

    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
    }

    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
    }


    .card-link {
        margin-top: 1rem;
        font-weight: 600;
        color: #2563eb;
    }

    .hero h1 {
        color: white;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .hero p {
        font-size: 1.2rem;
        opacity: 0.9;
    }

</style>
""", unsafe_allow_html=True)

# ---------- HERO SECTION ----------
st.markdown(
"""
<div class="hero">
<h1>🌫️ Air Quality Intelligence Platform</h1>
<p>Monitor • Predict • Compare • Forecast air quality using AI</p>
</div>
""",
unsafe_allow_html=True
)


# ---------- INTRO ----------
st.markdown("<div class='main-title'>Welcome</div>", unsafe_allow_html=True)
st.markdown(
"<div class='subtitle'>Your all-in-one platform for historical analysis, live monitoring, AI prediction, and forecasting of air quality.</div>",
unsafe_allow_html=True
)

# ---------- FEATURE CARDS ----------
st.markdown("""
<div class="card-grid">

  <div class="aqi-card">
    <div>
      <div class="card-title">🧪 Manual AQI Prediction</div>
      <div class="card-desc">Enter pollutant values and get instant AI predictions.</div>
    </div>
    <a class="card-link" href="/Manual_Prediction" target="_self">Go →</a>
  </div>

  <div class="aqi-card">
    <div>
      <div class="card-title">🔴 Live AQI</div>
      <div class="card-desc">View real-time air quality using live API integration.</div>
    </div>
    <a class="card-link" href="/Live_AQI" target="_self">Go →</a>
  </div>

  <div class="aqi-card">
    <div>
      <div class="card-title">📊 Historical vs Live</div>
      <div class="card-desc">Compare past air quality with current conditions.</div>
    </div>
    <a class="card-link" href="/Historical_vs_Live" target="_self">Go →</a>
  </div>

  <div class="aqi-card">
    <div>
      <div class="card-title">🔮 AQI Forecast</div>
      <div class="card-desc">AI-powered AQI predictions for upcoming days
      using the historical India data.
      </div>
    </div>
    <a class="card-link" href="/Forecast" target="_self">Go →</a>
  </div>
    <div class="aqi-card">
    <div>
      <div class="card-title">📉 Visualization</div>
      <div class="card-desc">AI-powered AQI predictions for upcoming days
      using the historical India data.
      </div>
    </div>
    <a class="card-link" href="/Visualization" target="_self">Go →</a>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div class="card-grid">

  <div class="aqi-card">
    <div>
      <div class="card-title">🤖 Project Model Insight </div>
      <div class="card-desc">veiw more Insights about the project.</div>
    </div>
    <a class="card-link" href="/Model_Insights" target="_self">Go →</a>
  </div>

  <div class="aqi-card">
    <div>
      <div class="card-title">ℹ️ About Project </div>
      <div class="card-desc">Know more about our project.</div>
    </div>
    <a class="card-link" href="/About" target="_self">Go →</a>
  </div>

  <div class="aqi-card">
    <div>
      <div class="card-title">⚙️ Settings</div>
      <div class="card-desc">Configure preferences, API keys, and display options.</div>
    </div>
    <a class="card-link" href="/Settings" target="_self">Go →</a>
  </div>


""", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""AI Track Project 9 - Air Quality prediction & Visualization
            Dashboard • AI-powered AQI Platform • Techcrush sponsored.""")

