from googletrans import Translator
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'en': 'English',
            'ml': 'Malayalam',
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu'
        }
    
    def translate(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """Translate text between languages"""
        try:
            if not text or not text.strip():
                return text
            
            # Skip translation if same language
            if source_lang == target_lang:
                return text
            
            result = self.translator.translate(
                text, 
                src=source_lang if source_lang != 'auto' else None,
                dest=target_lang
            )
            
            return result.text
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text if translation fails
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect language of given text"""
        try:
            detection = self.translator.detect(text)
            return detection.lang
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return None
    
    def get_supported_languages(self) -> dict:
        """Get list of supported languages"""
        return self.supported_languages