import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt
    salted_password = password + salt
    
    # Hash using SHA-256
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    
    return hashed, salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify password against hash"""
    test_hash, _ = hash_password(password, salt)
    return test_hash == hashed_password

def generate_verification_token(user_id: int, expires_hours: int = 24) -> str:
    """Generate email verification token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expires_hours),
        'iat': datetime.utcnow(),
        'type': 'email_verification'
    }
    
    secret_key = os.environ.get('JWT_SECRET_KEY', 'fallback-secret')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode token"""
    try:
        secret_key = os.environ.get('JWT_SECRET_KEY', 'fallback-secret')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def sanitize_input(text: str, max_length: int = None) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip whitespace
    text = text.strip()
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

