
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
        """Generate AI-powered agricultural recommendations based on real data"""
        recommendations = {
            'irrigation': [],
            'fertilization': [],
            'timing': [],
            'risk_assessment': [],
            'general': []
        }
        
        # Extract current sensor readings with proper error handling
        current_data = sensor_data.get('current', {}) if sensor_data else {}
        
        if not current_data:
            recommendations['general'].append({
                'priority': 'high',
                'action': 'Check sensor connectivity',
                'reason': 'No sensor data available - unable to generate recommendations',
                'timing': 'Immediate'
            })
            return recommendations
        
        # Generate category-specific recommendations
        irrigation_recs = self._analyze_irrigation_needs(current_data, weather_data, forecast_data)
        recommendations['irrigation'].extend(irrigation_recs)
        
        fertilization_recs = self._analyze_fertilization_needs(current_data)
        recommendations['fertilization'].extend(fertilization_recs)
        
        timing_recs = self._analyze_optimal_timing(weather_data, forecast_data, current_data)
        recommendations['timing'].extend(timing_recs)
        
        risk_recs = self._assess_agricultural_risks(current_data, weather_data, forecast_data)
        recommendations['risk_assessment'].extend(risk_recs)
        
        general_recs = self._generate_general_recommendations(current_data, weather_data, sensor_data)
        recommendations['general'].extend(general_recs)
        
        return recommendations
    
    def _analyze_irrigation_needs(self, current_data, weather_data, forecast_data):
        """Analyze irrigation requirements based on real sensor and weather data"""
        recommendations = []
        
        soil_humidity = float(current_data.get('Humidity', 0))
        air_humidity = float(weather_data.get('humidity', 50)) if weather_data else 50
        current_temp = float(current_data.get('Temperature', 25))
        
        # Calculate upcoming rainfall from forecast
        upcoming_rain = 0
        if forecast_data and isinstance(forecast_data, list):
            for forecast in forecast_data[:8]:  # Next 24 hours (3-hour intervals)
                rain_key = 'rain' if 'rain' in forecast else 'precipitation'
                if rain_key in forecast:
                    if isinstance(forecast[rain_key], dict):
                        upcoming_rain += forecast[rain_key].get('3h', 0)
                    else:
                        upcoming_rain += float(forecast[rain_key])
        
        # Dynamic irrigation recommendations based on actual readings
        if soil_humidity < 25:
            if upcoming_rain > 10:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Light irrigation before expected rain',
                    'reason': f'Soil critically dry ({soil_humidity:.1f}%) but heavy rain expected ({upcoming_rain:.1f}mm)',
                    'timing': 'Light watering in 2-3 hours, then monitor rainfall'
                })
            else:
                priority = 'high' if current_temp > 28 else 'medium'
                recommendations.append({
                    'priority': priority,
                    'action': 'Immediate deep irrigation required',
                    'reason': f'Critical soil moisture ({soil_humidity:.1f}%), temp {current_temp:.1f}°C, minimal rain expected',
                    'timing': 'Within 1-2 hours - early morning or evening preferred'
                })
        
        elif soil_humidity < 40:
            if upcoming_rain > 5:
                recommendations.append({
                    'priority': 'low',
                    'action': 'Monitor soil conditions',
                    'reason': f'Soil moisture adequate ({soil_humidity:.1f}%) with rain expected ({upcoming_rain:.1f}mm)',
                    'timing': 'Check again after rainfall'
                })
            else:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Moderate irrigation recommended',
                    'reason': f'Soil moisture below optimal ({soil_humidity:.1f}%), no significant rain forecast',
                    'timing': 'Next 4-6 hours, preferably early morning'
                })
        
        elif soil_humidity > 75:
            recommendations.append({
                'priority': 'low',
                'action': 'Reduce or skip irrigation',
                'reason': f'Soil moisture high ({soil_humidity:.1f}%) - risk of waterlogging',
                'timing': 'Monitor drainage, avoid irrigation for 24-48 hours'
            })
        
        # Temperature-based irrigation adjustments
        if current_temp > 32 and soil_humidity < 50:
            recommendations.append({
                'priority': 'high',
                'action': 'Heat stress mitigation irrigation',
                'reason': f'High temperature ({current_temp:.1f}°C) with moderate soil moisture',
                'timing': 'Immediate light irrigation, then evening watering'
            })
        
        return recommendations
    
    def _analyze_fertilization_needs(self, current_data):
        """Dynamic fertilization analysis based on actual NPK readings"""
        recommendations = []
        
        nitrogen = float(current_data.get('Nitrogen', 0))
        phosphorus = float(current_data.get('Phosphorus', 0))
        potassium = float(current_data.get('Potassium', 0))
        ph = float(current_data.get('pH', 7.0))
        conductivity = float(current_data.get('Conductivity', 0))
        
        # Nitrogen analysis with dynamic thresholds
        if nitrogen < 10:
            recommendations.append({
                'priority': 'high',
                'action': 'Emergency nitrogen application',
                'reason': f'Severe nitrogen deficiency detected ({nitrogen:.1f} ppm) - crops at risk',
                'timing': 'Apply high-nitrogen fertilizer within 24 hours'
            })
        elif nitrogen < 20:
            recommendations.append({
                'priority': 'medium',
                'action': 'Nitrogen supplementation needed',
                'reason': f'Low nitrogen levels ({nitrogen:.1f} ppm) below optimal range (20-50 ppm)',
                'timing': 'Apply nitrogen-rich fertilizer within 2-3 days'
            })
        elif nitrogen > 60:
            recommendations.append({
                'priority': 'medium',
                'action': 'Reduce nitrogen inputs',
                'reason': f'Nitrogen levels excessive ({nitrogen:.1f} ppm) - environmental risk',
                'timing': 'Skip next nitrogen application, monitor growth'
            })
        
        # Phosphorus analysis
        if phosphorus < 8:
            recommendations.append({
                'priority': 'high',
                'action': 'Phosphorus fertilization critical',
                'reason': f'Extremely low phosphorus ({phosphorus:.1f} ppm) affects root development',
                'timing': 'Apply phosphorus fertilizer immediately'
            })
        elif phosphorus < 15:
            recommendations.append({
                'priority': 'medium',
                'action': 'Increase phosphorus application',
                'reason': f'Phosphorus below optimal ({phosphorus:.1f} ppm)',
                'timing': 'Next fertilization cycle'
            })
        elif phosphorus > 50:
            recommendations.append({
                'priority': 'low',
                'action': 'Reduce phosphorus applications',
                'reason': f'High phosphorus levels ({phosphorus:.1f} ppm) - runoff risk',
                'timing': 'Skip phosphorus in next 2 applications'
            })
        
        # Potassium analysis
        if potassium < 12:
            recommendations.append({
                'priority': 'high',
                'action': 'Potassium supplementation urgent',
                'reason': f'Critical potassium deficiency ({potassium:.1f} ppm) affects disease resistance',
                'timing': 'Apply potassium fertilizer within 48 hours'
            })
        elif potassium < 20:
            recommendations.append({
                'priority': 'medium',
                'action': 'Increase potassium levels',
                'reason': f'Low potassium ({potassium:.1f} ppm) may affect fruit quality',
                'timing': 'Next regular fertilization'
            })
        
        # pH-nutrient interaction analysis
        if ph < 5.8:
            recommendations.append({
                'priority': 'high',
                'action': 'Immediate soil pH correction with lime',
                'reason': f'Acidic soil (pH {ph:.2f}) severely limits nutrient uptake',
                'timing': 'Apply agricultural lime before any other fertilizers'
            })
        elif ph > 7.8:
            recommendations.append({
                'priority': 'high',
                'action': 'Lower soil pH with sulfur amendments',
                'reason': f'Alkaline soil (pH {ph:.2f}) reduces iron and phosphorus availability',
                'timing': 'Apply elemental sulfur, monitor pH weekly'
            })
        elif 5.8 <= ph <= 6.2:
            recommendations.append({
                'priority': 'medium',
                'action': 'Light lime application recommended',
                'reason': f'Slightly acidic pH ({ph:.2f}) - optimal range is 6.0-7.5',
                'timing': 'Light lime application in next month'
            })
        
        # Salinity considerations
        if conductivity > 250:
            recommendations.append({
                'priority': 'high',
                'action': 'Address soil salinity before fertilizing',
                'reason': f'High soil salinity ({conductivity:.0f} µS/cm) reduces fertilizer effectiveness',
                'timing': 'Increase leaching irrigation before next fertilizer application'
            })
        
        return recommendations
    
    def _analyze_optimal_timing(self, weather_data, forecast_data, current_data):
        """Dynamic timing recommendations based on real conditions"""
        recommendations = []
        
        if not weather_data:
            return recommendations
        
        current_temp = float(weather_data.get('temperature', 25))
        wind_speed = float(weather_data.get('wind_speed', 0)) * 3.6  # Convert m/s to km/h
        humidity_air = float(weather_data.get('humidity', 50))
        soil_temp = float(current_data.get('Temperature', current_temp))
        
        # Spraying conditions analysis
        if wind_speed > 20:
            recommendations.append({
                'priority': 'high',
                'action': 'Cancel all spraying operations',
                'reason': f'Dangerous wind speed ({wind_speed:.1f} km/h) - high drift risk',
                'timing': 'Wait for wind speeds below 15 km/h'
            })
        elif wind_speed > 15:
            recommendations.append({
                'priority': 'medium',
                'action': 'Postpone spraying operations',
                'reason': f'High wind speed ({wind_speed:.1f} km/h) may cause drift',
                'timing': 'Wait for calmer conditions (<10 km/h)'
            })
        elif 3 <= wind_speed <= 10 and current_temp < 28:
            recommendations.append({
                'priority': 'low',
                'action': 'Excellent spraying conditions',
                'reason': f'Optimal wind ({wind_speed:.1f} km/h) and temperature ({current_temp:.1f}°C)',
                'timing': 'Current conditions ideal for pesticide/herbicide application'
            })
        
        # Temperature-based timing
        if current_temp > 35:
            recommendations.append({
                'priority': 'high',
                'action': 'Avoid midday field operations',
                'reason': f'Extreme heat ({current_temp:.1f}°C) - equipment and crop stress',
                'timing': 'Limit activities to early morning (5-8 AM) or evening (6-8 PM)'
            })
        elif current_temp < 5:
            recommendations.append({
                'priority': 'medium',
                'action': 'Delay outdoor activities',
                'reason': f'Low temperature ({current_temp:.1f}°C) may damage equipment and crops',
                'timing': 'Wait for temperatures above 8°C'
            })
        
        # Planting window analysis
        if forecast_data and len(forecast_data) >= 5:
            avg_temp = np.mean([float(f.get('temperature', current_temp)) for f in forecast_data[:5]])
            temp_stability = np.std([float(f.get('temperature', current_temp)) for f in forecast_data[:5]])
            
            if 15 <= avg_temp <= 28 and temp_stability < 5:
                recommendations.append({
                    'priority': 'low',
                    'action': 'Favorable planting window',
                    'reason': f'Stable temperatures (avg {avg_temp:.1f}°C, variation ±{temp_stability:.1f}°C)',
                    'timing': 'Next 3-5 days optimal for planting operations'
                })
            elif temp_stability > 8:
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Wait for stable weather',
                    'reason': f'High temperature variation (±{temp_stability:.1f}°C) not ideal for planting',
                    'timing': 'Delay planting until weather stabilizes'
                })
        
        return recommendations
    
    def _assess_agricultural_risks(self, current_data, weather_data, forecast_data):
        """Dynamic risk assessment based on real-time data"""
        risks = []
        
        temp = float(current_data.get('Temperature', 25))
        humidity = float(current_data.get('Humidity', 50))
        ph = float(current_data.get('pH', 7.0))
        
        # Temperature stress analysis
        if temp > 38:
            risks.append({
                'priority': 'high',
                'type': 'Severe Heat Stress',
                'description': f'Extreme soil temperature ({temp:.1f}°C) - immediate crop damage likely',
                'mitigation': 'Emergency irrigation, shade cloth installation, harvest early if possible'
            })
        elif temp > 33:
            risks.append({
                'priority': 'medium',
                'type': 'Heat Stress Warning',
                'description': f'High soil temperature ({temp:.1f}°C) - monitor crop stress indicators',
                'mitigation': 'Increase irrigation frequency, provide midday shade, monitor plant wilting'
            })
        elif temp < 8:
            risks.append({
                'priority': 'high',
                'type': 'Frost Risk',
                'description': f'Low soil temperature ({temp:.1f}°C) - frost damage possible',
                'mitigation': 'Deploy frost protection measures, cover sensitive plants, monitor overnight'
            })
        
        # Disease risk modeling
        if weather_data:
            air_temp = float(weather_data.get('temperature', 25))
            air_humidity = float(weather_data.get('humidity', 50))
            
            # Fungal disease risk calculation
            if humidity > 75 and 18 <= air_temp <= 30 and air_humidity > 70:
                risk_score = ((humidity - 75) + (air_humidity - 70) + abs(air_temp - 24)) / 3
                risks.append({
                    'priority': 'high' if risk_score > 15 else 'medium',
                    'type': 'High Fungal Disease Risk',
                    'description': f'Optimal conditions for fungal growth (soil: {humidity:.1f}%, air: {air_humidity:.1f}%, temp: {air_temp:.1f}°C)',
                    'mitigation': 'Apply preventive fungicide, improve air circulation, reduce leaf wetness duration'
                })
            
            # Bacterial disease risk
            if humidity > 80 and air_temp > 25:
                risks.append({
                    'priority': 'medium',
                    'type': 'Bacterial Disease Risk',
                    'description': f'High moisture and temperature favor bacterial pathogens',
                    'mitigation': 'Avoid overhead irrigation, improve drainage, apply copper-based bactericide if needed'
                })
        
        # Nutrient lockout risk
        if ph < 5.0 or ph > 8.5:
            severity = 'high' if ph < 4.5 or ph > 9.0 else 'medium'
            risks.append({
                'priority': severity,
                'type': 'Severe Nutrient Lockout',
                'description': f'Extreme pH ({ph:.2f}) prevents nutrient absorption - crop failure risk',
                'mitigation': 'Emergency pH correction required, foliar feeding as temporary measure'
            })
        
        # Weather-related risks from forecast
        if forecast_data and len(forecast_data) > 0:
            total_rain = 0
            max_wind = 0
            min_temp = float('inf')
            
            for forecast in forecast_data[:8]:  # Next 24 hours
                rain_key = 'rain' if 'rain' in forecast else 'precipitation'
                if rain_key in forecast:
                    if isinstance(forecast[rain_key], dict):
                        total_rain += forecast[rain_key].get('3h', 0)
                    else:
                        total_rain += float(forecast.get(rain_key, 0))
                
                if 'wind_speed' in forecast:
                    max_wind = max(max_wind, float(forecast['wind_speed']) * 3.6)
                
                if 'temperature' in forecast:
                    min_temp = min(min_temp, float(forecast['temperature']))
            
            if total_rain > 75:
                risks.append({
                    'priority': 'high',
                    'type': 'Flood Risk',
                    'description': f'Excessive rainfall predicted ({total_rain:.1f}mm) - waterlogging likely',
                    'mitigation': 'Ensure drainage systems clear, harvest ready crops, protect equipment'
                })
            elif total_rain > 40:
                risks.append({
                    'priority': 'medium',
                    'type': 'Heavy Rain Warning',
                    'description': f'Heavy rainfall expected ({total_rain:.1f}mm) - field access may be limited',
                    'mitigation': 'Complete urgent field work now, prepare drainage, delay fertilizer applications'
                })
            
            if max_wind > 60:
                risks.append({
                    'priority': 'high',
                    'type': 'Storm Damage Risk',
                    'description': f'High winds predicted ({max_wind:.1f} km/h) - crop and equipment damage possible',
                    'mitigation': 'Secure loose equipment, provide crop support, avoid tall machinery operations'
                })
            
            if min_temp < 2:
                risks.append({
                    'priority': 'high',
                    'type': 'Freeze Warning',
                    'description': f'Freezing temperatures expected ({min_temp:.1f}°C) - crop damage likely',
                    'mitigation': 'Deploy frost protection, harvest sensitive crops, drain irrigation lines'
                })
        
        return risks
    
    def _generate_general_recommendations(self, current_data, weather_data, sensor_data):
        """Generate general recommendations based on overall system health"""
        recommendations = []
        
        conductivity = float(current_data.get('Conductivity', 0))
        tds = float(current_data.get('TDS', 0))
        
        # Salinity management
        if conductivity > 300:
            recommendations.append({
                'priority': 'high',
                'action': 'Critical salinity management needed',
                'reason': f'Very high soil salinity ({conductivity:.0f} µS/cm) - crop damage imminent',
                'timing': 'Begin heavy leaching irrigation immediately'
            })
        elif conductivity > 200:
            recommendations.append({
                'priority': 'medium',
                'action': 'Monitor and reduce soil salinity',
                'reason': f'Elevated soil salinity ({conductivity:.0f} µS/cm) may affect sensitive crops',
                'timing': 'Increase leaching irrigation over next week'
            })
        
        # TDS correlation check
        if abs(conductivity * 0.67 - tds) > 50:  # Expected correlation between EC and TDS
            recommendations.append({
                'priority': 'low',
                'action': 'Calibrate sensors',
                'reason': f'Conductivity ({conductivity:.0f}) and TDS ({tds:.0f}) readings inconsistent',
                'timing': 'Check sensor calibration at next maintenance'
            })
        
        # Data freshness analysis
        data_quality = sensor_data.get('data_quality', {}) if sensor_data else {}
        freshness = data_quality.get('freshness', 'unknown')
        completeness = data_quality.get('completeness', 0)
        
        if freshness in ['poor', 'unknown'] or completeness < 70:
            recommendations.append({
                'priority': 'medium',
                'action': 'Check sensor system health',
                'reason': f'Data quality concerns - freshness: {freshness}, completeness: {completeness:.0f}%',
                'timing': 'Inspect sensors and connectivity within 24 hours'
            })
        
        # Seasonal recommendations (if timestamp available)
        if 'timestamp' in current_data:
            try:
                from datetime import datetime
                timestamp = datetime.fromisoformat(current_data['timestamp'].replace('Z', '+00:00'))
                month = timestamp.month
                
                if month in [12, 1, 2]:  # Winter
                    recommendations.append({
                        'priority': 'low',
                        'action': 'Winter crop protection measures',
                        'reason': 'Winter season - consider cold-hardy varieties and protection',
                        'timing': 'Review cold protection strategies'
                    })
                elif month in [6, 7, 8]:  # Summer
                    recommendations.append({
                        'priority': 'low',
                        'action': 'Summer heat management',
                        'reason': 'Summer season - implement heat stress mitigation strategies',
                        'timing': 'Prepare shade structures and cooling systems'
                    })
            except:
                pass  # Skip seasonal recommendations if timestamp parsing fails
        
        return recommendations
