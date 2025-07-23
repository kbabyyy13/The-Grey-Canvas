#!/usr/bin/env python3
"""
Create first admin user for secure admin authentication
Usage: python create_admin.py
"""

import os
import sys
from getpass import getpass

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import AdminUser


def create_admin_user():
    """Interactive script to create first admin user"""

    with app.app_context():
        # Check if admin user already exists
        existing_admin = AdminUser.query.first()
        if existing_admin:
            print("An admin user already exists!")
            print(f"Username: {existing_admin.username}")
            print(f"Email: {existing_admin.email}")
            print(f"Custom Login URL: /{existing_admin.custom_login_url}")
            return

        print("🔐 Creating your first admin user for secure backend access")
        print("=" * 60)

        # Get user input
        username = input("Enter username (min 3 characters): ").strip()
        while len(username) < 3:
            username = input("Username must be at least 3 characters: ").strip()

        email = input("Enter email address: ").strip()
        while "@" not in email:
            email = input("Please enter a valid email address: ").strip()

        print("\nPassword Requirements:")
        print("- At least 12 characters")
        print("- One uppercase letter")
        print("- One lowercase letter")
        print("- One number")
        print("- One special character (!@#$%^&*)")

        password = getpass("Enter password: ")
        confirm_password = getpass("Confirm password: ")

        while password != confirm_password:
            print("Passwords do not match!")
            password = getpass("Enter password: ")
            confirm_password = getpass("Confirm password: ")

        custom_url = input(
            "Enter custom login URL (leave blank for auto-generated): "
        ).strip()

        try:
            # Create admin user
            admin = AdminUser()
            admin.username = username
            admin.email = email
            admin.set_password(password)

            if custom_url:
                admin.custom_login_url = custom_url
            else:
                admin.custom_login_url = admin.generate_custom_login_url()

            db.session.add(admin)
            db.session.commit()

            print("\n✅ Admin user created successfully!")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Custom Login URL: /{admin.custom_login_url}")
            print(
                f"\nAccess your admin panel at: https://yoursite.com/{admin.custom_login_url}"
            )
            print("\n🔒 Keep your custom URL secure and don't share it publicly!")

        except ValueError as e:
            print(f"\n❌ Error: {e}")
            print("Please run the script again with a stronger password.")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating admin user: {e}")


if __name__ == "__main__":
    create_admin_user()
