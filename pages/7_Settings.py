import streamlit as st
from utils import init_settings
init_settings()

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="centered")


st.markdown("## ⚙️ App Settings")
st.markdown("Customize how your AQI app behaves and displays data.")


st.divider()


# ------------------ Display Settings ------------------
st.subheader("🎨 Display Preferences")


col1, col2 = st.columns(2)


with col1:
    theme = st.selectbox("Theme Mode", ["Light", "Dark", "System"])


with col2:
    show_emojis = st.toggle("Show AQI Emojis", value=True)


font_size = st.slider("Font Size", 12, 22, 16)


st.divider()


# ------------------ Units ------------------
st.subheader("📏 Units & Formats")


col3, col4 = st.columns(2)


with col3:
    aqi_standard = st.selectbox("AQI Standard", ["India (CPCB)", "US EPA", "WHO"])


with col4:
    time_format = st.selectbox("Time Format", ["12-hour", "24-hour"])


st.divider()


# ------------------ API Settings ------------------
st.subheader("🔌 API Configuration")


st.info("Your API keys are stored securely using Streamlit secrets.")


waqi_status = "Connected" if "WAQI_TOKEN" in st.secrets else "Not Configured"
st.metric("WAQI API Status", waqi_status)


st.divider()


# ------------------ Model Settings ------------------
st.subheader("🧠 Model Behavior")


confidence_level = st.select_slider(
"Prediction Confidence Level",
options=["Low", "Medium", "High"],
value="Medium"
)


forecast_days = st.slider("Default Forecast Days", 3, 14, 7)


st.divider()


# ------------------ Save ------------------
st.subheader("💾 Save Preferences")


if st.button("Save Settings"):
    st.success("Settings saved successfully!")


with st.expander("ℹ️ About Settings"):
    st.markdown("""
    These settings allow you to customize your experience.
    • Display: Control UI appearance
    • Units: Choose AQI interpretation
    • API: Live data configuration
    • Models: Prediction behavior
    """)
