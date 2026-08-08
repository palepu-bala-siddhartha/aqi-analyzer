import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

def health_recommendation(aqi):
    if aqi <= 50:
        return "Good 🟢 - Air quality is satisfactory, no health concerns."
    elif aqi <= 100:
        return "Moderate 🟡 - Acceptable air quality, sensitive people should limit outdoor activity."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups 🟠 - Children and elderly should reduce outdoor activity."
    elif aqi <= 200:
        return "Unhealthy 🔴 - Everyone should limit prolonged outdoor activity."
    elif aqi <= 300:
        return "Very Unhealthy 🟣 - Avoid outdoor activity."
    else:
        return "Hazardous ⚫ - Stay indoors, serious health risk."

API_KEY = "bee7902c14902094082a0a06d73a09fa771228b7"
st.title("🌍 AQI Analyzer")
st.subheader("Compare Air Quality Between Two Cities")
c1 = st.text_input("Enter first city", key="city1")
c2 = st.text_input("Enter second city", key="city2")
b = st.radio("Select what you want to know", ["AQI", "Trendgraph", "Compare"])
a = st.button("Analyze")

if a:
    cities = [c1, c2]
    if c1 and c2:
        all_rows = []
        forecast_data = {}
        error_occurred = False
        for i in cities:
            try:
                url = f"https://api.waqi.info/feed/{i}/?token={API_KEY}"
                response = requests.get(url)
                data = response.json()
                city_data = {
                    "city": i,
                    "AQI": data["data"]["aqi"],
                    "PM25": data["data"]["iaqi"].get("pm25", {}).get("v", None),
                    "PM10": data["data"]["iaqi"].get("pm10", {}).get("v", None),
                    "NO2": data["data"]["iaqi"].get("no2", {}).get("v", None),
                    "dominant_pollutant": data["data"]["dominentpol"],
                    "Time": data["data"]["time"]["s"]
                }
                all_rows.append(city_data)
                forecast_data[i] = data["data"]["forecast"]["daily"]["pm25"]
            except:
                st.error(f"❌ Could not fetch data for '{i}'. Please check the city spelling and try again.")
                error_occurred = True

        if not error_occurred and len(all_rows) == 2:
            df = pd.DataFrame(all_rows)

            if b == "AQI":
                st.dataframe(df)
                for i in range(len(cities)):
                    st.write(f"**{df.iloc[i]['city'].upper()}:** {health_recommendation(df.iloc[i]['AQI'])}")

            elif b == "Trendgraph":
                for j in cities:
                    avg = []
                    date = []
                    for k in range(len(forecast_data[j])):
                        avg.append(forecast_data[j][k]["avg"])
                        date.append(forecast_data[j][k]["day"])
                    plt.figure()
                    plt.bar(date, avg)
                    plt.xticks(rotation=45, ha='right')
                    plt.title(f"{j} PM2.5 Forecast")
                    plt.xlabel("Date")
                    plt.ylabel("Avg PM2.5")
                    st.pyplot(plt)
                    plt.close()

            elif b == "Compare":
                st.dataframe(df)
                if df.iloc[0]["AQI"] < df.iloc[1]["AQI"]:
                    st.success(f"🌿 {df.iloc[0]['city']} has better air quality today!")
                else:
                    st.success(f"🌿 {df.iloc[1]['city']} has better air quality today!")
    else:
        st.warning("⚠️ Please enter both city names and press Enter!")