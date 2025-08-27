import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class DataProcessor:
    def __init__(self):
        self.sensor_fields = [
            'Temperature', 'Humidity', 'pH', 'Nitrogen', 
            'Phosphorus', 'Potassium', 'Conductivity', 'TDS'
        ]
    
    def process_sensor_data(self, current_data, historical_data):
        """Process and analyze sensor data"""
        if not current_data:
            return {}
        
        processed = {
            'current': current_data,
            'statistics': {},
            'trends': {},
            'anomalies': [],
            'data_quality': {}
        }
        
        # Calculate statistics from historical data
        if not historical_data.empty:
            processed['statistics'] = self._calculate_statistics(historical_data)
            processed['trends'] = self._analyze_trends(historical_data)
            processed['anomalies'] = self._detect_anomalies(current_data, historical_data)
        
        # Assess data quality
        processed['data_quality'] = self._assess_data_quality(current_data)
        
        return processed
    
    def _calculate_statistics(self, df):
        """Calculate statistical measures for sensor data"""
        stats = {}
        
        for field in self.sensor_fields:
            if field in df.columns:
                field_data = df[field].dropna()
                if len(field_data) > 0:
                    stats[field] = {
                        'mean': float(field_data.mean()),
                        'median': float(field_data.median()),
                        'std': float(field_data.std()),
                        'min': float(field_data.min()),
                        'max': float(field_data.max()),
                        'q25': float(field_data.quantile(0.25)),
                        'q75': float(field_data.quantile(0.75)),
                        'count': int(len(field_data))
                    }
        
        return stats
    
    def _analyze_trends(self, df):
        """Analyze trends in sensor data over time"""
        trends = {}
        
        if len(df) < 3:
            return trends
        
        for field in self.sensor_fields:
            if field in df.columns:
                field_data = df[field].dropna()
                if len(field_data) >= 3:
                    # Simple linear trend analysis
                    x = np.arange(len(field_data))
                    y = field_data.values
                    
                    # Calculate correlation coefficient
                    correlation = np.corrcoef(x, y)[0, 1] if len(y) > 1 else 0
                    
                    # Calculate recent change (last 24 hours vs previous period)
                    if len(field_data) >= 10:
                        recent_mean = field_data.tail(5).mean()
                        previous_mean = field_data.iloc[-10:-5].mean()
                        change_pct = ((recent_mean - previous_mean) / previous_mean) * 100
                    else:
                        change_pct = 0
                    
                    trends[field] = {
                        'direction': 'increasing' if correlation > 0.1 else 'decreasing' if correlation < -0.1 else 'stable',
                        'strength': abs(correlation),
                        'recent_change_pct': float(change_pct),
                        'correlation': float(correlation)
                    }
        
        return trends
    
    def _detect_anomalies(self, current_data, historical_data):
        """Detect anomalies in current readings compared to historical data"""
        anomalies = []
        
        for field in self.sensor_fields:
            if field in current_data and field in historical_data.columns:
                current_value = current_data[field]
                historical_values = historical_data[field].dropna()
                
                if len(historical_values) >= 10:
                    mean_val = historical_values.mean()
                    std_val = historical_values.std()
                    
                    # Check for values beyond 2 standard deviations
                    if abs(current_value - mean_val) > 2 * std_val:
                        z_score = (current_value - mean_val) / std_val
                        anomalies.append({
                            'field': field,
                            'current_value': float(current_value),
                            'expected_range': [float(mean_val - 2*std_val), float(mean_val + 2*std_val)],
                            'z_score': float(z_score),
                            'severity': 'high' if abs(z_score) > 3 else 'medium'
                        })
        
        return anomalies
    
    def _assess_data_quality(self, data):
        """Assess the quality of sensor data"""
        quality = {
            'completeness': 0,
            'freshness': 'unknown',
            'issues': []
        }
        
        # Check completeness
        total_fields = len(self.sensor_fields)
        available_fields = sum(1 for field in self.sensor_fields if field in data and data[field] is not None)
        quality['completeness'] = (available_fields / total_fields) * 100
        
        # Check data freshness
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                time_diff = datetime.now(timestamp.tzinfo) - timestamp
                
                if time_diff.total_seconds() < 300:  # 5 minutes
                    quality['freshness'] = 'excellent'
                elif time_diff.total_seconds() < 1800:  # 30 minutes
                    quality['freshness'] = 'good'
                elif time_diff.total_seconds() < 3600:  # 1 hour
                    quality['freshness'] = 'fair'
                else:
                    quality['freshness'] = 'poor'
                    quality['issues'].append('Data is more than 1 hour old')
            except:
                quality['issues'].append('Invalid timestamp format')
        
        # Check for suspicious values
        for field, value in data.items():
            if field in self.sensor_fields and value is not None:
                if field == 'pH' and (value < 0 or value > 14):
                    quality['issues'].append(f'pH value out of valid range: {value}')
                elif field == 'Temperature' and (value < -50 or value > 60):
                    quality['issues'].append(f'Temperature value suspicious: {value}°C')
                elif field == 'Humidity' and (value < 0 or value > 100):
                    quality['issues'].append(f'Humidity value out of range: {value}%')
        
        return quality
    
    def calculate_agricultural_indices(self, data):
        """Calculate derived agricultural indices"""
        indices = {}
        
        if not data:
            return indices
        
        # Soil Fertility Index (simplified)
        n = data.get('Nitrogen', 0)
        p = data.get('Phosphorus', 0) 
        k = data.get('Potassium', 0)
        
        if n and p and k:
            # Normalize NPK values (0-100 scale)
            n_norm = min(n / 50 * 100, 100)
            p_norm = min(p / 40 * 100, 100)
            k_norm = min(k / 50 * 100, 100)
            
            indices['fertility_index'] = (n_norm + p_norm + k_norm) / 3
        
        # Soil Health Score
        ph = data.get('pH', 7.0)
        ph_score = 100 - abs(ph - 6.8) * 20  # Optimal pH around 6.8
        ph_score = max(0, min(100, ph_score))
        
        conductivity = data.get('Conductivity', 100)
        ec_score = 100 if conductivity < 200 else max(0, 100 - (conductivity - 200) / 10)
        
        indices['soil_health_score'] = (ph_score + ec_score) / 2
        
        # Water Stress Index
        humidity = data.get('Humidity', 50)
        temp = data.get('Temperature', 25)
        
        # Simple water stress calculation
        optimal_humidity = 60
        temp_factor = max(0, (temp - 30) / 10)  # Stress increases above 30°C
        humidity_factor = abs(humidity - optimal_humidity) / 30
        
        water_stress = min(100, (temp_factor + humidity_factor) * 50)
        indices['water_stress_index'] = water_stress
        
        return indices
