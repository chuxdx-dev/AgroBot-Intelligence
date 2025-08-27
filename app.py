import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import numpy as np

from services.thingspeak_api import ThingSpeakAPI
from services.weather_api import WeatherAPI
from services.agricultural_ai import AgriculturalAI
from utils.data_processing import DataProcessor
from components.dashboard import Dashboard
from components.visualizations import Visualizations
from components.alerts import AlertSystem

# Page configuration
st.set_page_config(
    page_title="AgriBot Intelligence - Smart Farming Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def initialize_services():
    thingspeak = ThingSpeakAPI()
    weather = WeatherAPI()
    ai = AgriculturalAI()
    processor = DataProcessor()
    dashboard = Dashboard()
    viz = Visualizations()
    alerts = AlertSystem()
    
    return thingspeak, weather, ai, processor, dashboard, viz, alerts

def main():
    # Initialize all services
    thingspeak, weather, ai, processor, dashboard, viz, alerts = initialize_services()
    
    # App header
    st.title("🌱 AgriBot Intelligence Dashboard")
    st.markdown("**AI-Powered Agricultural Intelligence with Real-time IoT Integration**")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🔧 Control Panel")
        auto_refresh = st.checkbox("Auto-refresh (5 min)", value=True)
        refresh_interval = st.slider("Refresh Interval (minutes)", 1, 30, 5)
        
        st.header("📊 Display Options")
        show_alerts = st.checkbox("Show Alerts", value=True)
        show_recommendations = st.checkbox("Show AI Recommendations", value=True)
        show_weather = st.checkbox("Show Weather Data", value=True)
        show_trends = st.checkbox("Show Historical Trends", value=True)
        
        # Manual refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Auto-refresh logic
    if auto_refresh:
        placeholder = st.empty()
        with placeholder:
            st.info(f"Auto-refreshing every {refresh_interval} minutes...")
            time.sleep(2)
            placeholder.empty()
    
    try:
        # Fetch real-time sensor data
        with st.spinner("Fetching real-time sensor data..."):
            sensor_data = thingspeak.get_latest_data()
            historical_data = thingspeak.get_historical_data(days=7)
        
        if not sensor_data:
            st.error("❌ Failed to fetch sensor data from ThingSpeak API")
            st.stop()
        
        # Extract GPS coordinates
        lat, lon = thingspeak.get_gps_coordinates()
        
        # Fetch weather data
        with st.spinner("Fetching weather forecast..."):
            weather_data = weather.get_current_weather(lat, lon)
            forecast_data = weather.get_forecast(lat, lon)
        
        # Process data
        processed_data = processor.process_sensor_data(sensor_data, historical_data)
        
        # Generate AI recommendations
        recommendations = ai.generate_recommendations(processed_data, weather_data, forecast_data)
        
        # Display alerts
        if show_alerts:
            alerts.display_critical_alerts(processed_data, weather_data)
        
        # Main dashboard
        dashboard.display_overview(processed_data, weather_data)
        
        # Create columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sensor data visualizations
            st.header("📊 Real-time Sensor Readings")
            viz.display_sensor_gauges(sensor_data)
            
            if show_trends:
                st.header("📈 Historical Trends")
                viz.display_trend_charts(historical_data)
        
        with col2:
            # Weather information
            if show_weather:
                st.header("🌤️ Weather Information")
                viz.display_weather_info(weather_data, forecast_data)
            
            # Location map
            st.header("📍 Robot Location")
            viz.display_location_map(lat, lon, weather_data)
        
        # AI Recommendations section
        if show_recommendations:
            st.header("🧠 AI Agricultural Recommendations")
            dashboard.display_recommendations(recommendations)
        
        # Comparison charts
        st.header("🔍 Weather vs Sensor Data Analysis")
        viz.display_comparison_charts(processed_data, weather_data, forecast_data)
        
        # Data export section
        st.header("💾 Data Export")
        dashboard.display_export_options(processed_data, weather_data)
        
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.error("Please check your API keys and network connection.")
    
    # Auto-refresh implementation
    if auto_refresh:
        time.sleep(refresh_interval * 60)
        st.rerun()

if __name__ == "__main__":
    main()
