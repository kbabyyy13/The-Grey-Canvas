import logging
import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Sentry SDK early to avoid circular imports
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    # Initialize Sentry SDK
    sentry_dsn = os.environ.get("SENTRY_DSN")
    if sentry_dsn:
        # Determine environment-specific sampling rates
        environment = os.environ.get("SENTRY_ENVIRONMENT", "development")
        if environment == "production":
            traces_sample_rate = 0.1  # 10% in production
            profile_sample_rate = 0.1  # 10% profiling in production
        else:
            traces_sample_rate = 1.0  # 100% in development
            profile_sample_rate = 1.0  # 100% profiling in development

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration(), SqlalchemyIntegration()],
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profile_sample_rate,
            release=os.environ.get("SENTRY_RELEASE", "development"),
            environment=environment,
            attach_stacktrace=True,
            send_default_pii=True,
            before_send=lambda event, hint: (
                event
                if environment != "production"
                or not event.get("user", {}).get("ip_address")
                else {
                    **event,
                    "user": {
                        k: v
                        for k, v in event.get("user", {}).items()
                        if k != "ip_address"
                    },
                }
            ),
        )
except ImportError:
    # Sentry SDK not available, continue without it
    print("Warning: Sentry SDK not available. Error tracking disabled.")
    sentry_sdk = None


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable must be set for security")
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 30  # 30 days

# Configure proxy for HTTPS in production
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure Flask-Mail
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() in [
    "true",
    "on",
    "1",
]
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# Initialize extensions
csrf = CSRFProtect(app)
mail = Mail(app)
db.init_app(app)

# Add template context processor for CSRF token
@app.template_global()
def csrf_token():
    """Generate CSRF token for templates"""
    from flask_wtf.csrf import generate_csrf
    return generate_csrf()

# Initialize Flask-Login for admin authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = (
    None  # We'll handle redirects manually since we have dynamic URLs
)
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


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

# Start backup scheduler in background when app starts
def start_backup_system():
    """Initialize backup system with error handling"""
    try:
        import threading
        import time
        import schedule
        from backup_system import run_daily_backup
        
        def backup_job():
            """Run backup with logging"""
            try:
                logging.info("Running scheduled backup...")
                success = run_daily_backup()
                if success:
                    logging.info("Scheduled backup completed successfully")
                else:
                    logging.error("Scheduled backup failed")
            except Exception as e:
                logging.error(f"Backup job error: {str(e)}")
        
        def cleanup_job():
            """Run weekly cleanup"""
            try:
                logging.info("Running weekly backup cleanup...")
                from backup_system import BackupManager
                backup_manager = BackupManager()
                backup_manager.cleanup_old_backups(days_to_keep=30)
                logging.info("Weekly cleanup completed")
            except Exception as e:
                logging.error(f"Cleanup job error: {str(e)}")
        
        def scheduler_thread():
            """Background scheduler thread"""
            # Schedule jobs
            schedule.every().day.at("02:00").do(backup_job)
            schedule.every().sunday.at("03:00").do(cleanup_job)
            
            logging.info("Backup scheduler started - Daily backups at 2:00 AM")
            logging.info(f"Next backup scheduled for: {schedule.next_run()}")
            
            # Run scheduler
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logging.error(f"Scheduler error: {str(e)}")
                    time.sleep(60)
        
        # Start scheduler in daemon thread
        thread = threading.Thread(target=scheduler_thread, daemon=True)
        thread.start()
        
        print("✅ Automated backup scheduler started successfully")
        print("Daily backups will run at 2:00 AM")
        return True
        
    except Exception as e:
        print(f"⚠️ Warning: Could not start backup scheduler: {str(e)}")
        print("Manual backups are still available through admin panel")
        return False

# Initialize backup system
start_backup_system()

if __name__ == "__main__":
    # Development server run - Gunicorn handles production
    import os

    # Type ignore comment to suppress LSP diagnostic for production environment
    app.run(host="0.0.0.0", port=5000, debug=True)  # type: ignore
