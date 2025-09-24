from celery import current_app
from app.celery_setup import celery
from app.models.user import User
from app.models.grievance import Grievance
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3)
def send_welcome_email(self, user_email: str, user_name: str):
    """Send welcome email to new user"""
    try:
        notification_service = NotificationService()
        success = notification_service.send_welcome_email(user_email, user_name)
        
        if not success:
            raise Exception("Failed to send welcome email")
        
        logger.info(f"Welcome email sent successfully to {user_email}")
        return {'status': 'success', 'email': user_email}
        
    except Exception as e:
        logger.error(f"Welcome email task error: {str(e)}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries  # 2, 4, 8 seconds
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {'status': 'failed', 'email': user_email, 'error': str(e)}

@celery.task(bind=True, max_retries=3)
def send_grievance_notification(self, grievance_id: int, location: str):
    """Send grievance notification to officials"""
    try:
        grievance = Grievance.query.get(grievance_id)
        if not grievance:
            logger.error(f"Grievance not found: {grievance_id}")
            return {'status': 'failed', 'error': 'Grievance not found'}
        
        user = grievance.user
        grievance_data = {
            'id': grievance.id,
            'subject': grievance.subject,
            'description': grievance.description,
            'category': grievance.category,
            'priority': grievance.priority,
            'created_at': grievance.created_at.isoformat(),
            'user_name': user.name,
            'user_email': user.email,
            'user_phone': user.phone or 'Not provided',
            'user_location': user.location
        }
        
        notification_service = NotificationService()
        success = notification_service.send_grievance_notification(grievance_data, location)
        
        if not success:
            raise Exception("Failed to send grievance notification")
        
        logger.info(f"Grievance notification sent for ID: {grievance_id}")
        return {'status': 'success', 'grievance_id': grievance_id}
        
    except Exception as e:
        logger.error(f"Grievance notification task error: {str(e)}")
        
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {'status': 'failed', 'grievance_id': grievance_id, 'error': str(e)}

@celery.task
def send_daily_weather_alerts():
    """Send daily weather alerts to users"""
    try:
        from app.services.weather_service import WeatherService
        
        # Get all active users
        users = User.query.filter_by(is_active=True).all()
        weather_service = WeatherService()
        notification_service = NotificationService()
        
        sent_count = 0
        
        for user in users:
            try:
                # Get weather alerts for user location
                alerts = weather_service.get_weather_alerts(user.location)
                
                if alerts:
                    # Send alert email
                    success = notification_service.send_weather_alert(
                        user.email, 
                        user.name, 
                        alerts, 
                        user.location
                    )
                    
                    if success:
                        sent_count += 1
                        
            except Exception as e:
                logger.error(f"Weather alert error for user {user.id}: {str(e)}")
                continue
        
        logger.info(f"Weather alerts sent to {sent_count} users")
        return {'status': 'success', 'alerts_sent': sent_count}
        
    except Exception as e:
        logger.error(f"Daily weather alerts task error: {str(e)}")
        return {'status': 'failed', 'error': str(e)}
