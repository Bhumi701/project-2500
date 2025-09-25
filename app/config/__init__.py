"""from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
from celery import Celery
import redis

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
cors = CORS()
migrate = Migrate()
redis_client = None
celery = None

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        from app.config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        from app.config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from app.config.testing import TestingConfig
        app.config.from_object(TestingConfig)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # Initialize Celery
    global celery
    celery = make_celery(app)
    
    # Register blueprints
    from app.api import auth_bp, weather_bp, chat_bp, grievances_bp, blog_bp, policies_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(grievances_bp, url_prefix='/api/grievances')
    app.register_blueprint(blog_bp, url_prefix='/api/blog')
    app.register_blueprint(policies_bp, url_prefix='/api/policies')
    
    # Health check route
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Agricultural Advisory API'}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND'),
        broker=app.config.get('CELERY_BROKER_URL')
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery"""

# app/config/__init__.py
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    @staticmethod
    def init_app(app):
        pass