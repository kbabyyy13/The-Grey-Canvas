#!/usr/bin/env python3
"""
Add the new blog post about website redesign signs to the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import BlogPost
from sqlalchemy.exc import SQLAlchemyError
import logging

def add_redesign_blog_post():
    """Add the website redesign signs blog post"""
    with app.app_context():
        # Check if the post already exists
        existing_post = BlogPost.query.filter_by(slug="10-signs-website-needs-redesign-2025").first()
        if existing_post:
            print("Blog post already exists!")
            return

        # Create the new blog post
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

<h3><span style="color: #E0218A;">3.</span> Your Design Looks Like a <span style="color: #E0218A;">Throwback</span></h3>

<p>Does your website have that distinct "early internet" vibe? Look, design trends move fast. A website that looked sharp a few years ago can easily look ancient today. It's like showing up to a client meeting in a dated suit—it sends the wrong message.</p>

<p>Your website should scream "current, professional, and trustworthy," not "we haven't updated anything in a decade."</p>

<h3><span style="color: #E0218A;">4.</span> You're Getting <span style="color: #E0218A;">Clicks</span>, but No <span style="color: #7A7A7A;">Customers</span></h3>

<p>Let's get down to brass tacks. Your website exists to do a job: get you leads, sales, or new clients. If people are visiting but the phone isn't ringing and your inbox is empty, your website isn't doing its job.</p>

<p>It's like having a beautiful storefront with a locked door. Usually, the culprit is confusing navigation, a poor user experience, or no clear "next step" for the visitor to take.</p>

<h3><span style="color: #E0218A;">5.</span> Updating It is a <span style="color: #E0218A;">Total</span> <span style="color: #7A7A7A;">Chore</span></h3>

<p>Do you dread needing to update your website? Do you have to email a developer (and wait for an invoice) just to change your business hours or add a new testimonial? That's a huge bottleneck.</p>

<p>A modern website should put you in the driver's seat. You should be able to post a blog or tweak your services page easily, without needing a degree in computer science.</p>

<h3><span style="color: #E0218A;">6.</span> Your Competitors Are <span style="color: #E0218A;">Eating</span> Your Lunch <span style="color: #7A7A7A;">Online</span></h3>

<p>Let's do a little recon. Open up the websites of your top three competitors. How does yours stack up? Be honest. Customers absolutely judge a book by its cover online.</p>

<p>If their site is clean, fast, and professional, and yours is... not, you're starting the race with a lead weight tied to your ankle.</p>

<h3><span style="color: #E0218A;">7.</span> It's Not <span style="color: #E0218A;">Secure</span> (and Google is <span style="color: #7A7A7A;">Flagging</span> It)</h3>

<p>This one's simple but crucial. Look at your web address in the browser. See that little padlock icon? If you don't, and especially if you see a "Not Secure" warning, you're telling visitors "don't trust me."</p>

<p>Google hates it, and potential customers will hit the back button in a heartbeat. In 2025, having a secure site (HTTPS) is a basic requirement, like having a lock on your front door.</p>

<h3><span style="color: #E0218A;">8.</span> Your "<span style="color: #E0218A;">Bounce</span> Rate" is Through the <span style="color: #7A7A7A;">Roof</span></h3>

<p>Ever heard of "bounce rate"? It's basically when someone lands on your site, says "nope," and leaves without clicking anything. A high bounce rate is the ultimate signal that you're not giving people what they want.</p>

<p>It's the digital equivalent of a customer walking into your store, looking around for two seconds, and walking right back out.</p>

<h3><span style="color: #E0218A;">9.</span> You're Ignoring a <span style="color: #E0218A;">Huge</span> Group of <span style="color: #7A7A7A;">Customers</span></h3>

<p>Could a potential customer with a visual impairment use your website? A huge chunk of the population uses tools like screen readers to browse the web.</p>

<p>Making your site accessible isn't just the right thing to do; it's smart business. You're opening your doors to a wider audience that your competitors are probably ignoring.</p>

<h3><span style="color: #E0218A;">10.</span> It No Longer <span style="color: #E0218A;">Represents</span> Your <span style="color: #7A7A7A;">Business</span></h3>

<p>Businesses change. You add services, drop others, and find a new niche. Does your website reflect the business you are today, or the one you were five years ago?</p>

<p>If your site is a time capsule of your old business model, it's not just outdated—it's actively misinforming your best potential customers.</p>

<blockquote>
<p>"If you were nodding your head to more than a couple of these points, it's a clear sign. Your website isn't just a digital business card; it's a tool that should be making you money. If it's not, it's time for an upgrade."</p>
</blockquote>

<h3>Ready to <span style="color: #E0218A;">Redesign</span> Your <span style="color: #7A7A7A;">Website</span>?</h3>

<p>Your website should be your most reliable employee. If it's not pulling its weight, let's fix that. Contact me for a free consultation and let's get your website working as hard as you do.</p>"""

        redesign_post.excerpt = "Is your website costing you customers? Here are 10 clear signs it's time for a redesign in 2025, from mobile nightmares to security issues that Google flags."
        redesign_post.tags = "web design, website redesign, small business, mobile optimization, SEO, user experience, 2025"
        redesign_post.meta_description = "Discover 10 clear signs your small business website needs a redesign in 2025. From mobile issues to slow loading times, learn what's costing you customers."
        redesign_post.featured_image = "https://hosting.photobucket.com/ffe76a37-34ae-4a9f-949c-780379ff74c1/1753616795406.jpeg?width=590&height=370&fit=bounds"
        redesign_post.published = True

        try:
            db.session.add(redesign_post)
            db.session.commit()
            print("✅ Website redesign blog post added successfully!")
            print(f"   Title: {redesign_post.title}")
            print(f"   Slug: {redesign_post.slug}")
            print(f"   Featured Image: {redesign_post.featured_image}")
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Database error adding blog post: {e}")
            print(f"❌ Database error: {e}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error adding blog post: {e}")
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    add_redesign_blog_post()