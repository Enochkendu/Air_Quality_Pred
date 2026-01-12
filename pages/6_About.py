import streamlit as st
from utils import init_settings
init_settings()

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
