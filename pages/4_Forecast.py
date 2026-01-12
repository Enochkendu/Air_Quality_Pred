import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import forecast_next_days, load_forecast_model, make_forecast_feature, init_settings
init_settings()
st.title("🔮 AQI Forecast Using Historical Data")

@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_station_day_with_station_info.csv", parse_dates=["Date"])

df = load_data()

cities = sorted(df["City"].unique())
city = st.selectbox("Select City", cities)

days = st.slider("Forecast Days", 3, 14, 7)

if st.button("Generate Forecast"):
    city_df = df[df["City"] == city][["Date", "AQI"]].dropna()

    forecast = forecast_next_days(city, city_df, days)

    if forecast is None:
        st.error("No forecast model available for this city.")
    else:
        f_dates = [x[0] for x in forecast]
        f_values = [x[1] for x in forecast]

        hist_tail = city_df.tail(30)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(hist_tail["Date"], hist_tail["AQI"], label="Historical")
        ax.plot(f_dates, f_values, marker="o", label="Forecast")

        ax.set_title(f"{city} AQI Forecast")
        ax.set_xlabel("Date")
        ax.set_ylabel("AQI")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

        with st.expander("📅 Forecast Table"):
            table_df = pd.DataFrame({
                "Date": f_dates,
                "Predicted AQI": [round(x, 1) for x in f_values]
            })
            st.dataframe(table_df)
