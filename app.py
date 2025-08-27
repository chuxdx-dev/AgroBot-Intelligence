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
        
        # Manual refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # System status in sidebar
        st.header("📊 System Status")
    
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
        
        # Display system overview in sidebar
        with st.sidebar:
            data_quality = processed_data.get('data_quality', {})
            freshness = data_quality.get('freshness', 'unknown')
            completeness = data_quality.get('completeness', 0)
            
            if freshness == 'excellent':
                st.success(f"✅ Data Quality: {completeness:.0f}%")
            elif freshness == 'good':
                st.info(f"ℹ️ Data Quality: {completeness:.0f}%")
            else:
                st.warning(f"⚠️ Data Quality: {completeness:.0f}%")
        
        # Critical alerts at the top
        alerts.display_critical_alerts(processed_data, weather_data)
        
        # Main tabbed interface
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🧠 AI Recommendations", 
            "🌤️ Weather Forecast", 
            "📍 Location & Map", 
            "📊 Analytics", 
            "📈 History & Reports"
        ])
        
        with tab1:
            st.header("🧠 AI Agricultural Recommendations")
            dashboard.display_recommendations(recommendations)
            
            # Quick sensor overview
            st.subheader("📊 Current Sensor Readings")
            dashboard.display_overview(processed_data, weather_data)
        
        with tab2:
            st.header("🌤️ Weather Information & Forecast")
            if weather_data:
                viz.display_weather_info(weather_data, forecast_data)
                
                # Weather vs sensor comparison
                st.subheader("🔍 Weather vs Sensor Analysis")
                viz.display_comparison_charts(processed_data, weather_data, forecast_data)
            else:
                st.warning("Weather data unavailable")
        
        with tab3:
            st.header("📍 Robot Location & Field Map")
            viz.display_location_map(lat, lon, weather_data)
            
            # Location details
            st.subheader("📍 Coordinates")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Latitude", f"{lat:.6f}°N")
            with col2:
                st.metric("Longitude", f"{lon:.6f}°E")
        
        with tab4:
            st.header("📊 Real-time Analytics")
            
            # Sensor gauges
            st.subheader("📊 Sensor Readings")
            viz.display_sensor_gauges(sensor_data)
            
            # Statistical analysis
            if processed_data.get('statistics'):
                st.subheader("📈 Statistical Analysis")
                stats = processed_data['statistics']
                
                # Create stats display
                for sensor, stat_data in stats.items():
                    with st.expander(f"📊 {sensor} Statistics"):
                        scol1, scol2, scol3 = st.columns(3)
                        with scol1:
                            st.metric("Average", f"{stat_data['mean']:.2f}")
                            st.metric("Minimum", f"{stat_data['min']:.2f}")
                        with scol2:
                            st.metric("Maximum", f"{stat_data['max']:.2f}")
                            st.metric("Std Dev", f"{stat_data['std']:.2f}")
                        with scol3:
                            st.metric("Median", f"{stat_data['median']:.2f}")
                            st.metric("Data Points", f"{stat_data['count']}")
        
        with tab5:
            st.header("📈 Historical Data & Reports")
            
            # Historical trends
            if not historical_data.empty:
                st.subheader("📈 Trend Analysis")
                viz.display_trend_charts(historical_data)
                
                # Trend summary
                trends = processed_data.get('trends', {})
                if trends:
                    st.subheader("📊 Trend Summary")
                    trend_data = []
                    for param, trend_info in trends.items():
                        trend_data.append({
                            'Parameter': param,
                            'Direction': trend_info['direction'].title(),
                            'Strength': f"{trend_info['strength']:.2f}",
                            'Recent Change': f"{trend_info['recent_change_pct']:.1f}%"
                        })
                    
                    trend_df = pd.DataFrame(trend_data)
                    st.dataframe(trend_df, use_container_width=True)
            else:
                st.warning("No historical data available for trend analysis")
            
            # Data export
            st.subheader("💾 Data Export")
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
