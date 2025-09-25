#from app.api.auth import auth_bp
from app.api.weather import weather_bp
from app.api.chat import chat_bp
from app.api.grievances import grievances_bp
from app.api.blog import blog_bp
from app.api.policies import policies_bp

__all__ = ['auth_bp', 'weather_bp', 'chat_bp', 'grievances_bp', 'blog_bp', 'policies_bp']
