import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService
from app.services.translation_service import TranslationService
from app.services.weather_service import WeatherService

class TestAIService:
    def test_ai_service_initialization(self):
        """Test AI service initialization."""
        ai_service = AIService()
        assert ai_service.model == "gpt-3.5-turbo"

    @patch('openai.ChatCompletion.create')
    def test_get_response(self, mock_openai):
        """Test AI response generation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test AI response"
        mock_openai.return_value = mock_response
        
        ai_service = AIService()
        response = ai_service.get_response("Test message")
        
        assert response == "Test AI response"
        mock_openai.assert_called_once()

    def test_fallback_response(self):
        """Test fallback response when AI service fails."""
        ai_service = AIService()
        response = ai_service._get_fallback_response("fertilizer advice")
        
        assert "fertilizer" in response.lower()
        assert "soil testing" in response.lower()

class TestTranslationService:
    def test_translation_service_initialization(self):
        """Test translation service initialization."""
        translation_service = TranslationService()
        assert 'en' in translation_service.supported_languages
        assert 'ml' in translation_service.supported_languages

    def test_same_language_translation(self):
        """Test translation with same source and target language."""
        translation_service = TranslationService()
        result = translation_service.translate("Hello", 'en', 'en')
        assert result == "Hello"

class TestWeatherService:
    def test_weather_service_initialization(self):
        """Test weather service initialization."""
        weather_service = WeatherService()
        assert weather_service.base_url == "http://api.openweathermap.org/data/2.5"

    def test_farming_advice_generation(self):
        """Test farming advice based on weather conditions."""
        weather_service = WeatherService()
        
        # Test hot weather advice
        advice = weather_service._get_farming_advice(25, 40, 0)
        assert "shade" in advice.lower()
        assert "irrigation" in advice.lower()
        
        # Test rainy weather advice
        advice = weather_service._get_farming_advice(20, 30, 25)
        assert "drainage" in advice.lower()

# ========================================