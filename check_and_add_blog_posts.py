
#!/usr/bin/env python3
"""
Check for existing blog posts and add them if missing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import BlogPost
from sqlalchemy.exc import SQLAlchemyError
import logging

def check_and_add_blog_posts():
    """Check for blog posts and add them if missing"""
    with app.app_context():
        try:
            # Check how many blog posts we have
            post_count = BlogPost.query.count()
            print(f"Current blog posts in database: {post_count}")
            
            # List existing posts
            existing_posts = BlogPost.query.all()
            print("Existing blog posts:")
            for post in existing_posts:
                print(f"  - {post.title} (slug: {post.slug})")
            
            if post_count == 0:
                print("No blog posts found. Adding default posts...")
                add_default_posts()
            else:
                print("Blog posts found in database.")
                
        except Exception as e:
            print(f"Error checking blog posts: {e}")

def add_default_posts():
    """Add default blog posts"""
    try:
        # Add first blog post
        first_post = BlogPost()
        first_post.title = "Why Small Businesses in Texas Need a Professional Website in 2025"
        first_post.slug = "why-small-businesses-need-websites"
        first_post.content = """<h2>The Digital Landscape Has Changed</h2>
<p>In 2025, your website isn't just a digital business card—it's your storefront, your salesperson, and your credibility all rolled into one. For small businesses in Texas, especially in the DFW area, having a professional website is no longer optional.</p>

<h2>Local Competition is Fierce</h2>
<p>Whether you're a contractor in Dallas, a real estate agent in Fort Worth, or a freelancer in Arlington, your competitors are online. When potential customers search for services in your area, you need to be there.</p>

<h3>Key Benefits of a Professional Website:</h3>
<ul>
<li><strong>24/7 Availability:</strong> Your website works while you sleep, answering questions and generating leads.</li>
<li><strong>Credibility:</strong> A professional website builds trust before the first phone call.</li>
<li><strong>Local SEO:</strong> Show up when customers search for services "near me".</li>
<li><strong>Cost-Effective Marketing:</strong> More affordable than traditional advertising with better targeting.</li>
<li><strong>Mobile Accessibility:</strong> Reach customers on their phones, tablets, and computers.</li>
</ul>

<h2>What Texas Small Businesses Need</h2>
<p>Your website should reflect your business's personality while serving your customers' needs. This means:</p>

<blockquote>
"A website that looks professional, loads fast, and makes it easy for customers to contact you or learn about your services."
</blockquote>

<h3>Essential Features for Small Business Websites:</h3>
<ol>
<li><strong>Clear Contact Information:</strong> Make it easy to reach you</li>
<li><strong>Service Descriptions:</strong> Tell people exactly what you do</li>
<li><strong>Customer Reviews:</strong> Build social proof</li>
<li><strong>Mobile Optimization:</strong> Most customers will find you on their phone</li>
<li><strong>Fast Loading:</strong> Don't lose customers to slow pages</li>
</ol>

<h2>Ready to Get Started?</h2>
<p>Building a website doesn't have to be overwhelming. Whether you're ready to DIY or want professional help, the important thing is to start. Your future customers are searching for you right now—make sure they can find you.</p>

<p>Need help getting your small business online? I specialize in creating professional, affordable websites for Texas entrepreneurs. Let's chat about bringing your business to the digital world.</p>"""
        first_post.excerpt = "In 2025, your website isn't just a digital business card—it's your storefront, your salesperson, and your credibility all rolled into one. Learn why Texas small businesses need a professional online presence."
        first_post.tags = "small business, Texas, web design, DFW, local SEO, professional website"
        first_post.meta_description = "Discover why small businesses in Texas need professional websites in 2025. Learn the key benefits and essential features for success in the digital marketplace."
        first_post.published = True

        db.session.add(first_post)
        
        # Add redesign blog post
        redesign_post = BlogPost()
        redesign_post.title = "10 Signs Your Small Business Website Needs a Redesign in 2025"
        redesign_post.slug = "10-signs-website-needs-redesign-2025"
        redesign_post.content = """<h2><span style="color: #E0218A;">10</span> <span style="color: #7A7A7A;">Signs</span> Your <span style="color: #E0218A;">Small</span> <span style="color: #7A7A7A;">Business</span> Website Needs a <span style="color: #E0218A;">Redesign</span> in <span style="color: #7A7A7A;">2025</span></h2>

<p>Let's be honest. Your website is probably the hardest-working part of your business. It never sleeps, never calls in sick, and for many customers, it's your #1 salesperson.</p>

<p>But what happens when it starts letting you down?</p>

<p>I talk to business owners every day who have that nagging feeling that their website just isn't working anymore. They know something's off, but they can't quite pinpoint the problem. An underperforming website in 2025 isn't just a cosmetic issue; it's actively costing you customers and money.</p>

<p>If that sounds familiar, you're in the right place. Here are 10 signs I see all the time that show it's time for a change.</p>

<h3><span style="color: #E0218A;">1.</span> Your Website is a <span style="color: #E0218A;">Nightmare</span> on <span style="color: #7A7A7A;">Mobile</span></h3>

<p>This one is non-negotiable. Pull out your phone right now and load your website. Go ahead, I'll wait. Are you doing that awkward pinch-and-zoom dance just to read a sentence? Trying to tap a button the size of a pinhead? If so, you have a problem.</p>

<p>Most people will find you on their phones first. If that experience is clumsy, you've lost them before they even know what you do. Plus, Google ranks sites based on their mobile version first, so a bad mobile site means your search ranking suffers too.</p>

<h3><span style="color: #E0218A;">2.</span> It Loads at a <span style="color: #E0218A;">Snail's</span> <span style="color: #7A7A7A;">Pace</span></h3>

<p>Think about the last time you waited more than a few seconds for a page to load. What did you do? You left, right? We all do. If your website takes an eternity (which online means more than 3 seconds) to show up, your visitors are gone.</p>

<p>This isn't just about frustrating people; Google sees that slow load time, sees people leaving immediately, and pushes you down the search results.</p>

<h2>Ready to <span style="color: #E0218A;">Redesign</span> Your <span style="color: #7A7A7A;">Website</span>?</h2>

<p>Your website should be your most reliable employee. If it's not pulling its weight, let's fix that. Contact me for a free consultation and let's get your website working as hard as you do.</p>"""
        redesign_post.excerpt = "Is your website costing you customers? Here are 10 clear signs it's time for a redesign in 2025, from mobile nightmares to security issues that Google flags."
        redesign_post.tags = "web design, website redesign, small business, mobile optimization, SEO, user experience, 2025"
        redesign_post.meta_description = "Discover 10 clear signs your small business website needs a redesign in 2025. From mobile issues to slow loading times, learn what's costing you customers."
        redesign_post.featured_image = "https://hosting.photobucket.com/ffe76a37-34ae-4a9f-949c-780379ff74c1/1753616795406.jpeg?width=590&height=370&fit=bounds"
        redesign_post.published = True

        db.session.add(redesign_post)
        db.session.commit()
        
        print("✅ Default blog posts added successfully!")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Database error: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    check_and_add_blog_posts()
