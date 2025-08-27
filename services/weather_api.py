import requests
import os
from datetime import datetime
import streamlit as st

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, lat, lon):
        """Fetch current weather conditions"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            weather_data = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'cloudiness': data['clouds']['all'],
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'uv_index': None,  # Would need separate UV index API call
                'timestamp': datetime.fromtimestamp(data['dt'])
            }
            
            # Add precipitation if available
            if 'rain' in data:
                weather_data['rainfall_1h'] = data['rain'].get('1h', 0)
            else:
                weather_data['rainfall_1h'] = 0
                
            return weather_data
            
        except requests.exceptions.RequestException as e:
            st.error(f"Network error fetching weather data: {e}")
            return None
        except Exception as e:
            st.error(f"Error processing weather data: {e}")
            return None
    
    def get_forecast(self, lat, lon, days=5):
        """Fetch weather forecast for the next few days"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data
            forecast_list = []
            for item in data['list'][:days*8]:  # 8 forecasts per day (3-hour intervals)
                forecast_item = {
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'description': item['weather'][0]['description'],
                    'wind_speed': item['wind']['speed'],
                    'cloudiness': item['clouds']['all'],
                    'rainfall': item.get('rain', {}).get('3h', 0)
                }
                forecast_list.append(forecast_item)
            
            return forecast_list
            
        except requests.exceptions.RequestException as e:
            st.error(f"Network error fetching forecast data: {e}")
            return []
        except Exception as e:
            st.error(f"Error processing forecast data: {e}")
            return []
    
    def get_uv_index(self, lat, lon):
        """Fetch UV index data (requires separate API call)"""
        try:
            url = f"{self.base_url}/uvi"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('value', 0)
            
        except Exception as e:
            st.warning(f"UV index data unavailable: {e}")
            return 0
