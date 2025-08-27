import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np
from datetime import datetime, timedelta

class Visualizations:
    def __init__(self):
        self.colors = {
            'primary': '#2E8B57',
            'secondary': '#32CD32', 
            'warning': '#FFA500',
            'danger': '#DC143C',
            'info': '#4169E1'
        }
    
    def display_sensor_gauges(self, sensor_data):
        """Display sensor readings as gauge charts"""
        if not sensor_data:
            st.error("No sensor data available")
            return
        
        # Create gauge charts for key parameters
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature gauge
            temp = sensor_data.get('Temperature', 0)
            fig_temp = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = temp,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Temperature (°C)"},
                delta = {'reference': 25},
                gauge = {
                    'axis': {'range': [None, 50]},
                    'bar': {'color': self.colors['primary']},
                    'steps': [
                        {'range': [0, 20], 'color': "lightblue"},
                        {'range': [20, 30], 'color': "lightgreen"},
                        {'range': [30, 40], 'color': "yellow"},
                        {'range': [40, 50], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 35
                    }
                }
            ))
            fig_temp.update_layout(height=300)
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # pH gauge
            ph = sensor_data.get('pH', 7.0)
            fig_ph = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = ph,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Soil pH"},
                delta = {'reference': 6.8},
                gauge = {
                    'axis': {'range': [4, 10]},
                    'bar': {'color': self.colors['secondary']},
                    'steps': [
                        {'range': [4, 6], 'color': "orange"},
                        {'range': [6, 7.5], 'color': "lightgreen"},
                        {'range': [7.5, 10], 'color': "orange"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 8
                    }
                }
            ))
            fig_ph.update_layout(height=300)
            st.plotly_chart(fig_ph, use_container_width=True)
        
        with col2:
            # Humidity gauge
            humidity = sensor_data.get('Humidity', 0)
            fig_humidity = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = humidity,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Soil Moisture (%)"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': self.colors['info']},
                    'steps': [
                        {'range': [0, 30], 'color': "red"},
                        {'range': [30, 70], 'color': "lightgreen"},
                        {'range': [70, 100], 'color': "lightblue"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 25
                    }
                }
            ))
            fig_humidity.update_layout(height=300)
            st.plotly_chart(fig_humidity, use_container_width=True)
            
            # NPK combined gauge
            nitrogen = sensor_data.get('Nitrogen', 0)
            phosphorus = sensor_data.get('Phosphorus', 0)
            potassium = sensor_data.get('Potassium', 0)
            
            # Calculate overall NPK score
            npk_score = (min(nitrogen/30*100, 100) + min(phosphorus/25*100, 100) + min(potassium/30*100, 100)) / 3
            
            fig_npk = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = npk_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "NPK Fertility Score"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': self.colors['warning']},
                    'steps': [
                        {'range': [0, 40], 'color': "red"},
                        {'range': [40, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "lightgreen"}
                    ]
                }
            ))
            fig_npk.update_layout(height=300)
            st.plotly_chart(fig_npk, use_container_width=True)
        
        # Display NPK breakdown
        st.subheader("🧪 Nutrient Analysis")
        ncol1, ncol2, ncol3 = st.columns(3)
        
        with ncol1:
            st.metric("Nitrogen (N)", f"{nitrogen:.1f} ppm", 
                     help="Essential for leaf growth and green color")
        
        with ncol2:
            st.metric("Phosphorus (P)", f"{phosphorus:.1f} ppm",
                     help="Important for root development and flowering")
        
        with ncol3:
            st.metric("Potassium (K)", f"{potassium:.1f} ppm",
                     help="Crucial for overall plant health and disease resistance")
        
        # Additional parameters
        st.subheader("⚡ Soil Conductivity")
        ecol1, ecol2 = st.columns(2)
        
        with ecol1:
            conductivity = sensor_data.get('Conductivity', 0)
            st.metric("Electrical Conductivity", f"{conductivity:.0f} µS/cm",
                     help="Indicates soil salinity and nutrient concentration")
        
        with ecol2:
            tds = sensor_data.get('TDS', 0)
            st.metric("Total Dissolved Solids", f"{tds:.0f} ppm",
                     help="Measure of dissolved nutrients and salts")
    
    def display_trend_charts(self, historical_data):
        """Display historical trend charts"""
        if historical_data.empty:
            st.warning("No historical data available for trend analysis")
            return
        
        # Time series for key parameters
        fig = go.Figure()
        
        # Temperature trend
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'],
            y=historical_data['Temperature'],
            mode='lines+markers',
            name='Temperature (°C)',
            line=dict(color=self.colors['danger'], width=2)
        ))
        
        fig.update_layout(
            title="Temperature Trend (Last 7 Days)",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # NPK trends
        fig_npk = go.Figure()
        
        fig_npk.add_trace(go.Scatter(
            x=historical_data['timestamp'],
            y=historical_data['Nitrogen'],
            mode='lines+markers',
            name='Nitrogen',
            line=dict(color='blue')
        ))
        
        fig_npk.add_trace(go.Scatter(
            x=historical_data['timestamp'],
            y=historical_data['Phosphorus'],
            mode='lines+markers',
            name='Phosphorus',
            line=dict(color='orange')
        ))
        
        fig_npk.add_trace(go.Scatter(
            x=historical_data['timestamp'],
            y=historical_data['Potassium'],
            mode='lines+markers',
            name='Potassium',
            line=dict(color='green')
        ))
        
        fig_npk.update_layout(
            title="NPK Nutrient Trends",
            xaxis_title="Time",
            yaxis_title="Concentration (ppm)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_npk, use_container_width=True)
        
        # Soil conditions correlation heatmap
        numeric_cols = ['Temperature', 'Humidity', 'pH', 'Nitrogen', 'Phosphorus', 'Potassium']
        correlation_data = historical_data[numeric_cols].corr()
        
        fig_corr = px.imshow(
            correlation_data,
            text_auto=True,
            aspect="auto",
            title="Soil Parameter Correlations",
            color_continuous_scale='RdBu_r'
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
    
    def display_weather_info(self, weather_data, forecast_data):
        """Display weather information and forecasts"""
        if not weather_data:
            st.warning("Weather data unavailable")
            return
        
        # Current weather display
        st.markdown(f"**Current Conditions:** {weather_data.get('description', 'Unknown').title()}")
        
        wcol1, wcol2 = st.columns(2)
        
        with wcol1:
            st.metric("🌡️ Air Temperature", f"{weather_data.get('temperature', 0):.1f}°C")
            st.metric("💨 Wind Speed", f"{weather_data.get('wind_speed', 0):.1f} m/s")
        
        with wcol2:
            st.metric("💧 Air Humidity", f"{weather_data.get('humidity', 0):.0f}%")
            st.metric("🌧️ Rainfall", f"{weather_data.get('rainfall_1h', 0):.1f} mm/h")
        
        # Weather forecast chart
        if forecast_data:
            st.subheader("📅 5-Day Weather Forecast")
            
            # Create forecast dataframe
            forecast_df = pd.DataFrame(forecast_data)
            
            # Temperature forecast
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=forecast_df['datetime'],
                y=forecast_df['temperature'],
                mode='lines+markers',
                name='Temperature Forecast',
                line=dict(color=self.colors['primary'])
            ))
            
            fig_temp.update_layout(
                title="Temperature Forecast",
                xaxis_title="Date/Time",
                yaxis_title="Temperature (°C)",
                height=300
            )
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # Rainfall forecast
            rainfall_data = [f.get('rainfall', 0) for f in forecast_data]
            if max(rainfall_data) > 0:
                fig_rain = go.Figure()
                fig_rain.add_trace(go.Bar(
                    x=forecast_df['datetime'],
                    y=rainfall_data,
                    name='Rainfall Forecast',
                    marker_color=self.colors['info']
                ))
                
                fig_rain.update_layout(
                    title="Rainfall Forecast",
                    xaxis_title="Date/Time",
                    yaxis_title="Rainfall (mm)",
                    height=300
                )
                st.plotly_chart(fig_rain, use_container_width=True)
    
    def display_location_map(self, lat, lon, weather_data):
        """Display robot location with weather overlay"""
        # Create folium map
        m = folium.Map(location=[lat, lon], zoom_start=12)
        
        # Add robot location marker
        weather_desc = weather_data.get('description', 'Unknown') if weather_data else 'Unknown'
        temp = weather_data.get('temperature', 0) if weather_data else 0
        
        popup_text = f"""
        <b>AgriBot Location</b><br>
        Coordinates: {lat:.4f}, {lon:.4f}<br>
        Weather: {weather_desc.title()}<br>
        Temperature: {temp:.1f}°C
        """
        
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip="AgriBot Current Location",
            icon=folium.Icon(color='green', icon='leaf', prefix='fa')
        ).add_to(m)
        
        # Add circle to show approximate working area
        folium.Circle(
            [lat, lon],
            radius=500,  # 500 meter radius
            popup="AgriBot Working Area",
            color='green',
            fill=True,
            fillOpacity=0.2
        ).add_to(m)
        
        # Display map
        folium_static(m, width=700, height=400)
        
        # Display coordinates
        st.markdown(f"**GPS Coordinates:** {lat:.6f}°N, {lon:.6f}°E")
    
    def display_comparison_charts(self, processed_data, weather_data, forecast_data):
        """Display comparison between weather predictions and sensor readings"""
        if not processed_data.get('current') or not weather_data:
            st.warning("Insufficient data for comparison analysis")
            return
        
        current_data = processed_data['current']
        
        # Temperature comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Air vs Soil temperature
            air_temp = weather_data.get('temperature', 25)
            soil_temp = current_data.get('Temperature', 25)
            
            fig_temp_comp = go.Figure()
            fig_temp_comp.add_trace(go.Bar(
                x=['Air Temperature', 'Soil Temperature'],
                y=[air_temp, soil_temp],
                marker_color=[self.colors['info'], self.colors['primary']],
                text=[f'{air_temp:.1f}°C', f'{soil_temp:.1f}°C'],
                textposition='auto'
            ))
            
            fig_temp_comp.update_layout(
                title="Air vs Soil Temperature",
                yaxis_title="Temperature (°C)",
                height=300
            )
            st.plotly_chart(fig_temp_comp, use_container_width=True)
        
        with col2:
            # Humidity comparison
            air_humidity = weather_data.get('humidity', 50)
            soil_humidity = current_data.get('Humidity', 50)
            
            fig_hum_comp = go.Figure()
            fig_hum_comp.add_trace(go.Bar(
                x=['Air Humidity', 'Soil Moisture'],
                y=[air_humidity, soil_humidity],
                marker_color=[self.colors['warning'], self.colors['secondary']],
                text=[f'{air_humidity:.1f}%', f'{soil_humidity:.1f}%'],
                textposition='auto'
            ))
            
            fig_hum_comp.update_layout(
                title="Air Humidity vs Soil Moisture",
                yaxis_title="Percentage (%)",
                height=300
            )
            st.plotly_chart(fig_hum_comp, use_container_width=True)
        
        # Weather impact analysis
        if forecast_data:
            st.subheader("🌦️ Weather Impact Analysis")
            
            # Calculate average forecast conditions
            avg_temp = np.mean([f.get('temperature', 25) for f in forecast_data[:8]])
            total_rainfall = sum([f.get('rainfall', 0) for f in forecast_data[:8]])
            
            impact_data = {
                'Parameter': ['Temperature Impact', 'Irrigation Need', 'Disease Risk', 'Work Conditions'],
                'Current Status': ['Moderate', 'Medium', 'Low', 'Good'],
                'Forecast Impact': [
                    'High' if avg_temp > 30 else 'Low' if avg_temp < 20 else 'Moderate',
                    'Low' if total_rainfall > 10 else 'High',
                    'High' if total_rainfall > 5 and avg_temp > 25 else 'Low',
                    'Poor' if total_rainfall > 15 else 'Good'
                ]
            }
            
            impact_df = pd.DataFrame(impact_data)
            st.dataframe(impact_df, use_container_width=True)
