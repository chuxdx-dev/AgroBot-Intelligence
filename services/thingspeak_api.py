import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import streamlit as st

class ThingSpeakAPI:
    def __init__(self):
        self.base_url = "https://api.thingspeak.com"
        self.channel_id = "2957131"
        self.read_api_key = os.getenv("THINGSPEAK_READ_API_KEY", "")
        
        # Field mappings based on the actual ThingSpeak channel
        self.fields = {
            'field1': 'Temperature',
            'field2': 'Humidity',
            'field3': 'pH',
            'field4': 'Nitrogen',
            'field5': 'Phosphorus',
            'field6': 'Potassium',
            'field7': 'Conductivity',
            'field8': 'TDS'
        }
        
        # GPS coordinates from channel metadata
        self.latitude = 6.6018
        self.longitude = 3.3515
    
    def get_latest_data(self, results=1):
        """Fetch the latest sensor readings from ThingSpeak"""
        try:
            url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
            params = {
                'results': results,
                'api_key': self.read_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('feeds'):
                return None
            
            # Get the latest feed entry
            latest_feed = data['feeds'][-1]
            
            # Convert to structured format
            sensor_data = {}
            for field_key, field_name in self.fields.items():
                value = latest_feed.get(field_key)
                if value is not None:
                    sensor_data[field_name] = float(value)
            
            # Add timestamp
            sensor_data['timestamp'] = latest_feed.get('created_at')
            sensor_data['entry_id'] = latest_feed.get('entry_id')
            
            return sensor_data
            
        except requests.exceptions.RequestException as e:
            st.error(f"Network error fetching ThingSpeak data: {e}")
            return None
        except Exception as e:
            st.error(f"Error processing ThingSpeak data: {e}")
            return None
    
    def get_historical_data(self, days=7, results=100):
        """Fetch historical sensor data for trend analysis"""
        try:
            url = f"{self.base_url}/channels/{self.channel_id}/feeds.json"
            params = {
                'results': results,
                'api_key': self.read_api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('feeds'):
                return pd.DataFrame()
            
            # Convert to DataFrame
            feeds = data['feeds']
            df_data = []
            
            for feed in feeds:
                row = {'timestamp': pd.to_datetime(feed.get('created_at'))}
                
                for field_key, field_name in self.fields.items():
                    value = feed.get(field_key)
                    if value is not None:
                        row[field_name] = float(value)
                    else:
                        row[field_name] = None
                
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            # Handle timezone-aware comparison
            if not df.empty and len(df) > 0:
                # Convert cutoff_date to match DataFrame timezone
                if df['timestamp'].dtype.tz is not None:
                    import pytz
                    cutoff_date = cutoff_date.replace(tzinfo=pytz.UTC)
                df = df[df['timestamp'] >= cutoff_date]
            
            return df.sort_values('timestamp').reset_index(drop=True)
            
        except requests.exceptions.RequestException as e:
            st.error(f"Network error fetching historical data: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error processing historical data: {e}")
            return pd.DataFrame()
    
    def get_gps_coordinates(self):
        """Return the GPS coordinates of the robot/sensor location"""
        return self.latitude, self.longitude
    
    def get_channel_info(self):
        """Fetch channel metadata"""
        try:
            url = f"{self.base_url}/channels/{self.channel_id}.json"
            params = {'api_key': self.read_api_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            st.error(f"Error fetching channel info: {e}")
            return None
