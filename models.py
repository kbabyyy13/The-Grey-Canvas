from app import db
from datetime import datetime, timedelta
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


# Authentication models for Replit Auth
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.id}>'

    @staticmethod
    def get_user(user_id: str) -> dict | None:
        """
        Get user by ID and return as dictionary

        Args:
            user_id (str): The user ID from Replit authentication

        Returns:
            dict | None: User data or None if not found
        """
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return None

        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_image_url': user.profile_image_url,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or None
        }


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)


# Secure Admin Authentication Model
class AdminUser(UserMixin, db.Model):
    """Secure admin user model with password hashing and customizable login URLs"""
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Custom login URL for security
    custom_login_url = db.Column(db.String(200), unique=True, nullable=False)

    # Security features  
    active_status = db.Column(db.Boolean, default=True)
    login_attempts = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, nullable=True)
    locked_until = db.Column(db.DateTime, nullable=True)

    # Password requirements tracking
    password_updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    require_password_change = db.Column(db.Boolean, default=False)

    # Audit trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password with strong security requirements"""
        if not self.is_strong_password(password):
            raise ValueError("Password does not meet security requirements")
        self.password_hash = generate_password_hash(password)
        self.password_updated_at = datetime.utcnow()
        self.require_password_change = False

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def is_strong_password(self, password):
        """Validate password strength requirements"""
        if len(password) < 12:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            return False
        return True

    def generate_custom_login_url(self):
        """Generate a secure, unique login URL"""
        return f"admin-{secrets.token_urlsafe(16)}"

    def is_account_locked(self):
        """Check if account is locked due to failed attempts"""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False

    def increment_login_attempts(self):
        """Increment failed login attempts and lock if necessary"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            # Lock account for 30 minutes after 5 failed attempts
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)

    def reset_login_attempts(self):
        """Reset login attempts after successful login"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()

    def __repr__(self):
        return f'<AdminUser {self.username}>'


class ContactSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactSubmission {self.name}: {self.subject}>'


class IntakeSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    website_type = db.Column(db.String(50), nullable=False)
    timeline = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.String(50), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    additional_notes = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<IntakeSubmission {self.business_name}: {self.contact_name}>'


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(100), nullable=False, default='Krysta McAlister')
    published = db.Column(db.Boolean, default=True)
    featured_image = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    meta_description = db.Column(db.String(160), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<BlogPost {self.title}>'

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def format_date(self):
        return self.created_at.strftime('%B %d, %Y')


# Project Progress Tracking Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    # Type: business, ecommerce, portfolio, blog, other
    project_type = db.Column(db.String(50), nullable=False)
    # Status: inquiry, planning, development, review, completed, cancelled
    status = db.Column(db.String(50), nullable=False, default='inquiry')
    budget = db.Column(db.String(50), nullable=True)
    timeline = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    client_email = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(20), nullable=True)

    # Project dates
    inquiry_date = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, nullable=True)
    expected_completion = db.Column(db.DateTime, nullable=True)
    actual_completion = db.Column(db.DateTime, nullable=True)

    # Progress tracking
    progress_percentage = db.Column(db.Integer, default=0)  # Range: 0-100
    current_phase = db.Column(db.String(100), nullable=True)
    next_milestone = db.Column(db.String(200), nullable=True)

    # Project details
    website_url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to intake submission
    intake_submission_id = db.Column(db.Integer, db.ForeignKey('intake_submission.id'), nullable=True)
    intake_submission = db.relationship('IntakeSubmission', backref='project')

    # Relationship to project timeline events
    timeline_events = db.relationship('ProjectTimelineEvent', backref='project', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.project_name} - {self.client_name}>'

    def get_status_display(self):
        status_map = {
            'inquiry': 'Initial Inquiry',
            'planning': 'Planning & Design',
            'development': 'Development',
            'review': 'Client Review',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        return status_map.get(self.status, self.status.title())

    def get_status_color(self):
        color_map = {
            'inquiry': 'blue',
            'planning': 'yellow',
            'development': 'purple',
            'review': 'orange',
            'completed': 'green',
            'cancelled': 'red'
        }
        return color_map.get(self.status, 'gray')

    def days_since_inquiry(self):
        return (datetime.utcnow() - self.inquiry_date).days

    def is_overdue(self):
        if self.expected_completion and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.expected_completion
        return False


class ProjectTimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # status_change, milestone, note, file_upload, client_feedback
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=True)  # admin user who created the event

    # Optional fields for different event types
    old_status = db.Column(db.String(50), nullable=True)
    new_status = db.Column(db.String(50), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    is_milestone = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProjectTimelineEvent {self.title}>'

    def get_event_icon(self):
        icon_map = {
            'status_change': '🔄',
            'milestone': '🎯',
            'note': '📝',
            'file_upload': '📁',
            'client_feedback': '💬',
            'meeting': '🤝',
            'payment': '💰'
        }
        return icon_map.get(self.event_type, '📌')

    def format_date(self):
        return self.event_date.strftime('%B %d, %Y at %I:%M %p')


class NewsletterSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<NewsletterSubscription {self.email}>'