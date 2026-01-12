import streamlit as st
from utils import init_settings
init_settings()

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
