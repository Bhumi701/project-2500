"""from app.config import Config

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///agricultural_advisory_dev.db'
    """
# app/config/development.py
import os
from app.config import Config

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data-dev.sqlite')
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log SQL queries in development