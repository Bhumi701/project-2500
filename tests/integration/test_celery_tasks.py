import pytest
from unittest.mock import Mock, patch
from app.tasks.email_tasks import send_welcome_email, send_grievance_notification
from app.models.user import User
from app.models.grievance import Grievance
from app.extensions import db

class TestEmailTasks:
    @patch('app.services.notification_service.NotificationService.send_welcome_email')
    def test_send_welcome_email_task(self, mock_send_email, app):
        """Test welcome email task."""
        with app.app_context():
            mock_send_email.return_value = True
            
            result = send_welcome_email.apply(args=['test@example.com', 'Test User'])
            
            assert result.result['status'] == 'success'
            mock_send_email.assert_called_once_with('test@example.com', 'Test User')

    @patch('app.services.notification_service.NotificationService.send_grievance_notification')
    def test_send_grievance_notification_task(self, mock_send_notification, app, sample_user):
        """Test grievance notification task."""
        with app.app_context():
            # Create a test grievance
            grievance = Grievance(
                user_id=sample_user.id,
                subject='Test Grievance',
                description='Test description',
                category='water_supply'
            )
            db.session.add(grievance)
            db.session.commit()
            
            mock_send_notification.return_value = True
            
            result = send_grievance_notification.apply(args=[grievance.id, 'Kerala'])
            
            assert result.result['status'] == 'success'
            mock_send_notification.assert_called_once()

