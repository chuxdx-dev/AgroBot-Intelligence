# AgriBot Intelligence - Smart Farming Dashboard

## Overview

AgriBot Intelligence is an AI-powered agricultural monitoring and decision support system that integrates real-time IoT sensor data with weather information to provide intelligent farming recommendations. The application serves as a comprehensive dashboard for smart farming operations, featuring real-time sensor monitoring, data visualization, alert management, and AI-driven agricultural insights.

The system combines IoT sensor readings (temperature, humidity, pH, nutrients) with weather data to generate actionable recommendations for irrigation, fertilization, timing, and risk assessment. It's designed to help farmers optimize crop conditions and make data-driven agricultural decisions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application providing an interactive dashboard interface
- **Component Structure**: Modular design with separate components for dashboard display, visualizations, and alert systems
- **Visualization Engine**: Plotly for interactive charts and gauges, Folium for mapping capabilities
- **Layout**: Wide layout with sidebar controls and multi-column metric displays

### Backend Architecture
- **Service Layer**: Modular service architecture with dedicated classes for different data sources and processing
- **Data Processing**: Centralized data processor handling sensor data analysis, statistics, trend detection, and anomaly identification
- **AI Engine**: Agricultural intelligence system providing crop recommendations based on sensor and weather data
- **Caching**: Streamlit resource caching for service initialization to improve performance

### Data Sources and Integration
- **IoT Integration**: ThingSpeak API integration for real-time sensor data collection
  - 8-field sensor setup: Temperature, Humidity, pH, Nitrogen, Phosphorus, Potassium, Conductivity, TDS
  - GPS coordinates for location-based analysis
- **Weather Integration**: OpenWeatherMap API for current weather conditions and forecasting
- **Data Processing**: Real-time data analysis with statistical calculations, trend analysis, and anomaly detection

### Alert and Monitoring System
- **Multi-tier Alert System**: Critical, warning, and informational alerts based on configurable thresholds
- **Smart Thresholds**: Crop-specific optimal ranges and critical thresholds for different parameters
- **Real-time Monitoring**: Continuous assessment of sensor readings against agricultural best practices

### AI and Analytics
- **Recommendation Engine**: AI-powered system generating specific recommendations for:
  - Irrigation scheduling and water management
  - Fertilization timing and nutrient management
  - Optimal timing for farming activities
  - Risk assessment and mitigation strategies
- **Data Analytics**: Statistical analysis, trend detection, and anomaly identification
- **Quality Assessment**: Data quality monitoring and validation

## External Dependencies

### APIs and Services
- **ThingSpeak API**: IoT data collection platform for sensor readings
  - Requires: THINGSPEAK_READ_API_KEY environment variable
  - Channel ID: 2957131 (configured for 8-field sensor setup)
- **OpenWeatherMap API**: Weather data and forecasting service
  - Requires: OPENWEATHERMAP_API_KEY environment variable
  - Provides current weather, forecasts, and atmospheric conditions

### Python Libraries
- **Streamlit**: Web application framework and UI components
- **Plotly**: Interactive data visualization (graph_objects, express)
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing and array operations
- **Folium**: Geographic mapping and location visualization
- **Requests**: HTTP client for API communications

### Environment Configuration
- Environment variables required for API authentication
- GPS coordinates hardcoded for Lagos, Nigeria region (6.6018, 3.3515)
- Configurable sensor field mappings and alert thresholds