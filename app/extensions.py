# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
# Add any other extensions you're using

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()