from app.redis_setup import redis_client
import json
import logging
from typing import Any, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.redis = redis_client
        self.default_timeout = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.redis:
                return None
            
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """Set value in cache"""
        try:
            if not self.redis:
                return False
            
            timeout = timeout or self.default_timeout
            serialized_value = json.dumps(value)
            
            return self.redis.setex(key, timeout, serialized_value)
            
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if not self.redis:
                return False
            
            return bool(self.redis.delete(key))
            
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if not self.redis:
                return 0
            
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {str(e)}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if not self.redis:
                return False
            
            return bool(self.redis.exists(key))
            
        except Exception as e:
            logger.error(f"Cache exists error: {str(e)}")
            return False

# Global cache instance
cache = CacheManager()
