import streamlit as st
from utils import get_settings, apply_theme

st.set_page_config(page_title="Insights", layout="centered")
apply_theme()


st.title("🤖 Model Insights")

st.markdown("""
### Models Used
- RandomForestRegressor → AQI prediction
- RandomForestClassifier → AQI category prediction

### Why Random Forest?
- Handles non-linearity
- Robust to noise
- Works well with environmental data

### Training Strategy
- City-specific models
- Time-based train/test split
- Feature engineering (lags, seasonality)
""")
