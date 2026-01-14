import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import train_city_models, get_settings

settings = get_settings()

st.write(f"Theme: {settings['theme']}")
st.write(f"Show Grid: {settings['show_grid']}")

st.set_page_config(page_title="AQI Forecasr", layout="wide")
st.title("🔮 AQI Forecast Using Historical Data")

@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_station_day_with_station_info.csv", parse_dates=["Date"])

df = load_data()

cities = sorted(df["City"].unique())
city = st.selectbox("Select City", cities)

default_days = st.session_state.get("forecast_days", 7)
days = st.slider("Forecast Days", 3, 14, default_days)


if st.button("Generate Forecast"):
    city_df = df[df["City"] == city].sort_values("Date").copy()

    if len(city_df) < 50:
        st.error("Not enough data for this city.")
    else:
        models = train_city_models(city, df)

        if models == (None, None):
            st.error("Model unavailable for this city.")
        else:
            reg, _ = models

            history = city_df.tail(30)
            aqi_series = list(city_df["AQI"].values)

            last_row = city_df.iloc[-1]
            pm25_lag = last_row["PM2.5"]
            pm10_lag = last_row["PM10"]

            forecast_values = []
            forecast_dates = []

            current_date = city_df["Date"].iloc[-1]

            for _ in range(days):
                next_date = current_date + pd.Timedelta(days=1)

                month = next_date.month
                dow = next_date.dayofweek

                X = [
                    last_row["PM2.5"],
                    last_row["PM10"],
                    last_row["NO2"],
                    last_row["SO2"],
                    last_row["CO"],
                    last_row["O3"],
                    month,
                    dow,
                    pm25_lag,
                    pm10_lag
                ]

                X = np.array(X).reshape(1, -1)
                next_aqi = reg.predict(X)[0]

                forecast_values.append(next_aqi)
                forecast_dates.append(next_date)

                pm25_lag = last_row["PM2.5"]
                pm10_lag = last_row["PM10"]
                current_date = next_date

    

            # Plot
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(history["Date"], history["AQI"], label="Historical")
            ax.plot(forecast_dates, forecast_values, marker="o", label="Forecast")

            ax.set_title(f"{city} AQI Forecast")
            ax.set_xlabel("Date")
            ax.set_ylabel("AQI")
            ax.legend()
            show_grid = st.session_state.get("show_grid", True)
            ax.grid(show_grid)

            st.pyplot(fig)

            with st.expander("📅 Forecast Table"):
                table_df = pd.DataFrame({
                    "Date": forecast_dates,
                    "Predicted AQI": [round(x, 1) for x in forecast_values]
                })
                st.dataframe(table_df)
