import pytest
import tempfile
import os
from app import create_app, db
from app.models.user import User
from app.models.grievance import Grievance

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret'
    }
    
    app = create_app('testing')
    app.config.update(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            name='Test User',
            email='test@example.com',
            location='Test Location',
            preferred_language='en'
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers for API requests."""
    response = client.post('/api/auth/login', json={
        'email': sample_user.email,
        'password': 'testpassword123'
    })
    
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
