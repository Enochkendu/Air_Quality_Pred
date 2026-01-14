import streamlit as st
import pandas as pd
from utils import predict_aqi, get_settings
import datetime


# ------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Air Quality Intelligence",
    page_icon="🌍",
    layout="wide"
)

# ------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .main-title {
        font_size: 3rem;
        font_weight: 800;
        color: #0f172a;
        margin-bottom: 0.2em;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #475569;
        margin_bottom: 2em;
    }
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
    }

    .aqi-card {
        background: #f1f5f9;
        padding: 1.5rem;
        border-radius: 16px;
        min-height: 180px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease;
    }

    .aqi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 15px 35px rgba(0,0,0,0.1);
    }

    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
    }

    .card-desc {
        color: #475569;
        margin-top: 0.5rem;
    }

    .card-link {
        margin-top: 1rem;
        font-weight: 600;
        color: #2563eb;
    }
    .hero {
        padding: 3rem 2rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        color: white;
        margin-bottom: 2rem;
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

</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div class="card-grid">

  <div class="aqi-card">
    <div>
      <div class="card-title"> Project Model Insight </div>
      <div class="card-desc">veiw more Insights about the project.</div>
    </div>
    <a class="card-link" href="/Model_Insights" target="_self">Go →</a>
  </div>

  <div class="aqi-card">
    <div>
      <div class="card-title">About Project </div>
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

