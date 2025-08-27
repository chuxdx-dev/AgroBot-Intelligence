import streamlit as st
from datetime import datetime, timedelta

class AlertSystem:
    def __init__(self):
        self.alert_thresholds = {
            'temperature': {'critical_low': 10, 'low': 15, 'high': 35, 'critical_high': 40},
            'humidity': {'critical_low': 20, 'low': 30, 'high': 80, 'critical_high': 90},
            'ph': {'critical_low': 4.5, 'low': 5.5, 'high': 8.0, 'critical_high': 9.0},
            'nitrogen': {'critical_low': 5, 'low': 15},
            'phosphorus': {'critical_low': 5, 'low': 10},
            'potassium': {'critical_low': 5, 'low': 15}
        }
    
    def display_critical_alerts(self, processed_data, weather_data):
        """Display critical alerts and warnings"""
        alerts = self._generate_alerts(processed_data, weather_data)
        
        if not alerts:
            st.success("✅ All systems operating within normal parameters")
            return
        
        # Separate alerts by priority
        critical_alerts = [a for a in alerts if a['priority'] == 'critical']
        warning_alerts = [a for a in alerts if a['priority'] == 'warning']
        info_alerts = [a for a in alerts if a['priority'] == 'info']
        
        # Display critical alerts
        if critical_alerts:
            st.error("🚨 CRITICAL ALERTS")
            for alert in critical_alerts:
                st.error(f"**{alert['title']}**: {alert['message']}")
                if 'action' in alert:
                    st.markdown(f"⚡ **Immediate Action Required:** {alert['action']}")
        
        # Display warnings
        if warning_alerts:
            st.warning("⚠️ WARNINGS")
            for alert in warning_alerts:
                st.warning(f"**{alert['title']}**: {alert['message']}")
                if 'action' in alert:
                    st.markdown(f"📋 **Recommended Action:** {alert['action']}")
        
        # Display info alerts
        if info_alerts:
            st.info("💡 NOTIFICATIONS")
            for alert in info_alerts:
                st.info(f"**{alert['title']}**: {alert['message']}")
    
    def _generate_alerts(self, processed_data, weather_data):
        """Generate alerts based on sensor and weather data"""
        alerts = []
        
        if not processed_data.get('current'):
            return alerts
        
        current_data = processed_data['current']
        anomalies = processed_data.get('anomalies', [])
        data_quality = processed_data.get('data_quality', {})
        
        # Sensor-based alerts
        alerts.extend(self._check_sensor_alerts(current_data))
        
        # Data quality alerts
        alerts.extend(self._check_data_quality_alerts(data_quality))
        
        # Anomaly alerts
        alerts.extend(self._check_anomaly_alerts(anomalies))
        
        # Weather-based alerts
        if weather_data:
            alerts.extend(self._check_weather_alerts(weather_data, current_data))
        
        # System health alerts
        alerts.extend(self._check_system_health_alerts(current_data))
        
        return alerts
    
    def _check_sensor_alerts(self, data):
        """Check for sensor-based alerts"""
        alerts = []
        
        # Temperature alerts
        temp = data.get('Temperature', 25)
        if temp <= self.alert_thresholds['temperature']['critical_low']:
            alerts.append({
                'priority': 'critical',
                'title': 'Extreme Cold Temperature',
                'message': f'Temperature critically low at {temp:.1f}°C - crop damage possible',
                'action': 'Activate heating systems, protect sensitive plants'
            })
        elif temp >= self.alert_thresholds['temperature']['critical_high']:
            alerts.append({
                'priority': 'critical',
                'title': 'Extreme Heat Temperature',
                'message': f'Temperature critically high at {temp:.1f}°C - heat stress likely',
                'action': 'Increase irrigation, provide shade, improve ventilation'
            })
        elif temp <= self.alert_thresholds['temperature']['low']:
            alerts.append({
                'priority': 'warning',
                'title': 'Low Temperature Warning',
                'message': f'Temperature below optimal at {temp:.1f}°C',
                'action': 'Monitor closely, consider protection measures'
            })
        elif temp >= self.alert_thresholds['temperature']['high']:
            alerts.append({
                'priority': 'warning',
                'title': 'High Temperature Warning',
                'message': f'Temperature above optimal at {temp:.1f}°C',
                'action': 'Increase irrigation frequency, monitor plant stress'
            })
        
        # Soil moisture alerts
        humidity = data.get('Humidity', 50)
        if humidity <= self.alert_thresholds['humidity']['critical_low']:
            alerts.append({
                'priority': 'critical',
                'title': 'Severe Drought Conditions',
                'message': f'Soil moisture critically low at {humidity:.1f}%',
                'action': 'Emergency irrigation required immediately'
            })
        elif humidity <= self.alert_thresholds['humidity']['low']:
            alerts.append({
                'priority': 'warning',
                'title': 'Low Soil Moisture',
                'message': f'Soil moisture below optimal at {humidity:.1f}%',
                'action': 'Schedule irrigation within next few hours'
            })
        elif humidity >= self.alert_thresholds['humidity']['critical_high']:
            alerts.append({
                'priority': 'warning',
                'title': 'Waterlogged Conditions',
                'message': f'Soil moisture very high at {humidity:.1f}% - risk of root rot',
                'action': 'Improve drainage, reduce irrigation'
            })
        
        # pH alerts
        ph = data.get('pH', 7.0)
        if ph <= self.alert_thresholds['ph']['critical_low']:
            alerts.append({
                'priority': 'critical',
                'title': 'Extremely Acidic Soil',
                'message': f'Soil pH critically low at {ph:.1f} - nutrient lockout likely',
                'action': 'Apply lime immediately to raise pH'
            })
        elif ph >= self.alert_thresholds['ph']['critical_high']:
            alerts.append({
                'priority': 'critical',
                'title': 'Extremely Alkaline Soil',
                'message': f'Soil pH critically high at {ph:.1f} - nutrient deficiency likely',
                'action': 'Apply sulfur or acidifying agents'
            })
        elif ph <= self.alert_thresholds['ph']['low'] or ph >= self.alert_thresholds['ph']['high']:
            alerts.append({
                'priority': 'warning',
                'title': 'Suboptimal Soil pH',
                'message': f'Soil pH at {ph:.1f} - outside optimal range (6.0-7.5)',
                'action': 'Plan pH adjustment for next maintenance cycle'
            })
        
        # Nutrient deficiency alerts
        nitrogen = data.get('Nitrogen', 20)
        phosphorus = data.get('Phosphorus', 15)
        potassium = data.get('Potassium', 20)
        
        if nitrogen <= self.alert_thresholds['nitrogen']['critical_low']:
            alerts.append({
                'priority': 'critical',
                'title': 'Severe Nitrogen Deficiency',
                'message': f'Nitrogen critically low at {nitrogen:.1f} ppm',
                'action': 'Apply nitrogen fertilizer immediately'
            })
        elif nitrogen <= self.alert_thresholds['nitrogen']['low']:
            alerts.append({
                'priority': 'warning',
                'title': 'Low Nitrogen Levels',
                'message': f'Nitrogen below optimal at {nitrogen:.1f} ppm',
                'action': 'Schedule nitrogen fertilization'
            })
        
        if phosphorus <= self.alert_thresholds['phosphorus']['critical_low']:
            alerts.append({
                'priority': 'warning',
                'title': 'Low Phosphorus Levels',
                'message': f'Phosphorus low at {phosphorus:.1f} ppm',
                'action': 'Consider phosphorus supplementation'
            })
        
        if potassium <= self.alert_thresholds['potassium']['critical_low']:
            alerts.append({
                'priority': 'warning',
                'title': 'Low Potassium Levels',
                'message': f'Potassium low at {potassium:.1f} ppm',
                'action': 'Apply potassium-rich fertilizer'
            })
        
        return alerts
    
    def _check_data_quality_alerts(self, data_quality):
        """Check for data quality issues"""
        alerts = []
        
        completeness = data_quality.get('completeness', 100)
        if completeness < 50:
            alerts.append({
                'priority': 'critical',
                'title': 'Sensor Data Incomplete',
                'message': f'Only {completeness:.0f}% of sensors reporting',
                'action': 'Check sensor connections and power supply'
            })
        elif completeness < 80:
            alerts.append({
                'priority': 'warning',
                'title': 'Some Sensors Offline',
                'message': f'{completeness:.0f}% sensor completeness',
                'action': 'Verify all sensors are functioning'
            })
        
        freshness = data_quality.get('freshness', 'good')
        if freshness == 'poor':
            alerts.append({
                'priority': 'critical',
                'title': 'Stale Sensor Data',
                'message': 'Sensor data is more than 1 hour old',
                'action': 'Check robot connectivity and sensor operation'
            })
        elif freshness == 'fair':
            alerts.append({
                'priority': 'warning',
                'title': 'Outdated Sensor Data',
                'message': 'Sensor data may be outdated',
                'action': 'Verify real-time data transmission'
            })
        
        return alerts
    
    def _check_anomaly_alerts(self, anomalies):
        """Check for statistical anomalies"""
        alerts = []
        
        for anomaly in anomalies:
            if anomaly.get('severity') == 'high':
                alerts.append({
                    'priority': 'warning',
                    'title': f'Unusual {anomaly["field"]} Reading',
                    'message': f'{anomaly["field"]} at {anomaly["current_value"]:.1f} is significantly different from normal patterns',
                    'action': 'Verify sensor calibration and inspect field conditions'
                })
        
        return alerts
    
    def _check_weather_alerts(self, weather_data, sensor_data):
        """Check for weather-related alerts"""
        alerts = []
        
        wind_speed = weather_data.get('wind_speed', 0)
        if wind_speed > 20:  # m/s (about 72 km/h)
            alerts.append({
                'priority': 'critical',
                'title': 'High Wind Alert',
                'message': f'Wind speed at {wind_speed:.1f} m/s - avoid spraying operations',
                'action': 'Postpone pesticide/fertilizer applications, secure equipment'
            })
        elif wind_speed > 10:
            alerts.append({
                'priority': 'warning',
                'title': 'Moderate Wind Warning',
                'message': f'Wind speed at {wind_speed:.1f} m/s - may affect spray operations',
                'action': 'Use caution with spray applications'
            })
        
        rainfall = weather_data.get('rainfall_1h', 0)
        if rainfall > 10:
            alerts.append({
                'priority': 'info',
                'title': 'Heavy Rainfall Detected',
                'message': f'Current rainfall at {rainfall:.1f} mm/h',
                'action': 'Skip irrigation, monitor for flooding'
            })
        
        # Temperature differential alert
        air_temp = weather_data.get('temperature', 25)
        soil_temp = sensor_data.get('Temperature', 25)
        temp_diff = abs(air_temp - soil_temp)
        
        if temp_diff > 15:
            alerts.append({
                'priority': 'info',
                'title': 'Large Temperature Differential',
                'message': f'Air ({air_temp:.1f}°C) and soil ({soil_temp:.1f}°C) temperatures differ significantly',
                'action': 'Monitor for rapid temperature changes'
            })
        
        return alerts
    
    def _check_system_health_alerts(self, data):
        """Check for overall system health issues"""
        alerts = []
        
        # High conductivity alert
        conductivity = data.get('Conductivity', 100)
        if conductivity > 300:
            alerts.append({
                'priority': 'warning',
                'title': 'High Soil Salinity',
                'message': f'Electrical conductivity high at {conductivity:.0f} µS/cm',
                'action': 'Increase leaching irrigation to reduce salt buildup'
            })
        
        # Check for sensor timestamp
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                time_diff = datetime.now(timestamp.tzinfo) - timestamp
                
                if time_diff > timedelta(hours=2):
                    alerts.append({
                        'priority': 'warning',
                        'title': 'Communication Issue',
                        'message': 'Robot has not reported data for over 2 hours',
                        'action': 'Check robot power and network connectivity'
                    })
            except:
                pass
        
        return alerts
