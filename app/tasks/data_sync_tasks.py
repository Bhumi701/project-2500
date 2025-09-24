from app.celery_setup import celery
from app.models.blog import BlogPost
from app.services.weather_service import WeatherService
from app.utils.cache import cache
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@celery.task
def sync_weather_data():
    """Sync and cache weather data for major locations"""
    try:
        weather_service = WeatherService()
        
        # Major agricultural districts in Kerala
        locations = [
            'Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha',
            'Kottayam', 'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad',
            'Malappuram', 'Kozhikode', 'Wayanad', 'Kannur', 'Kasaragod'
        ]
        
        synced_count = 0
        
        for location in locations:
            try:
                # Get current weather
                current_weather = weather_service.get_current_weather(location)
                
                if current_weather:
                    # Cache weather data
                    cache_key = f"weather:{location}"
                    cache.set(cache_key, current_weather, timeout=1800)  # 30 minutes
                    
                    # Get forecast
                    forecast = weather_service.get_forecast(location)
                    if forecast:
                        forecast_key = f"forecast:{location}"
                        cache.set(forecast_key, forecast, timeout=3600)  # 1 hour
                    
                    synced_count += 1
                    
            except Exception as e:
                logger.error(f"Weather sync error for {location}: {str(e)}")
                continue
        
        logger.info(f"Weather data synced for {synced_count} locations")
        return {'status': 'success', 'synced_locations': synced_count}
        
    except Exception as e:
        logger.error(f"Weather sync task error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

@celery.task
def sync_policy_data():
    """Sync government policies and schemes"""
    try:
        # This would fetch from government APIs
        # For now, we'll update sample data
        
        policies = [
            {
                'title': 'Kerala Agricultural Development Scheme 2024',
                'description': 'Financial assistance for farmers to adopt modern farming techniques',
                'category': 'Financial Support',
                'language': 'en',
                'last_updated': datetime.utcnow()
            },
            {
                'title': 'കേരള കാർഷിക വികസന പദ്ധതി 2024',
                'description': 'ആധുനിക കാർഷിക രീതികൾ സ്വീകരിക്കുന്നതിനുള്ള സാമ്പത്തിക സഹായം',
                'category': 'Financial Support',
                'language': 'ml',
                'last_updated': datetime.utcnow()
            }
        ]
        
        # Cache policies
        for lang in ['en', 'ml']:
            lang_policies = [p for p in policies if p['language'] == lang]
            cache_key = f"policies:{lang}"
            cache.set(cache_key, lang_policies, timeout=3600)
        
        logger.info("Policy data synced successfully")
        return {'status': 'success', 'policies_synced': len(policies)}
        
    except Exception as e:
        logger.error(f"Policy sync task error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

@celery.task
def cleanup_old_chat_sessions():
    """Clean up old chat sessions"""
    try:
        from app.models.chat import ChatSession
        
        # Delete chat sessions older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_sessions = ChatSession.query.filter(
            ChatSession.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        for session in old_sessions:
            db.session.delete(session)
            deleted_count += 1
        
        db.session.commit()
        
        logger.info(f"Cleaned up {deleted_count} old chat sessions")
        return {'status': 'success', 'deleted_sessions': deleted_count}
        
    except Exception as e:
        logger.error(f"Chat cleanup task error: {str(e)}")
        db.session.rollback()
        return {'status': 'failed', 'error': str(e)}