import secrets
from datetime import datetime, timedelta

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash
import re

from app import db


# Authentication models for Replit Auth
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    profile_image_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow,
                           nullable=False)

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_created_at', 'created_at'),
    )

    def __repr__(self):
        return f'<User {self.id}>'

    @validates('email')
    def validate_email(self, key, address):
        """Validate email format"""
        if address and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', address):
            raise ValueError('Invalid email format')
        return address

    @validates('id')
    def validate_id(self, key, user_id):
        """Validate user ID format and length"""
        if not user_id or len(user_id.strip()) == 0:
            raise ValueError('User ID cannot be empty')
        if len(user_id) > 100:
            raise ValueError('User ID too long')
        return user_id.strip()

    @staticmethod
    def get_user(user_id: str) -> dict | None:
        """
        Get user by ID and return as dictionary

        Args:
            user_id (str): The user ID from Replit authentication

        Returns:
            dict | None: User data or None if not found
        """
        if not user_id or len(user_id.strip()) == 0:
            return None
            
        user = User.query.filter_by(id=user_id.strip()).first()

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
    user_id = db.Column(db.String(100), db.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    browser_session_key = db.Column(db.String(255), nullable=False)
    user = db.relationship(User, backref='oauth_tokens')

    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'browser_session_key',
            'provider',
            name='uq_user_browser_session_key_provider',
        ),
        Index('idx_oauth_user_id', 'user_id'),
        Index('idx_oauth_provider', 'provider'),
    )


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
    __tablename__ = 'contact_submission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_contact_submitted_at', 'submitted_at'),
        Index('idx_contact_email', 'email'),
    )

    @validates('email')
    def validate_email(self, key, address):
        """Validate email format"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', address):
            raise ValueError('Invalid email format')
        return address.lower().strip()

    @validates('name', 'subject')
    def validate_text_fields(self, key, value):
        """Validate and sanitize text fields"""
        if not value or len(value.strip()) == 0:
            raise ValueError(f'{key} cannot be empty')
        return value.strip()

    @validates('phone') 
    def validate_phone(self, key, phone):
        """Validate phone format if provided"""
        if phone and len(phone.strip()) > 0:
            # Remove all non-digit characters for validation
            digits_only = re.sub(r'[^\d]', '', phone)
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError('Invalid phone number format')
        return phone.strip() if phone else None

    def __repr__(self):
        return f'<ContactSubmission {self.name}: {self.subject}>'


class IntakeSubmission(db.Model):
    __tablename__ = 'intake_submission'
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
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_intake_submitted_at', 'submitted_at'),
        Index('idx_intake_email', 'email'),
        Index('idx_intake_business_name', 'business_name'),
    )

    @validates('email')
    def validate_email(self, key, address):
        """Validate email format"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', address):
            raise ValueError('Invalid email format')
        return address.lower().strip()

    @validates('business_name', 'contact_name', 'website_type', 'timeline', 'budget')
    def validate_required_fields(self, key, value):
        """Validate required fields are not empty"""
        if not value or len(value.strip()) == 0:
            raise ValueError(f'{key} cannot be empty')
        return value.strip()

    @validates('phone')
    def validate_phone(self, key, phone):
        """Validate phone format if provided"""
        if phone and len(phone.strip()) > 0:
            digits_only = re.sub(r'[^\d]', '', phone)
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError('Invalid phone number format')
        return phone.strip() if phone else None

    def __repr__(self):
        return f'<IntakeSubmission {self.business_name}: {self.contact_name}>'


class BlogPost(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(100), nullable=False, default='Krysta McAlister')
    published = db.Column(db.Boolean, default=True, nullable=False)
    featured_image = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    meta_description = db.Column(db.String(160), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_blog_published', 'published'),
        Index('idx_blog_created_at', 'created_at'),
        Index('idx_blog_slug', 'slug'),
    )

    @validates('title', 'content')
    def validate_required_fields(self, key, value):
        """Validate required fields are not empty"""
        if not value or len(value.strip()) == 0:
            raise ValueError(f'{key} cannot be empty')
        return value.strip()

    @validates('slug')
    def validate_slug(self, key, slug):
        """Validate slug format"""
        if not slug or len(slug.strip()) == 0:
            raise ValueError('Slug cannot be empty')
        # Ensure slug contains only URL-safe characters
        if not re.match(r'^[a-z0-9-]+$', slug.strip()):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return slug.strip().lower()

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
    __tablename__ = 'newsletter_subscription'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        Index('idx_newsletter_email', 'email'),
        Index('idx_newsletter_active', 'is_active'),
    )

    @validates('email')
    def validate_email(self, key, address):
        """Validate email format"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', address):
            raise ValueError('Invalid email format')
        return address.lower().strip()

    def __repr__(self):
        return f'<NewsletterSubscription {self.email}>'