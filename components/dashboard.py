import streamlit as st
import pandas as pd
from datetime import datetime
import json

class Dashboard:
    def __init__(self):
        self.status_colors = {
            'excellent': '🟢',
            'good': '🟡', 
            'fair': '🟠',
            'poor': '🔴',
            'unknown': '⚪'
        }
    
    def display_overview(self, processed_data, weather_data):
        """Display overview dashboard with key metrics"""
        st.header("🌟 System Overview")
        
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        current_data = processed_data.get('current', {})
        data_quality = processed_data.get('data_quality', {})
        
        with col1:
            temp = current_data.get('Temperature', 0)
            temp_color = '🟢' if 20 <= temp <= 30 else '🟡' if 15 <= temp <= 35 else '🔴'
            st.metric(
                label="🌡️ Temperature",
                value=f"{temp:.1f}°C",
                delta=None
            )
            st.markdown(f"{temp_color} Status: {'Optimal' if 20 <= temp <= 30 else 'Monitor'}")
        
        with col2:
            humidity = current_data.get('Humidity', 0)
            humidity_color = '🟢' if 40 <= humidity <= 70 else '🟡' if 30 <= humidity <= 80 else '🔴'
            st.metric(
                label="💧 Soil Moisture",
                value=f"{humidity:.1f}%",
                delta=None
            )
            st.markdown(f"{humidity_color} Status: {'Good' if 40 <= humidity <= 70 else 'Action Needed'}")
        
        with col3:
            ph = current_data.get('pH', 7.0)
            ph_color = '🟢' if 6.0 <= ph <= 7.5 else '🟡' if 5.5 <= ph <= 8.0 else '🔴'
            st.metric(
                label="⚗️ Soil pH",
                value=f"{ph:.1f}",
                delta=None
            )
            st.markdown(f"{ph_color} Status: {'Optimal' if 6.0 <= ph <= 7.5 else 'Adjust'}")
        
        with col4:
            freshness = data_quality.get('freshness', 'unknown')
            freshness_icon = self.status_colors.get(freshness, '⚪')
            completeness = data_quality.get('completeness', 0)
            st.metric(
                label="📊 Data Quality",
                value=f"{completeness:.0f}%",
                delta=None
            )
            st.markdown(f"{freshness_icon} Freshness: {freshness.title()}")
        
        # Weather integration row
        if weather_data:
            st.markdown("---")
            st.subheader("🌤️ Current Weather Conditions")
            
            wcol1, wcol2, wcol3, wcol4 = st.columns(4)
            
            with wcol1:
                st.metric("Air Temperature", f"{weather_data.get('temperature', 0):.1f}°C")
            
            with wcol2:
                st.metric("Air Humidity", f"{weather_data.get('humidity', 0):.0f}%")
            
            with wcol3:
                st.metric("Wind Speed", f"{weather_data.get('wind_speed', 0):.1f} m/s")
            
            with wcol4:
                rainfall = weather_data.get('rainfall_1h', 0)
                st.metric("Rainfall (1h)", f"{rainfall:.1f} mm")
            
            st.markdown(f"**Conditions:** {weather_data.get('description', 'Unknown').title()}")
    
    def display_recommendations(self, recommendations):
        """Display AI-generated recommendations"""
        if not recommendations:
            st.warning("No recommendations available")
            return
        
        # Priority sorting
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        for category, recs in recommendations.items():
            if recs:
                st.subheader(f"📋 {category.replace('_', ' ').title()}")
                
                for rec in sorted(recs, key=lambda x: priority_order.get(x.get('priority', 'low'), 3)):
                    priority = rec.get('priority', 'low')
                    
                    if priority == 'high':
                        st.error(f"🚨 **{rec.get('action', 'Action required')}**")
                    elif priority == 'medium':
                        st.warning(f"⚠️ **{rec.get('action', 'Recommended action')}**")
                    else:
                        st.info(f"💡 **{rec.get('action', 'Suggestion')}**")
                    
                    st.markdown(f"**Reason:** {rec.get('reason', 'Analysis-based recommendation')}")
                    
                    if 'timing' in rec:
                        st.markdown(f"**Timing:** {rec['timing']}")
                    
                    if 'mitigation' in rec:
                        st.markdown(f"**Mitigation:** {rec['mitigation']}")
                    
                    st.markdown("---")
    
    def display_export_options(self, processed_data, weather_data):
        """Display data export options"""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Sensor Data"):
                if processed_data.get('current'):
                    data_dict = processed_data['current'].copy()
                    df = pd.DataFrame([data_dict])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("📥 Download Full Report"):
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'sensor_data': processed_data.get('current', {}),
                    'weather_data': weather_data,
                    'data_quality': processed_data.get('data_quality', {}),
                    'statistics': processed_data.get('statistics', {}),
                    'anomalies': processed_data.get('anomalies', [])
                }
                
                json_str = json.dumps(report_data, indent=2, default=str)
                st.download_button(
                    label="Download JSON Report",
                    data=json_str,
                    file_name=f"agricultural_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # Display last update time
        current_data = processed_data.get('current', {})
        if 'timestamp' in current_data:
            st.markdown(f"**Last Update:** {current_data['timestamp']}")
