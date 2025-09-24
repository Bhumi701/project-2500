import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = os.environ.get('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location: str) -> Optional[Dict]:
        """Get current weather data for location"""
        try:
            if not self.api_key:
                logger.error("Weather API key not configured")
                return None
            
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'uv_index': self._get_uv_index(data['coord']['lat'], data['coord']['lon']),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Current weather fetch error: {str(e)}")
            return None
    
    def get_forecast(self, location: str, days: int = 5) -> List[Dict]:
        """Get weather forecast for location"""
        try:
            if not self.api_key:
                return []
            
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecast = []
            
            # Group by day and get daily summary
            daily_data = {}
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                
                if date not in daily_data:
                    daily_data[date] = {
                        'temperatures': [],
                        'humidity': [],
                        'descriptions': [],
                        'wind_speeds': [],
                        'rain': 0
                    }
                
                daily_data[date]['temperatures'].append(item['main']['temp'])
                daily_data[date]['humidity'].append(item['main']['humidity'])
                daily_data[date]['descriptions'].append(item['weather'][0]['description'])
                daily_data[date]['wind_speeds'].append(item['wind']['speed'])
                
                if 'rain' in item:
                    daily_data[date]['rain'] += item['rain'].get('3h', 0)
            
            # Create daily forecast summary
            for date, day_data in list(daily_data.items())[:days]:
                forecast.append({
                    'date': date.isoformat(),
                    'day_name': date.strftime('%A'),
                    'min_temp': round(min(day_data['temperatures']), 1),
                    'max_temp': round(max(day_data['temperatures']), 1),
                    'avg_humidity': round(sum(day_data['humidity']) / len(day_data['humidity']), 1),
                    'description': max(set(day_data['descriptions']), key=day_data['descriptions'].count),
                    'wind_speed': round(sum(day_data['wind_speeds']) / len(day_data['wind_speeds']), 1),
                    'rainfall': round(day_data['rain'], 1),
                    'farming_advice': self._get_farming_advice(
                        min(day_data['temperatures']),
                        max(day_data['temperatures']),
                        day_data['rain']
                    )
                })
            
            return forecast
            
        except Exception as e:
            logger.error(f"Weather forecast error: {str(e)}")
            return []
    
    def get_weather_alerts(self, location: str) -> List[Dict]:
        """Get weather alerts for location"""
        try:
            # This would integrate with weather alert APIs
            # For now, return mock data based on current conditions
            current = self.get_current_weather(location)
            alerts = []
            
            if current:
                # Temperature-based alerts
                if current['temperature'] > 35:
                    alerts.append({
                        'type': 'heat_wave',
                        'severity': 'high',
                        'message': 'High temperature alert. Ensure adequate irrigation and shade for crops.',
                        'farming_advice': 'Increase watering frequency, provide shade, harvest early morning'
                    })
                
                # Humidity-based alerts
                if current['humidity'] > 85:
                    alerts.append({
                        'type': 'high_humidity',
                        'severity': 'medium',
                        'message': 'High humidity may increase disease risk.',
                        'farming_advice': 'Monitor for fungal diseases, ensure proper ventilation'
                    })
                
                # Wind-based alerts
                if current['wind_speed'] > 15:
                    alerts.append({
                        'type': 'strong_wind',
                        'severity': 'medium',
                        'message': 'Strong winds may damage crops.',
                        'farming_advice': 'Secure plant supports, avoid spraying pesticides'
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Weather alerts error: {str(e)}")
            return []
    
    def _get_uv_index(self, lat: float, lon: float) -> float:
        """Get UV index for coordinates"""
        try:
            url = f"{self.base_url}/uvi"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return round(data.get('value', 0), 1)
            
        except Exception as e:
            logger.error(f"UV index error: {str(e)}")
            return 0.0
    
    def _get_farming_advice(self, min_temp: float, max_temp: float, rainfall: float) -> str:
        """Generate farming advice based on weather conditions"""
        advice = []
        
        if max_temp > 35:
            advice.append("Provide shade and increase irrigation frequency")
        elif max_temp < 15:
            advice.append("Protect crops from cold, consider row covers")
        
        if rainfall > 20:
            advice.append("Ensure proper drainage, delay fertilizer application")
        elif rainfall < 1:
            advice.append("Increase irrigation, mulch to retain moisture")
        
        if min_temp < 10:
            advice.append("Protect sensitive crops from frost damage")
        
        return "; ".join(advice) if advice else "Favorable conditions for most farming activities"
