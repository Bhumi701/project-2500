import speech_recognition as sr
import pyttsx3
from pydub import AudioSegment
import io
import base64
import tempfile
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AudioService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self._configure_tts()
    
    def _configure_tts(self):
        """Configure text-to-speech engine"""
        try:
            # Set properties
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
            
            # Try to set voice for Malayalam if available
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'malayalam' in voice.name.lower() or 'ml' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
                    
        except Exception as e:
            logger.error(f"TTS configuration error: {str(e)}")
    
    def speech_to_text(self, audio_file, language: str = 'en') -> Optional[str]:
        """Convert audio file to text"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_file.save(temp_file.name)
                
                # Load and process audio
                with sr.AudioFile(temp_file.name) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)
                
                # Set language code
                lang_code = self._get_language_code(language)
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio, language=lang_code)
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return text.strip()
                
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Audio processing error: {str(e)}")
            return None
    
    def text_to_speech(self, text: str, language: str = 'en') -> Optional[str]:
        """Convert text to audio and return as base64"""
        try:
            if not text or not text.strip():
                return None
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            # Configure voice for language
            self._set_voice_for_language(language)
            
            # Generate speech
            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()
            
            # Convert to base64
            with open(temp_path, 'rb') as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            return None
    
    def _get_language_code(self, language: str) -> str:
        """Get Google Speech API language code"""
        language_codes = {
            'en': 'en-US',
            'ml': 'ml-IN',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'te': 'te-IN'
        }
        return language_codes.get(language, 'en-US')
    
    def _set_voice_for_language(self, language: str):
        """Set TTS voice for specific language"""
        try:
            voices = self.tts_engine.getProperty('voices')
            
            # Language-specific voice selection
            voice_keywords = {
                'ml': ['malayalam', 'ml'],
                'hi': ['hindi', 'hi'],
                'ta': ['tamil', 'ta'],
                'te': ['telugu', 'te']
            }
            
            if language in voice_keywords:
                for voice in voices:
                    for keyword in voice_keywords[language]:
                        if keyword in voice.name.lower() or keyword in voice.id.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            return
            
            # Default to first available voice
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
                
        except Exception as e:
            logger.error(f"Voice setting error: {str(e)}")
