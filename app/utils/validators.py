import re
from typing import Dict, Any

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    if len(password) < 8:
        return {'valid': False, 'message': 'Password must be at least 8 characters long'}
    
    if not re.search(r'[A-Za-z]', password):
        return {'valid': False, 'message': 'Password must contain at least one letter'}
    
    if not re.search(r'[0-9]', password):
        return {'valid': False, 'message': 'Password must contain at least one number'}
    
    return {'valid': True, 'message': 'Password is valid'}

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove spaces and special characters
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Check Indian phone number patterns
    patterns = [
    r'^\+91[6-9]\d{9}$',   # +91 format
    r'^[6-9]\d{9}$',       # 10 digit format
    r'^0[6-9]\d{9}$'       # 11 digit format with 0
    ]
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def validate_grievance_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate grievance submission data"""
    required_fields = ['subject', 'description', 'category']
    
    for field in required_fields:
        if not data.get(field) or not data[field].strip():
            return {'valid': False, 'message': f'{field.title()} is required'}
    
    if len(data['subject'].strip()) < 10:
        return {'valid': False, 'message': 'Subject must be at least 10 characters long'}
    
    if len(data['description'].strip()) < 20:
        return {'valid': False, 'message': 'Description must be at least 20 characters long'}
    
    valid_categories = [
        'crop_insurance', 'subsidies', 'loan_issues', 'market_access',
        'water_supply', 'pest_control', 'other'
    ]
    
    if data['category'] not in valid_categories:
        return {'valid': False, 'message': 'Invalid category selected'}
    
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    priority = data.get('priority', 'medium')
    
    if priority not in valid_priorities:
        return {'valid': False, 'message': 'Invalid priority level'}
    
    return {'valid': True, 'message': 'Grievance data is valid'}

def validate_location(location: str) -> bool:
    """Validate location format"""
    if not location or len(location.strip()) < 2:
        return False
    
    # Allow letters, spaces, commas, and hyphens
    pattern = r'^[a-zA-Z\s,.-]+'
    return bool(re.match(pattern, location.strip()))