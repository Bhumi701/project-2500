from app import create_app
# from app.config import DevelopmentConfig
import os


# Create Flask application
app = create_app(os.environ.get('FLASK_CONFIG') or 'development')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)