import pytest
import json

class TestAuthRoutes:
    def test_user_registration(self, client):
        """Test user registration endpoint."""
        user_data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'securepassword123',
            'location': 'Kerala',
            'preferred_language': 'en'
        }
        
        response = client.post('/api/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'testuser@example.com'

    def test_user_login(self, client, sample_user):
        """Test user login endpoint."""
        login_data = {
            'email': sample_user.email,
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == sample_user.email

    def test_get_profile(self, client, auth_headers):
        """Test get user profile endpoint."""
        response = client.get('/api/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data

class TestChatRoutes:
    def test_text_chat(self, client, auth_headers):
        """Test text chat endpoint."""
        chat_data = {
            'message': 'What fertilizer should I use for rice?',
            'language': 'en'
        }
        
        response = client.post('/api/chat/',
                             data=json.dumps(chat_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data
        assert 'session_id' in data

    def test_chat_sessions(self, client, auth_headers):
        """Test get chat sessions endpoint."""
        response = client.get('/api/chat/sessions', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'sessions' in data
        assert isinstance(data['sessions'], list)

class TestGrievanceRoutes:
    def test_submit_grievance(self, client, auth_headers):
        """Test grievance submission endpoint."""
        grievance_data = {
            'subject': 'Water supply issue in my area',
            'description': 'There has been no proper water supply for irrigation in our area for the past month. This is severely affecting crop production.',
            'category': 'water_supply',
            'priority': 'high'
        }
        
        response = client.post('/api/grievances/',
                             data=json.dumps(grievance_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'grievance' in data
        assert data['grievance']['subject'] == grievance_data['subject']

    def test_get_grievances(self, client, auth_headers):
        """Test get user grievances endpoint."""
        response = client.get('/api/grievances/', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'grievances' in data
        assert isinstance(data['grievances'], list)

    def test_get_grievance_categories(self, client, auth_headers):
        """Test get grievance categories endpoint."""
        response = client.get('/api/grievances/categories', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'categories' in data
        assert len(data['categories']) > 0

class TestWeatherRoutes:
    def test_get_weather_unauthorized(self, client):
        """Test weather endpoint without authentication."""
        response = client.get('/api/weather/')
        assert response.status_code == 401

    def test_get_weather_authorized(self, client, auth_headers):
        """Test weather endpoint with authentication."""
        response = client.get('/api/weather/', headers=auth_headers)
        # This might return 503 if weather API is not configured
        assert response.status_code in [200, 503]

class TestBlogRoutes:
    def test_get_blog_posts(self, client, auth_headers):
        """Test get blog posts endpoint."""
        response = client.get('/api/blog/', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'posts' in data
        assert isinstance(data['posts'], list)

    def test_get_blog_categories(self, client, auth_headers):
        """Test get blog categories endpoint."""
        response = client.get('/api/blog/categories', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'categories' in data
        assert len(data['categories']) > 0
