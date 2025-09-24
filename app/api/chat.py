from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.chat import ChatSession
from app.services import AIService
from app.services.translation_service import TranslationService
from app.services.audio_service import AudioService
from datetime import datetime
import uuid
import logging

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

@chat_bp.route('/', methods=['POST'])
@jwt_required()
def text_chat():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        message = data.get('message', '').strip()
        language = data.get('language', user.preferred_language)
        session_id = data.get('session_id', f"session_{user_id}_{uuid.uuid4().hex[:8]}")
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create chat session
        chat_session = ChatSession.query.filter_by(
            user_id=user_id, 
            session_id=session_id
        ).first()
        
        if not chat_session:
            chat_session = ChatSession(
                user_id=user_id,
                session_id=session_id,
                language=language
            )
            db.session.add(chat_session)
        
        # Process message through AI service
        ai_service = AIService()
        translation_service = TranslationService()
        
        # Translate to English if needed
        if language != 'en':
            english_message = translation_service.translate(message, 'en', language)
        else:
            english_message = message
        
        # Get AI response
        ai_response = ai_service.get_response(
            english_message, 
            context={
                'user_location': user.location,
                'language': language,
                'chat_history': chat_session.get_messages()[-5:]  # Last 5 messages for context
            }
        )
        
        # Translate response back if needed
        if language != 'en':
            translated_response = translation_service.translate(ai_response, language, 'en')
        else:
            translated_response = ai_response
        
        # Save to chat session
        chat_session.add_message(message, translated_response)
        db.session.commit()
        
        return jsonify({
            'response': translated_response,
            'session_id': session_id,
            'language': language,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Text chat error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Chat service error'}), 500

@chat_bp.route('/audio', methods=['POST'])
@jwt_required()
def audio_chat():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file required'}), 400
        
        audio_file = request.files['audio']
        language = request.form.get('language', user.preferred_language)
        session_id = request.form.get('session_id', f"session_{user_id}_{uuid.uuid4().hex[:8]}")
        
        # Initialize services
        audio_service = AudioService()
        ai_service = AIService()
        translation_service = TranslationService()
        
        # Convert audio to text
        text_message = audio_service.speech_to_text(audio_file, language)
        
        if not text_message:
            return jsonify({'error': 'Could not process audio'}), 400
        
        # Process through AI (similar to text chat)
        if language != 'en':
            english_message = translation_service.translate(text_message, 'en', language)
        else:
            english_message = text_message
        
        ai_response = ai_service.get_response(
            english_message,
            context={'user_location': user.location, 'language': language}
        )
        
        if language != 'en':
            translated_response = translation_service.translate(ai_response, language, 'en')
        else:
            translated_response = ai_response
        
        # Convert response to audio
        audio_response = audio_service.text_to_speech(translated_response, language)
        
        # Save chat session
        chat_session = ChatSession.query.filter_by(
            user_id=user_id, 
            session_id=session_id
        ).first()
        
        if not chat_session:
            chat_session = ChatSession(
                user_id=user_id,
                session_id=session_id,
                language=language
            )
            db.session.add(chat_session)
        
        chat_session.add_message(text_message, translated_response)
        db.session.commit()
        
        return jsonify({
            'text_message': text_message,
            'text_response': translated_response,
            'audio_response': audio_response,
            'session_id': session_id,
            'language': language
        }), 200
        
    except Exception as e:
        logger.error(f"Audio chat error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Audio chat service error'}), 500

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_chat_sessions():
    try:
        user_id = get_jwt_identity()
        
        sessions = ChatSession.query.filter_by(user_id=user_id)\
                                  .order_by(ChatSession.updated_at.desc())\
                                  .limit(20).all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions]
        }), 200
        
    except Exception as e:
        logger.error(f"Chat sessions error: {str(e)}")
        return jsonify({'error': 'Failed to fetch chat sessions'}), 500

