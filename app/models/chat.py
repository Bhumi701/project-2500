from app.extensions import db
from datetime import datetime
import json

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    messages = db.Column(db.Text)
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('chat_sessions', lazy=True, order_by='ChatSession.created_at.desc()'))
    
    def add_message(self, user_message, bot_response):
        messages = json.loads(self.messages or '[]')
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response
        })
        self.messages = json.dumps(messages)
        self.updated_at = datetime.utcnow()
    
    def get_messages(self):
        return json.loads(self.messages or '[]')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'language': self.language,
            'messages': self.get_messages(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'

