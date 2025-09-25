# ========================================
# app/api/weather.py
# ========================================

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.weather_service import WeatherService
from app.utils.decorators import cache_response
import logging
from app.extensions import db

weather_bp = Blueprint('weather', __name__)
logger = logging.getLogger(__name__)

@weather_bp.route('/', methods=['GET'])
@jwt_required()
@cache_response(timeout=1800)  # Cache for 30 minutes
def get_weather():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        location = request.args.get('location', user.location)
        weather_service = WeatherService()
        
        current_weather = weather_service.get_current_weather(location)
        forecast = weather_service.get_forecast(location, days=5)
        
        if not current_weather:
            return jsonify({'error': 'Weather data unavailable'}), 503
        
        return jsonify({
            'current': current_weather,
            'forecast': forecast,
            'location': location
        }), 200
        
    except Exception as e:
        logger.error(f"Weather API error: {str(e)}")
        return jsonify({'error': 'Weather service error'}), 500

@weather_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_weather_alerts():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        weather_service = WeatherService()
        alerts = weather_service.get_weather_alerts(user.location)
        
        return jsonify({'alerts': alerts}), 200
        
    except Exception as e:
        logger.error(f"Weather alerts error: {str(e)}")
        return jsonify({'error': 'Failed to fetch weather alerts'}), 500
