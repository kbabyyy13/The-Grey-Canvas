#!/usr/bin/env python3
"""
Admin Management Utilities
Provides command-line tools for managing admin users
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from getpass import getpass

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import AdminUser

def list_admins():
    """List all admin users"""
    with app.app_context():
        admins = AdminUser.query.all()
        
        if not admins:
            print("No admin users found.")
            print("Run 'python create_admin.py' to create your first admin user.")
            return
        
        print(f"\n📋 Found {len(admins)} admin user(s):")
        print("=" * 80)
        
        for admin in admins:
            print(f"ID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Custom URL: /{admin.custom_login_url}")
            print(f"Active: {'Yes' if admin.is_active else 'No'}")
            print(f"Last Login: {admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if admin.last_login else 'Never'}")
            print(f"Failed Attempts: {admin.login_attempts}")
            print(f"Account Locked: {'Yes' if admin.is_account_locked() else 'No'}")
            print("-" * 80)

def unlock_admin(username):
    """Unlock an admin account"""
    with app.app_context():
        admin = AdminUser.query.filter_by(username=username).first()
        
        if not admin:
            print(f"Admin user '{username}' not found.")
            return
        
        admin.login_attempts = 0
        admin.locked_until = None
        db.session.commit()
        
        print(f"✅ Admin account '{username}' has been unlocked.")

def change_admin_password(username):
    """Change admin password"""
    with app.app_context():
        admin = AdminUser.query.filter_by(username=username).first()
        
        if not admin:
            print(f"Admin user '{username}' not found.")
            return
        
        print(f"Changing password for admin user: {username}")
        print("\nPassword Requirements:")
        print("- At least 12 characters")
        print("- One uppercase letter")
        print("- One lowercase letter") 
        print("- One number")
        print("- One special character (!@#$%^&*)")
        
        password = getpass("Enter new password: ")
        confirm_password = getpass("Confirm new password: ")
        
        while password != confirm_password:
            print("Passwords do not match!")
            password = getpass("Enter new password: ")
            confirm_password = getpass("Confirm new password: ")
        
        try:
            admin.set_password(password)
            db.session.commit()
            print(f"✅ Password changed successfully for '{username}'.")
            
        except ValueError as e:
            print(f"❌ Error: {e}")

def generate_new_url(username):
    """Generate new custom login URL"""
    with app.app_context():
        admin = AdminUser.query.filter_by(username=username).first()
        
        if not admin:
            print(f"Admin user '{username}' not found.")
            return
        
        old_url = admin.custom_login_url
        admin.custom_login_url = admin.generate_custom_login_url()
        db.session.commit()
        
        print(f"✅ New custom login URL generated for '{username}':")
        print(f"Old URL: /{old_url}")
        print(f"New URL: /{admin.custom_login_url}")

def deactivate_admin(username):
    """Deactivate an admin account"""
    with app.app_context():
        admin = AdminUser.query.filter_by(username=username).first()
        
        if not admin:
            print(f"Admin user '{username}' not found.")
            return
        
        admin.is_active = False
        db.session.commit()
        
        print(f"✅ Admin account '{username}' has been deactivated.")

def activate_admin(username):
    """Activate an admin account"""
    with app.app_context():
        admin = AdminUser.query.filter_by(username=username).first()
        
        if not admin:
            print(f"Admin user '{username}' not found.")
            return
        
        admin.is_active = True
        db.session.commit()
        
        print(f"✅ Admin account '{username}' has been activated.")

def security_audit():
    """Run security audit on admin accounts"""
    with app.app_context():
        admins = AdminUser.query.all()
        
        if not admins:
            print("No admin users found.")
            return
        
        print("🔍 Security Audit Report")
        print("=" * 50)
        
        issues = []
        
        for admin in admins:
            # Check password age
            password_age = datetime.utcnow() - admin.password_updated_at
            if password_age.days > 90:
                issues.append(f"⚠️  {admin.username}: Password is {password_age.days} days old (recommend change)")
            
            # Check failed login attempts
            if admin.login_attempts > 0:
                issues.append(f"⚠️  {admin.username}: {admin.login_attempts} recent failed login attempts")
            
            # Check if account is locked
            if admin.is_account_locked():
                issues.append(f"🔒 {admin.username}: Account is currently locked")
            
            # Check if account is inactive
            if not admin.is_active:
                issues.append(f"⚠️  {admin.username}: Account is deactivated")
        
        if issues:
            print("\nSecurity Issues Found:")
            for issue in issues:
                print(issue)
        else:
            print("\n✅ No security issues found.")
        
        print(f"\nTotal Admin Users: {len(admins)}")
        print(f"Active Users: {len([a for a in admins if a.is_active])}")
        print(f"Locked Users: {len([a for a in admins if a.is_account_locked()])}")

def main():
    parser = argparse.ArgumentParser(description='Admin Management Utilities')
    parser.add_argument('action', choices=['list', 'unlock', 'password', 'url', 'deactivate', 'activate', 'audit'],
                       help='Action to perform')
    parser.add_argument('--username', '-u', help='Username for user-specific actions')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_admins()
    elif args.action == 'unlock':
        if not args.username:
            print("Username required for unlock action. Use --username or -u")
            return
        unlock_admin(args.username)
    elif args.action == 'password':
        if not args.username:
            print("Username required for password action. Use --username or -u")
            return
        change_admin_password(args.username)
    elif args.action == 'url':
        if not args.username:
            print("Username required for URL action. Use --username or -u")
            return
        generate_new_url(args.username)
    elif args.action == 'deactivate':
        if not args.username:
            print("Username required for deactivate action. Use --username or -u")
            return
        deactivate_admin(args.username)
    elif args.action == 'activate':
        if not args.username:
            print("Username required for activate action. Use --username or -u")
            return
        activate_admin(args.username)
    elif args.action == 'audit':
        security_audit()

if __name__ == "__main__":
    main()