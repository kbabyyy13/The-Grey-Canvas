import os
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Simple Sentry test configuration (commented out - use environment-based config below)
# sentry_sdk.init(
#     dsn="https://a4a1e2fb28becfe6aa44ef0b93f8ed8e@o4509702640697344.ingest.us.sentry.io/4509702645350400",
#     traces_sample_rate=1.0,
# )
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Initialize Sentry SDK
sentry_dsn = os.environ.get('SENTRY_DSN')
if sentry_dsn:
    # Determine environment-specific sampling rates
    environment = os.environ.get('SENTRY_ENVIRONMENT', 'development')
    if environment == 'production':
        traces_sample_rate = 0.1  # 10% in production
        profile_sample_rate = 0.1  # 10% profiling in production
    else:
        traces_sample_rate = 1.0   # 100% in development
        profile_sample_rate = 1.0  # 100% profiling in development
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration()
        ],
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profile_sample_rate,
        release=os.environ.get('SENTRY_RELEASE', 'development'),
        environment=environment,
        attach_stacktrace=True,
        send_default_pii=False,  # Keep PII protection enabled
        before_send=lambda event, hint: event if environment != 'production' or not event.get('user', {}).get('ip_address') else {**event, 'user': {k: v for k, v in event.get('user', {}).items() if k != 'ip_address'}}
    )

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable must be set for security")
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30  # 30 days

# Configure proxy for HTTPS in production
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# Initialize extensions
csrf = CSRFProtect(app)
mail = Mail(app)
db.init_app(app)

# Initialize Flask-Login for admin authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None  # We'll handle redirects manually since we have dynamic URLs
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login - supports both Replit users and Admin users"""
    from models import AdminUser, User
    
    # Try to load as AdminUser first (for secure admin login)
    try:
        admin_user = AdminUser.query.get(int(user_id)) if user_id.isdigit() else None
        if admin_user:
            return admin_user
    except (ValueError, TypeError):
        pass
    
    # Fall back to Replit OAuth user
    return User.query.get(user_id)

# Create database tables
with app.app_context():
    # Import models to register them with SQLAlchemy
    import models  # noqa: F401
    db.create_all()

# Import routes
from routes import *

if __name__ == '__main__':
    # Development server run - Gunicorn handles production
    import os
    # Type ignore comment to suppress LSP diagnostic for production environment
    app.run(host='0.0.0.0', port=5000, debug=True)  # type: ignore
