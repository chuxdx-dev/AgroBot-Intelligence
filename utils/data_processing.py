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
        processed['data_quality'] = self._assess_data_quality(current_data, historical_data)

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

    def _assess_data_quality(self, data, historical_data):
        """Assess the quality and freshness of sensor data"""
        quality = {
            'freshness': 'unknown',
            'completeness': 0,
            'reliability': 0,
            'last_update': None,
            'sensor_status': 'unknown'
        }

        if not data:
            quality['sensor_status'] = 'offline'
            return quality

        # Check data freshness with more granular assessment
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                time_diff = datetime.now(timestamp.tzinfo) - timestamp
                minutes_old = time_diff.total_seconds() / 60

                quality['last_update'] = f"{int(minutes_old)} minutes ago"

                if minutes_old < 5:
                    quality['freshness'] = 'excellent'
                    quality['sensor_status'] = 'online'
                elif minutes_old < 15:
                    quality['freshness'] = 'good'
                    quality['sensor_status'] = 'online'
                elif minutes_old < 60:
                    quality['freshness'] = 'fair'
                    quality['sensor_status'] = 'delayed'
                elif minutes_old < 360:  # 6 hours
                    quality['freshness'] = 'poor'
                    quality['sensor_status'] = 'intermittent'
                else:
                    quality['freshness'] = 'stale'
                    quality['sensor_status'] = 'offline'
            except:
                quality['freshness'] = 'unknown'
                quality['sensor_status'] = 'error'

        # Check data completeness with critical field weighting
        expected_fields = ['Temperature', 'Humidity', 'pH', 'Nitrogen', 'Phosphorus', 'Potassium', 'Conductivity', 'TDS']
        critical_fields = ['Temperature', 'Humidity', 'pH']  # Most important for AI recommendations

        present_fields = []
        critical_present = []

        for field in expected_fields:
            if field in data and data[field] is not None and str(data[field]).strip() != '':
                try:
                    # Validate that we can convert to float
                    float(data[field])
                    present_fields.append(field)
                    if field in critical_fields:
                        critical_present.append(field)
                except (ValueError, TypeError):
                    pass  # Skip invalid numeric data

        # Calculate weighted completeness (critical fields count more)
        base_completeness = (len(present_fields) / len(expected_fields)) * 100
        critical_completeness = (len(critical_present) / len(critical_fields)) * 100
        quality['completeness'] = (base_completeness * 0.6) + (critical_completeness * 0.4)

        # Enhanced reliability check with realistic ranges
        reliability_score = 100
        anomaly_count = 0

        for field in present_fields:
            try:
                value = float(data[field])

                # Check realistic ranges for agricultural sensors
                if field == 'Temperature':
                    if not (-20 <= value <= 70):  # Extended range for different climates
                        reliability_score -= 15
                        anomaly_count += 1
                    elif value < -10 or value > 55:  # Warning range
                        reliability_score -= 5

                elif field == 'Humidity':
                    if not (0 <= value <= 100):
                        reliability_score -= 15
                        anomaly_count += 1
                    elif value > 95 or value < 5:  # Extreme but possible
                        reliability_score -= 5

                elif field == 'pH':
                    if not (0 <= value <= 14):
                        reliability_score -= 20  # pH is critical
                        anomaly_count += 1
                    elif value < 3 or value > 11:  # Very unusual for soil
                        reliability_score -= 10

                elif field in ['Nitrogen', 'Phosphorus', 'Potassium']:
                    if value < 0 or value > 200:  # Unrealistic nutrient levels
                        reliability_score -= 10
                        anomaly_count += 1

                elif field == 'Conductivity':
                    if value < 0 or value > 5000:  # Extreme EC values
                        reliability_score -= 10
                        anomaly_count += 1

                elif field == 'TDS':
                    if value < 0 or value > 3000:  # Extreme TDS values
                        reliability_score -= 10
                        anomaly_count += 1

            except (ValueError, TypeError):
                reliability_score -= 15
                anomaly_count += 1

        # Cross-validation checks
        if 'Conductivity' in present_fields and 'TDS' in present_fields:
            try:
                conductivity = float(data['Conductivity'])
                tds = float(data['TDS'])
                # TDS should be roughly 0.5-0.7 times EC (in µS/cm to ppm conversion)
                expected_tds = conductivity * 0.65
                if abs(tds - expected_tds) > (expected_tds * 0.5):  # Allow 50% variance
                    reliability_score -= 8
            except:
                pass

        quality['reliability'] = max(0, min(100, reliability_score))
        quality['anomaly_count'] = anomaly_count

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