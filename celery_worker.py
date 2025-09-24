from app import create_app, celery

# Create Flask app instance
flask_app = create_app()

# Push application context for Celery
flask_app.app_context().push()

if __name__ == '__main__':
    celery.start()