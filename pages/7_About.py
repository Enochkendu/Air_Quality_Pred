import streamlit as st
from utils import get_settings, apply_theme

st.set_page_config(page_title="Insights", layout="centered")
apply_theme()

st.title("ℹ️ About This Project")

st.markdown("""
**Project Title:** Air Quality Monitoring & Prediction System  

**Tech Stack:**
- Python
- Scikit-Learn
- Streamlit
- Pandas

**Use Case:**
- Environmental monitoring
- Smart cities
- Public health awareness
""")
