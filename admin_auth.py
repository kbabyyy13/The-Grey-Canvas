"""
Secure Admin Authentication System
Provides customizable login URLs and strong password requirements
"""

import logging
import re
import secrets
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash

from models import AdminUser, db

admin_auth = Blueprint('admin_auth', __name__)

def validate_password_strength(password):
    """
    Validate password meets security requirements:
    - At least 12 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    - Contains special character
    """
    errors = []
    
    if len(password) < 12:
        errors.append("Password must be at least 12 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return errors

@admin_auth.route('/admin/setup', methods=['GET', 'POST'])
def setup_admin():
    """Setup first admin user with custom login URL"""
    # Check if admin user already exists
    if AdminUser.query.first():
        flash('Admin user already exists. Use the login page.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            custom_url = request.form.get('custom_url', '').strip()
            
            # Validation
            errors = []
            
            if not username or len(username) < 3:
                errors.append("Username must be at least 3 characters long")
            
            if not email or '@' not in email:
                errors.append("Please enter a valid email address")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            # Validate password strength
            password_errors = validate_password_strength(password)
            errors.extend(password_errors)
            
            # Validate custom URL
            if not custom_url:
                custom_url = f"admin-{secrets.token_urlsafe(16)}"
            elif not re.match(r'^[a-zA-Z0-9\-_]+$', custom_url):
                errors.append("Custom URL can only contain letters, numbers, hyphens, and underscores")
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin_setup.html')
            
            # Create admin user
            admin = AdminUser()
            admin.username = username
            admin.email = email
            admin.set_password(password)
            admin.custom_login_url = custom_url
            
            db.session.add(admin)
            db.session.commit()
            
            flash(f'Admin account created successfully! Your custom login URL is: /{custom_url}', 'success')
            return redirect(f'/admin-{custom_url}')
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating admin user: {e}")
            flash('Error creating admin account. Please try again.', 'error')
    
    return render_template('admin_setup.html')

@admin_auth.route('/admin-<url_path>', methods=['GET', 'POST'])
def login(url_path):
    """Dynamic login route using custom URL"""
    # Find admin user by custom URL
    admin = AdminUser.query.filter_by(custom_login_url=url_path).first()
    
    if not admin:
        # Invalid URL - redirect to 404 to avoid revealing admin URLs
        return render_template('404.html'), 404
    
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            # Check if account is locked
            if admin.is_account_locked():
                flash('Account is temporarily locked due to failed login attempts. Please try again later.', 'error')
                return render_template('admin_login.html', admin=admin)
            
            # Validate credentials
            if admin.username == username and admin.check_password(password):
                if not admin.active_status:
                    flash('Account is disabled. Please contact administrator.', 'error')
                    return render_template('admin_login.html', admin=admin)
                
                # Successful login
                admin.reset_login_attempts()
                db.session.commit()
                login_user(admin)
                
                # Check if password change is required
                if admin.require_password_change:
                    return redirect(url_for('admin_auth.change_password'))
                
                # Direct redirect without Flask url_for to avoid OAuth conflicts
                return redirect('/admin/dashboard')
            else:
                # Failed login
                admin.increment_login_attempts()
                db.session.commit()
                flash('Invalid username or password.', 'error')
                
        except Exception as e:
            logging.error(f"Login error: {e}")
            flash('Login error. Please try again.', 'error')
    
    return render_template('admin_login.html', admin=admin)

@admin_auth.route('/admin/logout')
@login_required
def logout():
    """Logout admin user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@admin_auth.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change admin password"""
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            errors = []
            
            # Validate current password
            if not current_user.check_password(current_password):
                errors.append("Current password is incorrect")
            
            # Validate new password
            if new_password != confirm_password:
                errors.append("New passwords do not match")
            
            password_errors = validate_password_strength(new_password)
            errors.extend(password_errors)
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin_change_password.html')
            
            # Update password
            current_user.set_password(new_password)
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Password change error: {e}")
            flash('Error changing password. Please try again.', 'error')
    
    return render_template('admin_change_password.html')

@admin_auth.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """Admin account settings including custom URL management"""
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'update_url':
                new_url = request.form.get('new_custom_url', '').strip()
                
                if not new_url:
                    flash('Custom URL cannot be empty', 'error')
                elif not re.match(r'^[a-zA-Z0-9\-_]+$', new_url):
                    flash('Custom URL can only contain letters, numbers, hyphens, and underscores', 'error')
                elif AdminUser.query.filter_by(custom_login_url=new_url).first():
                    flash('This custom URL is already in use', 'error')
                else:
                    old_url = current_user.custom_login_url
                    current_user.custom_login_url = new_url
                    db.session.commit()
                    flash(f'Custom login URL updated! New URL: /{new_url}', 'success')
                    
            elif action == 'generate_url':
                new_url = f"admin-{secrets.token_urlsafe(16)}"
                current_user.custom_login_url = new_url
                db.session.commit()
                flash(f'New custom login URL generated: /{new_url}', 'success')
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Settings update error: {e}")
            flash('Error updating settings. Please try again.', 'error')
    
    return render_template('admin_settings.html')

@admin_auth.route('/admin/security-check')
@login_required
def security_check():
    """Security status check for admin account"""
    admin = current_user
    
    # Check password age (recommend change every 90 days)
    password_age = datetime.utcnow() - admin.password_updated_at
    password_old = password_age.days > 90
    
    # Security recommendations
    recommendations = []
    
    if password_old:
        recommendations.append("Consider changing your password (it's over 90 days old)")
    
    if admin.login_attempts > 0:
        recommendations.append("Recent failed login attempts detected")
    
    return jsonify({
        'password_age_days': password_age.days,
        'password_old': password_old,
        'last_login': admin.last_login.isoformat() if admin.last_login else None,
        'login_attempts': admin.login_attempts,
        'recommendations': recommendations
    })