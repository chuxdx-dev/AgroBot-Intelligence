import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class AgriculturalAI:
    def __init__(self):
        # Optimal ranges for different crops (this could be expanded with ML models)
        self.optimal_ranges = {
            'temperature': {'min': 20, 'max': 30, 'unit': '°C'},
            'humidity': {'min': 40, 'max': 70, 'unit': '%'},
            'ph': {'min': 6.0, 'max': 7.5, 'unit': 'pH'},
            'nitrogen': {'min': 20, 'max': 50, 'unit': 'ppm'},
            'phosphorus': {'min': 15, 'max': 40, 'unit': 'ppm'},
            'potassium': {'min': 20, 'max': 50, 'unit': 'ppm'}
        }
        
        # Critical thresholds for alerts
        self.critical_thresholds = {
            'temperature': {'very_low': 10, 'low': 15, 'high': 35, 'very_high': 40},
            'humidity': {'very_low': 20, 'low': 30, 'high': 80, 'very_high': 90},
            'ph': {'very_low': 4.5, 'low': 5.5, 'high': 8.0, 'very_high': 9.0}
        }
    
    def generate_recommendations(self, sensor_data, weather_data, forecast_data):
        """Generate AI-powered agricultural recommendations"""
        recommendations = {
            'irrigation': [],
            'fertilization': [],
            'timing': [],
            'risk_assessment': [],
            'general': []
        }
        
        if not sensor_data:
            return recommendations
        
        # Irrigation recommendations
        irrigation_recs = self._analyze_irrigation_needs(sensor_data, weather_data, forecast_data)
        recommendations['irrigation'].extend(irrigation_recs)
        
        # Fertilization recommendations
        fertilization_recs = self._analyze_fertilization_needs(sensor_data)
        recommendations['fertilization'].extend(fertilization_recs)
        
        # Timing recommendations
        timing_recs = self._analyze_optimal_timing(weather_data, forecast_data)
        recommendations['timing'].extend(timing_recs)
        
        # Risk assessment
        risk_recs = self._assess_agricultural_risks(sensor_data, weather_data, forecast_data)
        recommendations['risk_assessment'].extend(risk_recs)
        
        # General recommendations
        general_recs = self._generate_general_recommendations(sensor_data, weather_data)
        recommendations['general'].extend(general_recs)
        
        return recommendations
    
    def _analyze_irrigation_needs(self, sensor_data, weather_data, forecast_data):
        """Analyze irrigation requirements"""
        recommendations = []
        
        soil_humidity = sensor_data.get('Humidity', 0)
        air_humidity = weather_data.get('humidity', 50) if weather_data else 50
        
        # Check for upcoming rain
        upcoming_rain = 0
        if forecast_data:
            upcoming_rain = sum([f.get('rainfall', 0) for f in forecast_data[:8]])  # Next 24 hours
        
        if soil_humidity < 30:
            if upcoming_rain > 5:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Moderate irrigation recommended',
                    'reason': f'Soil moisture low ({soil_humidity:.1f}%) but rain expected ({upcoming_rain:.1f}mm)',
                    'timing': 'Wait for rain, then assess'
                })
            else:
                recommendations.append({
                    'priority': 'high',
                    'action': 'Immediate irrigation required',
                    'reason': f'Critically low soil moisture ({soil_humidity:.1f}%) with no rain expected',
                    'timing': 'Within next 2-4 hours'
                })
        elif soil_humidity < 45:
            recommendations.append({
                'priority': 'medium',
                'action': 'Light irrigation recommended',
                'reason': f'Soil moisture below optimal ({soil_humidity:.1f}%)',
                'timing': 'Early morning or evening'
            })
        elif upcoming_rain > 15:
            recommendations.append({
                'priority': 'low',
                'action': 'Skip irrigation',
                'reason': f'Heavy rain expected ({upcoming_rain:.1f}mm)',
                'timing': 'Monitor soil conditions after rain'
            })
        
        return recommendations
    
    def _analyze_fertilization_needs(self, sensor_data):
        """Analyze fertilization requirements based on NPK levels"""
        recommendations = []
        
        nitrogen = sensor_data.get('Nitrogen', 0)
        phosphorus = sensor_data.get('Phosphorus', 0)
        potassium = sensor_data.get('Potassium', 0)
        ph = sensor_data.get('pH', 7.0)
        
        # NPK analysis
        if nitrogen < 15:
            recommendations.append({
                'priority': 'high',
                'action': 'Nitrogen fertilization required',
                'reason': f'Nitrogen levels critically low ({nitrogen:.1f} ppm)',
                'timing': 'Apply nitrogen-rich fertilizer within 1-2 days'
            })
        elif nitrogen < 25:
            recommendations.append({
                'priority': 'medium',
                'action': 'Light nitrogen application recommended',
                'reason': f'Nitrogen levels below optimal ({nitrogen:.1f} ppm)',
                'timing': 'Next fertilization cycle'
            })
        
        if phosphorus < 10:
            recommendations.append({
                'priority': 'high',
                'action': 'Phosphorus supplementation needed',
                'reason': f'Phosphorus levels very low ({phosphorus:.1f} ppm)',
                'timing': 'Apply phosphorus fertilizer immediately'
            })
        elif phosphorus > 50:
            recommendations.append({
                'priority': 'low',
                'action': 'Reduce phosphorus applications',
                'reason': f'Phosphorus levels high ({phosphorus:.1f} ppm) - risk of runoff',
                'timing': 'Skip next phosphorus application'
            })
        
        if potassium < 15:
            recommendations.append({
                'priority': 'high',
                'action': 'Potassium fertilization required',
                'reason': f'Potassium levels low ({potassium:.1f} ppm)',
                'timing': 'Apply potassium-rich fertilizer'
            })
        
        # pH correction recommendations
        if ph < 6.0:
            recommendations.append({
                'priority': 'high',
                'action': 'Soil pH correction - add lime',
                'reason': f'Soil too acidic (pH {ph:.1f}) - affects nutrient uptake',
                'timing': 'Apply agricultural lime before next planting'
            })
        elif ph > 8.0:
            recommendations.append({
                'priority': 'high',
                'action': 'Soil pH correction - add sulfur',
                'reason': f'Soil too alkaline (pH {ph:.1f}) - reduces nutrient availability',
                'timing': 'Apply sulfur amendments gradually'
            })
        
        return recommendations
    
    def _analyze_optimal_timing(self, weather_data, forecast_data):
        """Analyze optimal timing for agricultural activities"""
        recommendations = []
        
        if not weather_data or not forecast_data:
            return recommendations
        
        current_temp = weather_data.get('temperature', 25)
        wind_speed = weather_data.get('wind_speed', 0)
        
        # Optimal spraying conditions
        if wind_speed > 15:  # km/h
            recommendations.append({
                'priority': 'high',
                'action': 'Avoid spraying operations',
                'reason': f'High wind speed ({wind_speed:.1f} km/h) - risk of drift',
                'timing': 'Wait for calmer conditions (<10 km/h)'
            })
        elif wind_speed < 5 and current_temp < 30:
            recommendations.append({
                'priority': 'low',
                'action': 'Optimal conditions for spraying',
                'reason': f'Low wind ({wind_speed:.1f} km/h) and moderate temperature',
                'timing': 'Current conditions favorable'
            })
        
        # Planting recommendations
        avg_temp = np.mean([f.get('temperature', 25) for f in forecast_data[:5]])
        if 18 <= avg_temp <= 28:
            recommendations.append({
                'priority': 'low',
                'action': 'Good conditions for planting',
                'reason': f'Average temperature optimal ({avg_temp:.1f}°C)',
                'timing': 'Next 2-3 days favorable'
            })
        
        return recommendations
    
    def _assess_agricultural_risks(self, sensor_data, weather_data, forecast_data):
        """Assess potential agricultural risks"""
        risks = []
        
        if not sensor_data:
            return risks
        
        # Temperature stress risks
        temp = sensor_data.get('Temperature', 25)
        if temp > 35:
            risks.append({
                'priority': 'high',
                'type': 'Heat Stress',
                'description': f'Extreme temperature ({temp:.1f}°C) - crop stress likely',
                'mitigation': 'Increase irrigation frequency, provide shade if possible'
            })
        elif temp < 15:
            risks.append({
                'priority': 'medium',
                'type': 'Cold Stress',
                'description': f'Low temperature ({temp:.1f}°C) - growth may slow',
                'mitigation': 'Monitor for frost, consider row covers'
            })
        
        # Disease risk assessment
        humidity = sensor_data.get('Humidity', 50)
        air_temp = weather_data.get('temperature', 25) if weather_data else 25
        
        if humidity > 70 and 20 <= air_temp <= 30:
            risks.append({
                'priority': 'medium',
                'type': 'Fungal Disease Risk',
                'description': 'High humidity and moderate temperatures favor fungal growth',
                'mitigation': 'Improve air circulation, consider preventive fungicide application'
            })
        
        # Nutrient deficiency risks
        ph = sensor_data.get('pH', 7.0)
        if ph < 5.5 or ph > 8.5:
            risks.append({
                'priority': 'high',
                'type': 'Nutrient Uptake Risk',
                'description': f'Extreme pH ({ph:.1f}) prevents optimal nutrient absorption',
                'mitigation': 'Immediate pH correction required'
            })
        
        # Weather-related risks
        if weather_data and forecast_data:
            total_rain = sum([f.get('rainfall', 0) for f in forecast_data])
            if total_rain > 50:
                risks.append({
                    'priority': 'medium',
                    'type': 'Waterlogging Risk',
                    'description': f'Heavy rain expected ({total_rain:.1f}mm) - potential flooding',
                    'mitigation': 'Ensure proper drainage, delay irrigation'
                })
        
        return risks
    
    def _generate_general_recommendations(self, sensor_data, weather_data):
        """Generate general agricultural recommendations"""
        recommendations = []
        
        # Soil health recommendations
        conductivity = sensor_data.get('Conductivity', 0)
        if conductivity > 200:
            recommendations.append({
                'priority': 'medium',
                'action': 'Monitor soil salinity',
                'reason': f'High electrical conductivity ({conductivity:.0f} µS/cm)',
                'timing': 'Increase leaching irrigation'
            })
        
        # Data quality recommendations
        timestamp = sensor_data.get('timestamp')
        if timestamp:
            time_diff = datetime.now() - datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            if time_diff.total_seconds() > 3600:  # More than 1 hour old
                recommendations.append({
                    'priority': 'low',
                    'action': 'Check sensor connectivity',
                    'reason': 'Sensor data is more than 1 hour old',
                    'timing': 'Verify robot and sensor operation'
                })
        
        return recommendations
