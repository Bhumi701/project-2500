from flask_mail import Message
import flask_mail as Mail
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.sender_email = "noreply@agricultural-advisory.com"
    
    def send_welcome_email(self, recipient_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        try:
            msg = Message(
                subject="Welcome to Agricultural Advisory System",
                sender=self.sender_email,
                recipients=[recipient_email]
            )
            
            msg.body = f"""
            Dear {user_name},
            
            Welcome to our Agricultural Advisory System!
            
            Your account has been created successfully. You can now access:
            
            🌤️ Real-time weather updates and forecasts
            🤖 AI-powered agricultural advice in multiple languages
            📋 Government policies and schemes information
            💰 Current seed costs and market prices
            📝 Grievance submission system
            📚 Educational blog posts on farming techniques
            
            We're here to support your farming journey with the latest technology and expert advice.
            
            Happy farming!
            
            Best regards,
            Agricultural Advisory Team
            """
            
            msg.html = f"""
            <html>
            <body>
                <h2>Welcome to Agricultural Advisory System!</h2>
                <p>Dear {user_name},</p>
                
                <p>Your account has been created successfully. You now have access to:</p>
                
                <ul>
                    <li>🌤️ Real-time weather updates and forecasts</li>
                    <li>🤖 AI-powered agricultural advice in multiple languages</li>
                    <li>📋 Government policies and schemes information</li>
                    <li>💰 Current seed costs and market prices</li>
                    <li>📝 Grievance submission system</li>
                    <li>📚 Educational blog posts on farming techniques</li>
                </ul>
                
                <p>We're here to support your farming journey with the latest technology and expert advice.</p>
                
                <p><strong>Happy farming!</strong></p>
                
                <p>Best regards,<br>Agricultural Advisory Team</p>
            </body>
            </html>
            """
            
            mail.send(msg)
            logger.info(f"Welcome email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Welcome email error: {str(e)}")
            return False
    
    def send_grievance_notification(self, grievance_data: Dict, location: str) -> bool:
        """Send grievance notification to officials"""
        try:
            # Kerala Agricultural Department emails (example)
            official_emails = [
                "agriculture.grievance@kerala.gov.in",
                f"agriculture.{location.lower().replace(' ', '')}@kerala.gov.in"
            ]
            
            msg = Message(
                subject=f"New Agricultural Grievance: {grievance_data['subject']}",
                sender=self.sender_email,
                recipients=official_emails
            )
            
            msg.body = f"""
            New Agricultural Grievance Submitted
            
            Grievance ID: {grievance_data['id']}
            Subject: {grievance_data['subject']}
            Category: {grievance_data['category']}
            Priority: {grievance_data['priority']}
            Location: {location}
            
            Description:
            {grievance_data['description']}
            
            Farmer Details:
            Name: {grievance_data['user_name']}
            Email: {grievance_data['user_email']}
            Phone: {grievance_data['user_phone']}
            Location: {grievance_data['user_location']}
            
            Submitted on: {grievance_data['created_at']}
            
            Please review and take appropriate action.
            
            Agricultural Advisory System
            """
            
            mail.send(msg)
            logger.info(f"Grievance notification sent for ID: {grievance_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Grievance notification error: {str(e)}")
            return False

