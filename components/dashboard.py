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
        
        current_data = processed_data.get('current', {})
        data_quality = processed_data.get('data_quality', {})
        
        # Primary sensor readings - First row
        st.subheader("📊 Current Sensor Readings")
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        # Nutrient levels - Second row
        st.subheader("🧪 Nutrient Levels (NPK)")
        ncol1, ncol2, ncol3, ncol4 = st.columns(4)
        
        with ncol1:
            nitrogen = current_data.get('Nitrogen', 0)
            nitrogen_color = '🟢' if nitrogen >= 20 else '🟡' if nitrogen >= 10 else '🔴'
            st.metric(
                label="🔵 Nitrogen (N)",
                value=f"{nitrogen:.1f} ppm",
                delta=None
            )
            st.markdown(f"{nitrogen_color} Status: {'Good' if nitrogen >= 20 else 'Low' if nitrogen >= 10 else 'Critical'}")
        
        with ncol2:
            phosphorus = current_data.get('Phosphorus', 0)
            phosphorus_color = '🟢' if 15 <= phosphorus <= 40 else '🟡' if 10 <= phosphorus <= 50 else '🔴'
            st.metric(
                label="🟠 Phosphorus (P)",
                value=f"{phosphorus:.1f} ppm",
                delta=None
            )
            st.markdown(f"{phosphorus_color} Status: {'Good' if 15 <= phosphorus <= 40 else 'Monitor'}")
        
        with ncol3:
            potassium = current_data.get('Potassium', 0)
            potassium_color = '🟢' if potassium >= 20 else '🟡' if potassium >= 10 else '🔴'
            st.metric(
                label="🟡 Potassium (K)",
                value=f"{potassium:.1f} ppm",
                delta=None
            )
            st.markdown(f"{potassium_color} Status: {'Good' if potassium >= 20 else 'Low' if potassium >= 10 else 'Critical'}")
        
        with ncol4:
            # NPK Balance Score
            npk_score = 0
            if nitrogen > 0 and phosphorus > 0 and potassium > 0:
                n_score = min(nitrogen/30*100, 100)
                p_score = min(phosphorus/25*100, 100)
                k_score = min(potassium/30*100, 100)
                npk_score = (n_score + p_score + k_score) / 3
            
            npk_color = '🟢' if npk_score >= 70 else '🟡' if npk_score >= 40 else '🔴'
            st.metric(
                label="⚖️ NPK Balance",
                value=f"{npk_score:.0f}%",
                delta=None
            )
            st.markdown(f"{npk_color} Status: {'Balanced' if npk_score >= 70 else 'Needs Attention'}")
        
        # Soil conductivity - Third row
        st.subheader("⚡ Soil Conductivity & Salts")
        scol1, scol2, scol3, scol4 = st.columns(4)
        
        with scol1:
            conductivity = current_data.get('Conductivity', 0)
            conductivity_color = '🟢' if conductivity < 200 else '🟡' if conductivity < 300 else '🔴'
            st.metric(
                label="⚡ Conductivity",
                value=f"{conductivity:.0f} µS/cm",
                delta=None
            )
            st.markdown(f"{conductivity_color} Status: {'Normal' if conductivity < 200 else 'High' if conductivity < 300 else 'Very High'}")
        
        with scol2:
            tds = current_data.get('TDS', 0)
            tds_color = '🟢' if tds < 150 else '🟡' if tds < 250 else '🔴'
            st.metric(
                label="🧂 TDS",
                value=f"{tds:.0f} ppm",
                delta=None
            )
            st.markdown(f"{tds_color} Status: {'Normal' if tds < 150 else 'Elevated' if tds < 250 else 'High'}")
        
        with scol3:
            # Soil health composite score
            health_factors = []
            if 6.0 <= ph <= 7.5: health_factors.append(25)
            elif 5.5 <= ph <= 8.0: health_factors.append(15)
            else: health_factors.append(0)
            
            if 40 <= humidity <= 70: health_factors.append(25)
            elif 30 <= humidity <= 80: health_factors.append(15)
            else: health_factors.append(0)
            
            if conductivity < 200: health_factors.append(25)
            elif conductivity < 300: health_factors.append(15)
            else: health_factors.append(0)
            
            if npk_score >= 70: health_factors.append(25)
            elif npk_score >= 40: health_factors.append(15)
            else: health_factors.append(0)
            
            soil_health = sum(health_factors)
            health_color = '🟢' if soil_health >= 80 else '🟡' if soil_health >= 60 else '🔴'
            
            st.metric(
                label="🌱 Soil Health",
                value=f"{soil_health}%",
                delta=None
            )
            st.markdown(f"{health_color} Status: {'Excellent' if soil_health >= 80 else 'Good' if soil_health >= 60 else 'Needs Improvement'}")
        
        with scol4:
            # Last sensor update
            if 'timestamp' in current_data:
                from datetime import datetime
                try:
                    timestamp = datetime.fromisoformat(current_data['timestamp'].replace('Z', '+00:00'))
                    time_ago = datetime.now(timestamp.tzinfo) - timestamp
                    minutes_ago = int(time_ago.total_seconds() / 60)
                    
                    update_color = '🟢' if minutes_ago < 10 else '🟡' if minutes_ago < 30 else '🔴'
                    st.metric(
                        label="🕐 Last Update",
                        value=f"{minutes_ago} min ago",
                        delta=None
                    )
                    st.markdown(f"{update_color} Status: {'Real-time' if minutes_ago < 10 else 'Recent' if minutes_ago < 30 else 'Delayed'}")
                except:
                    st.metric(label="🕐 Last Update", value="Unknown", delta=None)
                    st.markdown("⚪ Status: Unknown")
            else:
                st.metric(label="🕐 Last Update", value="No data", delta=None)
                st.markdown("🔴 Status: No timestamp")
        
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
