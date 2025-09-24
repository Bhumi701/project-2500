# ========================================
# app/utils/decorators.py
# ========================================

from functools import wraps
from flask import request, jsonify, current_app

from app.redis_setup import redis_client
import json
import hashlib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def rate_limit(max_requests: int = 100, window_seconds: int = 3600, per_ip: bool = True):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_client:
                return f(*args, **kwargs)
            
            try:
                # Create rate limit key
                if per_ip:
                    client_id = request.remote_addr
                else:
                    from flask_jwt_extended import get_jwt_identity
                    client_id = get_jwt_identity() or request.remote_addr
                
                key = f"rate_limit:{f.__name__}:{client_id}"
                
                # Get current count
                current_requests = redis_client.get(key)
                
                if current_requests is None:
                    # First request in window
                    redis_client.setex(key, window_seconds, 1)
                    return f(*args, **kwargs)
                
                current_requests = int(current_requests)
                
                if current_requests >= max_requests:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'max_requests': max_requests,
                        'window_seconds': window_seconds
                    }), 429
                
                # Increment counter
                redis_client.incr(key)
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Rate limiting error: {str(e)}")
                return f(*args, **kwargs)  # Continue without rate limiting
        
        return decorated_function
    return decorator

def cache_response(timeout: int = 300, key_func=None):
    """Response caching decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_client:
                return f(*args, **kwargs)
            
            try:
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default key generation
                    key_parts = [
                        f.__name__,
                        request.endpoint,
                        request.args.to_dict(flat=False),
                        getattr(request, 'view_args', {})
                    ]
                    key_string = json.dumps(key_parts, sort_keys=True)
                    cache_key = f"cache:{hashlib.md5(key_string.encode()).hexdigest()}"
                
                # Try to get from cache
                cached_result = redis_client.get(cache_key)
                
                if cached_result:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return json.loads(cached_result)
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                
                # Only cache successful responses
                if isinstance(result, tuple) and len(result) == 2:
                    response_data, status_code = result
                    if status_code == 200:
                        redis_client.setex(cache_key, timeout, json.dumps(result))
                        logger.debug(f"Cached result for key: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Caching error: {str(e)}")
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def log_api_call(include_response: bool = False):
    """API call logging decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.now()
            
            # Log request
            logger.info(f"API Call: {request.method} {request.endpoint}")
            logger.debug(f"Request args: {request.args}")
            
            if request.is_json:
                logger.debug(f"Request JSON: {request.get_json()}")
            
            try:
                result = f(*args, **kwargs)
                
                # Log response
                duration = (datetime.now() - start_time).total_seconds()
                status_code = result[1] if isinstance(result, tuple) else 200
                
                logger.info(f"API Response: {status_code} - Duration: {duration:.3f}s")
                
                if include_response and status_code == 200:
                    logger.debug(f"Response: {result}")
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"API Error: {str(e)} - Duration: {duration:.3f}s")
                raise
        
        return decorated_function
    return decorator
