import streamlit as st
from utils import get_settings


st.set_page_config(page_title="Settings", page_icon="⚙️", layout="centered")


st.markdown("## ⚙️ App Settings")
st.markdown("Customize how your AQI app behaves and displays data.")

# Initialize defaults
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "show_grid" not in st.session_state:
    st.session_state.show_grid = True

if "forecast_days" not in st.session_state:
    st.session_state.forecast_days = 7

if "health_alerts" not in st.session_state:
    st.session_state.health_alerts = True

st.divider()
# ------------------ Display Settings ------------------
st.subheader("🎨 Display Preferences")

# -------------------
# Appearance
# -------------------

st.session_state.theme = st.radio(
    "Theme Mode",
    ["Light", "Dark"],
    index=0 if st.session_state.theme == "Light" else 1
)

st.divider()
# -------------------
# Charts
# -------------------
st.subheader("📊 Charts")

st.session_state.show_grid = st.checkbox(
    "Show Grid on Charts",
    value=st.session_state.show_grid
)

st.divider()
# -------------------
# Forecast
# -------------------
st.subheader("🔮 Forecast")

st.session_state.forecast_days = st.slider(
    "Default Forecast Days",
    3, 14,
    st.session_state.forecast_days
)

st.divider()
# -------------------
# Health Alerts
# -------------------
st.subheader("🚨 Health Alerts")

st.session_state.health_alerts = st.toggle(
    "Enable Health Alerts",
    value=st.session_state.health_alerts
)

st.divider()
# -------------------
# Debug Panel
# -------------------
with st.expander("🧪 Debug: Current Settings"):
    st.json({
        "Theme": st.session_state.theme,
        "Show Grid": st.session_state.show_grid,
        "Forecast Days": st.session_state.forecast_days,
        "Health Alerts": st.session_state.health_alerts
    })


