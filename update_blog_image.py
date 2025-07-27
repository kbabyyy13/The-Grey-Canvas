#!/usr/bin/env python3
"""
Update the featured image for the website redesign blog post
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import BlogPost
from sqlalchemy.exc import SQLAlchemyError
import logging

def update_blog_image():
    """Update the featured image for the redesign blog post"""
    with app.app_context():
        # Find the blog post
        post = BlogPost.query.filter_by(slug="10-signs-website-needs-redesign-2025").first()
        if not post:
            print("❌ Blog post not found!")
            return

        # Update the featured image
        old_image = post.featured_image
        post.featured_image = "https://hosting.photobucket.com/ffe76a37-34ae-4a9f-949c-780379ff74c1/bb0985d5-f250-42c9-ad15-f0acf001bd9b.jpeg?width=960&height=720&fit=bounds"

        try:
            db.session.commit()
            print("✅ Blog post image updated successfully!")
            print(f"   Title: {post.title}")
            print(f"   Old Image: {old_image}")
            print(f"   New Image: {post.featured_image}")
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Database error updating blog post: {e}")
            print(f"❌ Database error: {e}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error updating blog post: {e}")
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    update_blog_image()