from app.config import Config
import os

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security settings
    SSL_REDIRECT = True
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')