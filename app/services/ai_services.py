import openai
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"
    
    def get_response(self, message: str, context: Dict = None) -> str:
        """Generate AI response for agricultural queries"""
        try:
            # Build system prompt with agricultural context
            system_prompt = self._build_system_prompt(context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add chat history if available
            if context and 'chat_history' in context:
                for msg in context['chat_history'][-3:]:  # Last 3 exchanges
                    messages.insert(-1, {"role": "user", "content": msg['user_message']})
                    messages.insert(-1, {"role": "assistant", "content": msg['bot_response']})
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            return self._get_fallback_response(message)
    
    def _build_system_prompt(self, context: Dict = None) -> str:
        """Build system prompt with agricultural context"""
        base_prompt = """You are an AI agricultural advisor specifically designed to help farmers in Kerala, India. 
        You provide expert advice on:
        - Crop management and farming techniques
        - Weather-based farming decisions
        - Pest and disease control
        - Soil health and fertilizer recommendations
        - Government schemes and subsidies
        - Market prices and trends
        - Sustainable and organic farming practices
        
        Always provide practical, actionable advice suitable for small to medium-scale farmers.
        Keep responses concise but informative."""
        
        if context:
            if context.get('user_location'):
                base_prompt += f"\n\nUser location: {context['user_location']}"
            
            if context.get('language') == 'ml':
                base_prompt += "\n\nNote: This response will be translated to Malayalam, so use simple, clear language."
        
        return base_prompt
    
    def _get_fallback_response(self, message: str) -> str:
        """Provide fallback response when AI service is unavailable"""
        agricultural_keywords = {
            'weather': "I recommend checking current weather conditions before making farming decisions. Consider rainfall patterns and temperature for optimal planting and harvesting times.",
            'fertilizer': "For fertilizer recommendations, consider soil testing first. NPK ratios depend on your crop type and soil conditions. Organic fertilizers like compost and vermicompost are also beneficial.",
            'pesticide': "For pest management, identify the specific pest first. Integrated Pest Management (IPM) combining biological, cultural, and chemical methods is most effective.",
            'seeds': "Choose seeds based on your local climate, soil type, and market demand. High-yield varieties adapted to Kerala's conditions are recommended.",
            'irrigation': "Water management is crucial. Drip irrigation systems are water-efficient. Consider rainwater harvesting during monsoon seasons.",
            'soil': "Maintain soil health through regular testing, organic matter addition, and proper crop rotation. Good soil is the foundation of successful farming."
        }
        
        message_lower = message.lower()
        
        for keyword, response in agricultural_keywords.items():
            if keyword in message_lower:
                return response
        
        return "I'm here to help with your agricultural questions. Please ask about crops, fertilizers, pesticides, weather, irrigation, or any farming-related topics."
