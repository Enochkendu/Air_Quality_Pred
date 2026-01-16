import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_settings, apply_theme

apply_theme()

st.set_page_config(page_title="Visualization", layout="centered")

st.title("Air Quality Visualization Dashboard")
data_vis_choice = st.selectbox("Which data would you like to visualize?", ("Historical data", "Custom data"))
if data_vis_choice == "Historical data":
    data = "data/station_day_with_station_info.csv"
else:
    uploaded_file = st.file_uploader("Upload Air Quality Data")
    if uploaded_file is None:
        st.write("No file uploaded yet...")
        st.stop()
    st.write(f"Thank you for uploading {uploaded_file.name} !")
    data = uploaded_file

df = pd.read_csv(data)
# df = df.dropna()
st.write(df)
st.write("---")



st.write("""### View The Average AQI for Each Month""")
df['Date'] = pd.to_datetime(df['Date'])
df['Month_Year'] = df['Date'].dt.to_period('M')

monthly_aqi = df.groupby('Month_Year')['AQI'].mean().reset_index(name="monthly_avg")
print(monthly_aqi.columns)
monthly_aqi["Month_Year"] = monthly_aqi["Month_Year"].dt.to_timestamp()


# Slider for filtering years
# Finding the min and max dates
min_date = monthly_aqi["Month_Year"].min().to_pydatetime()
max_date = monthly_aqi["Month_Year"].max().to_pydatetime()

# Create a date range slider in Streamlit
start_date, end_date = st.slider(
    "Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM"
)

# Filter the dataframe based on the slider
filtered_df = monthly_aqi[
    (monthly_aqi["Month_Year"] >= start_date) &
    (monthly_aqi["Month_Year"] <= end_date)
    ]

# Create the line_chart based on the filtered dataframe
st.line_chart(filtered_df.set_index("Month_Year")["monthly_avg"])


st.write("---") # Separate different section with a line


"""# MONTHLY POLLUTANT VISUALIZATION"""
st.write("""### View The Average pollutant value for Each Month""")
# 1. Convert Month_Year to datetime
# --- POLLUTANTS MONTHLY DATA ---
pollutant_df = df.copy()

pollutants = [
    'PM2.5', 'PM10', 'NO', 'NO2', 'NOx',
     'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene'
]
# pollutant_df["Month_Year"] = pd.to_datetime(pollutant_df["Month_Year"], format="%Y-%m")

pollutant_df["Month_Year"] = pollutant_df["Month_Year"].dt.to_timestamp()

monthly_pollutants = (
    pollutant_df
    .groupby("Month_Year")[pollutants]
    .mean()
    .sort_index()
)


min_p, max_p = (
    monthly_pollutants.index.min().to_pydatetime(),
    monthly_pollutants.index.max().to_pydatetime()
)

# Create a drodown menu to choose to view ALL pollutants at once or an individual pollutant
pollutant_options = ["ALL"] + pollutants

selected_pollutant = st.selectbox(
    "Select pollutant",
    options=pollutant_options,
    index=0,  # default = ALL
    key="pollutant_selectbox"
)


p_start, p_end = st.slider(
    "Select pollutant month range",
    min_value=min_p,
    max_value=max_p,
    value=(min_p, max_p),
    format="YYYY-MM",
    key="pollutant_slider"  # IMPORTANT
)

filtered_pollutants = monthly_pollutants.loc[p_start:p_end]

#Create a condition to plot on a line_chart, whatever the user chooses
if selected_pollutant == "ALL":
    plot_df = filtered_pollutants
else:
    plot_df = filtered_pollutants[[selected_pollutant]]

st.line_chart(plot_df)


st.write("---") # Separate different section with a line



#"""CREATE A BAR CHART SHOWING THE FREQUENCY OF AIR QUALITIES IN THE AQI BUCKET"""
st.write("""### View how many times the air quality in your dataset was actually severe, moderate...""")
bar_plot = df.copy()
aqi_counts = (
    bar_plot["AQI_Bucket"]
    .value_counts()
    .sort_index()  # keeps logical bucket order if labels are sortable
    .to_frame(name="Count")
)

st.bar_chart(aqi_counts)


st.write("---")


#""" CREATING A BAR CHART TO VIEW AVERAGE AQI BY STATE"""
st.write("""### View Average AQI by State""")
state_aqi = df.groupby('State')['AQI'].mean().sort_values(ascending=False).to_frame(name="State AQI")
st.bar_chart(state_aqi)
