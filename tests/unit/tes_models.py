import pytest
from app.models.user import User
from app.models.grievance import Grievance
from app.extensions import db

class TestUserModel:
    def test_user_creation(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(
                name='John Doe',
                email='john@example.com',
                location='Kerala',
                preferred_language='en'
            )
            user.set_password('securepassword')
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.name == 'John Doe'
            assert user.email == 'john@example.com'
            assert user.check_password('securepassword') is True
            assert user.check_password('wrongpassword') is False

    def test_user_to_dict(self, app, sample_user):
        """Test user serialization."""
        with app.app_context():
            user_dict = sample_user.to_dict()
            
            assert 'id' in user_dict
            assert user_dict['name'] == 'Test User'
            assert user_dict['email'] == 'test@example.com'
            assert 'password_hash' not in user_dict

class TestGrievanceModel:
    def test_grievance_creation(self, app, sample_user):
        """Test grievance creation."""
        with app.app_context():
            grievance = Grievance(
                user_id=sample_user.id,
                subject='Test Grievance',
                description='This is a test grievance description.',
                category='crop_insurance'
            )
            
            db.session.add(grievance)
            db.session.commit()
            
            assert grievance.id is not None
            assert grievance.subject == 'Test Grievance'
            assert grievance.status == 'pending'
            assert grievance.user_id == sample_user.id