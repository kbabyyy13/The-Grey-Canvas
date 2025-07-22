import os
from datetime import datetime, timedelta
from flask import render_template, request, flash, redirect, url_for, make_response, session, jsonify
from flask_mail import Message
from flask_login import current_user
from markupsafe import escape
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload
from urllib.parse import urlparse, urljoin

from app import app, mail, db
from forms import ContactForm, IntakeForm, NewsletterForm
from models import (
    ContactSubmission, IntakeSubmission, BlogPost, 
    Project, ProjectTimelineEvent, User, OAuth, NewsletterSubscription, AdminUser
)
from replit_auth import require_login, make_replit_blueprint
from admin_auth import admin_auth
import logging

# Register the authentication blueprints
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")
app.register_blueprint(admin_auth)

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

def safe_redirect(url, fallback_endpoint='index'):
    """
    Safely redirect to a URL, preventing open redirect vulnerabilities.
    Only allows redirects to same-origin URLs.
    """
    if not url:
        return redirect(url_for(fallback_endpoint))
    
    try:
        parsed_url = urlparse(url)
        # Only allow redirects to same origin (no netloc means relative URL)
        if not parsed_url.netloc:
            return redirect(url)
        else:
            # External URL detected, redirect to fallback
            return redirect(url_for(fallback_endpoint))
    except Exception:
        # If parsing fails, redirect to fallback
        return redirect(url_for(fallback_endpoint))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/owner')
def owner():
    return render_template('owner.html')

@app.route('/company')
def company():
    return render_template('company.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            # Save to database with escaped data
            contact_submission = ContactSubmission()
            contact_submission.name = escape(form.name.data)
            contact_submission.email = form.email.data  # Email validation handles security
            contact_submission.phone = escape(form.phone.data) if form.phone.data else None
            contact_submission.subject = escape(form.subject.data)
            contact_submission.message = escape(form.message.data)
            
            db.session.add(contact_submission)
            db.session.commit()
            
            # Send email if configured
            if app.config.get('MAIL_DEFAULT_SENDER'):
                msg = Message(
                    subject=f'Contact Form: {form.subject.data}',
                    recipients=[app.config['MAIL_DEFAULT_SENDER']],
                    body=f"""
                    New contact form submission:
                    
                    Name: {form.name.data}
                    Email: {form.email.data}
                    Phone: {form.phone.data}
                    Subject: {form.subject.data}
                    
                    Message:
                    {form.message.data}
                    """
                )
                mail.send(msg)
            
            flash('Thank you for your message! We\'ll get back to you soon.', 'success')
            return redirect(url_for('contact'))
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f'Database error saving contact submission: {e}')
            flash('Sorry, there was a database error. Please try again.', 'error')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Unexpected error saving contact submission: {e}')
            flash('Sorry, there was an unexpected error. Please try again.', 'error')
    
    return render_template('contact.html', form=form)



@app.route('/thegrey')
def thegrey():
    return render_template('thegrey.html')

@app.route('/packages')
def packages():
    return render_template('packages.html')

@app.route('/plans')
def plans():
    return render_template('plans.html')

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/intake', methods=['GET', 'POST'])
def intake():
    form = IntakeForm()
    if form.validate_on_submit():
        try:
            # Save to database with escaped data
            intake_submission = IntakeSubmission()
            intake_submission.business_name = escape(form.business_name.data)
            intake_submission.contact_name = escape(form.contact_name.data)
            intake_submission.email = form.email.data  # Email validation handles security
            intake_submission.phone = escape(form.phone.data) if form.phone.data else None
            intake_submission.website_type = form.website_type.data  # SelectField - safe
            intake_submission.timeline = form.timeline.data  # SelectField - safe
            intake_submission.budget = form.budget.data  # SelectField - safe
            intake_submission.project_description = escape(form.project_description.data)
            intake_submission.additional_notes = escape(form.additional_notes.data) if form.additional_notes.data else None
            
            db.session.add(intake_submission)
            db.session.commit()
            
            # Send email if configured
            if app.config.get('MAIL_DEFAULT_SENDER'):
                msg = Message(
                    subject='New Client Intake Form Submission',
                    recipients=[app.config['MAIL_DEFAULT_SENDER']],
                    body=f"""
                    New client intake form submission:
                    
                    Business Name: {form.business_name.data}
                    Contact Name: {form.contact_name.data}
                    Email: {form.email.data}
                    Phone: {form.phone.data}
                    Website Type: {form.website_type.data}
                    Timeline: {form.timeline.data}
                    Budget: {form.budget.data}
                    
                    Project Description:
                    {form.project_description.data}
                    
                    Additional Notes:
                    {form.additional_notes.data}
                    """
                )
                mail.send(msg)
            
            flash('Thank you! Your intake form has been submitted. We\'ll review it and get back to you soon.', 'success')
            return redirect(url_for('intake'))
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f'Database error saving intake submission: {e}')
            flash('Sorry, there was a database error. Please try again.', 'error')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Unexpected error saving intake submission: {e}')
            flash('Sorry, there was an unexpected error. Please try again.', 'error')
    
    return render_template('intake.html', form=form)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Optimized for better grid layout (divisible by 2 and 3)
    
    try:
        # Optimized query with selective column loading and index usage
        posts = BlogPost.query.filter_by(published=True)\
            .order_by(BlogPost.created_at.desc())\
            .options(db.load_only(BlogPost.id, BlogPost.title, BlogPost.excerpt, 
                                 BlogPost.slug, BlogPost.created_at, BlogPost.author, 
                                 BlogPost.tags, BlogPost.featured_image))\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # If page number is too high, redirect to last page
        if page > posts.pages and posts.pages > 0:
            return redirect(url_for('blog', page=posts.pages))
            
    except SQLAlchemyError as e:
        logging.error(f'Database error loading blog posts: {e}')
        flash('Error loading blog posts. Please refresh the page.', 'error')
        # Return empty pagination object for graceful error handling
        posts = BlogPost.query.filter_by(published=True).paginate(page=1, per_page=per_page, error_out=False)
    
    # Set cache headers for better performance
    response = make_response(render_template('blog.html', posts=posts))
    response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes cache
    return response

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    # Get related posts (same tags)
    related_posts = []
    if post.tags:
        related_posts = BlogPost.query.filter(
            BlogPost.id != post.id,
            BlogPost.published == True,
            BlogPost.tags.contains(post.tags.split(',')[0])
        ).limit(3).all()
    
    return render_template('blog_post.html', post=post, related_posts=related_posts)

@app.route('/admin')
def admin_login():
    """Public admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@require_login
def admin_dashboard():
    """Enhanced admin dashboard for managing inquiries"""
    from datetime import datetime, timedelta
    
    # Get submission counts
    contact_count = ContactSubmission.query.count()
    intake_count = IntakeSubmission.query.count()
    
    # Get recent submissions (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_contacts = ContactSubmission.query.filter(ContactSubmission.submitted_at >= week_ago).count()
    recent_intakes = IntakeSubmission.query.filter(IntakeSubmission.submitted_at >= week_ago).count()
    recent_count = recent_contacts + recent_intakes
    
    # Get all submissions for the dashboard
    contact_submissions = ContactSubmission.query.order_by(ContactSubmission.submitted_at.desc()).all()
    intake_submissions = IntakeSubmission.query.order_by(IntakeSubmission.submitted_at.desc()).all()
    
    # Combine and prepare all inquiries with type information
    all_inquiries = []
    for submission in contact_submissions:
        submission.type = 'contact'
        all_inquiries.append(submission)
    for submission in intake_submissions:
        submission.type = 'intake'
        all_inquiries.append(submission)
    
    # Sort by submission date (newest first)
    all_inquiries.sort(key=lambda x: x.submitted_at, reverse=True)
    
    return render_template('admin_dashboard.html',
                         contact_count=contact_count,
                         intake_count=intake_count,
                         recent_count=recent_count,
                         all_inquiries=all_inquiries)

# API routes for inquiry management
@app.route('/admin/inquiry/<inquiry_type>/<int:inquiry_id>')
@require_login
def get_inquiry_details(inquiry_type, inquiry_id):
    """Get detailed information about a specific inquiry"""
    try:
        if inquiry_type == 'contact':
            inquiry = ContactSubmission.query.get_or_404(inquiry_id)
            data = {
                'id': inquiry.id,
                'type': 'contact',
                'name': inquiry.name,
                'email': inquiry.email,
                'phone': inquiry.phone,
                'subject': inquiry.subject,
                'message': inquiry.message,
                'submitted_at': inquiry.submitted_at.isoformat()
            }
        elif inquiry_type == 'intake':
            inquiry = IntakeSubmission.query.get_or_404(inquiry_id)
            data = {
                'id': inquiry.id,
                'type': 'intake',
                'business_name': inquiry.business_name,
                'contact_name': inquiry.contact_name,
                'email': inquiry.email,
                'phone': inquiry.phone,
                'website_type': inquiry.website_type,
                'timeline': inquiry.timeline,
                'budget': inquiry.budget,
                'project_description': inquiry.project_description,
                'additional_notes': inquiry.additional_notes,
                'submitted_at': inquiry.submitted_at.isoformat()
            }
        else:
            return jsonify({'error': 'Invalid inquiry type'}), 400
            
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching inquiry details: {e}")
        return jsonify({'error': 'Failed to fetch inquiry details'}), 500

@app.route('/admin/inquiry/<inquiry_type>/<int:inquiry_id>/complete', methods=['POST'])
@require_login
def mark_inquiry_complete(inquiry_type, inquiry_id):
    """Mark an inquiry as complete"""
    try:
        if inquiry_type == 'contact':
            inquiry = ContactSubmission.query.get_or_404(inquiry_id)
        elif inquiry_type == 'intake':
            inquiry = IntakeSubmission.query.get_or_404(inquiry_id)
        else:
            return jsonify({'error': 'Invalid inquiry type'}), 400
        
        # For now, we'll just add a note or we could add a status field to the models
        # Since we don't have a status field, we'll just return success
        # In a future update, we could add a status field to track inquiry states
        
        return jsonify({'success': True, 'message': 'Inquiry marked as complete'})
    except Exception as e:
        logging.error(f"Error marking inquiry complete: {e}")
        return jsonify({'error': 'Failed to mark inquiry complete'}), 500

@app.route('/admin/inquiry/<inquiry_type>/<int:inquiry_id>/delete', methods=['DELETE'])
@require_login
def delete_inquiry(inquiry_type, inquiry_id):
    """Delete an inquiry"""
    try:
        if inquiry_type == 'contact':
            inquiry = ContactSubmission.query.get_or_404(inquiry_id)
        elif inquiry_type == 'intake':
            inquiry = IntakeSubmission.query.get_or_404(inquiry_id)
        else:
            return jsonify({'error': 'Invalid inquiry type'}), 400
        
        db.session.delete(inquiry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Inquiry deleted successfully'})
    except Exception as e:
        logging.error(f"Error deleting inquiry: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete inquiry'}), 500

# Project Progress Tracking Routes
@app.route('/projects')
@require_login
def projects():
    """Project progress tracking dashboard with optimized queries"""
    try:
        # Get all projects - removing eager loading to fix LSP type issues
        all_projects = Project.query.order_by(Project.created_at.desc()).all()
        
        # Calculate statistics
        active_projects = len([p for p in all_projects if p.status not in ['completed', 'cancelled']])
        completed_projects = len([p for p in all_projects if p.status == 'completed'])
        overdue_projects = len([p for p in all_projects if p.is_overdue()])
        
        return render_template('projects.html',
                             projects=all_projects,
                             active_projects=active_projects,
                             completed_projects=completed_projects,
                             overdue_projects=overdue_projects)
    except SQLAlchemyError as e:
        logging.error(f'Database error loading projects: {e}')
        flash('Error loading projects data. Please refresh the page.', 'error')
        return render_template('projects.html', 
                             projects=[], 
                             active_projects=0, 
                             completed_projects=0, 
                             overdue_projects=0)

@app.route('/projects/create', methods=['GET', 'POST'])
@require_login
def create_project():
    """Create a new project from intake submission or manually"""
    if request.method == 'POST':
        try:
            # Get and validate form data with input sanitization
            client_name = escape(request.form.get('client_name', '').strip())
            project_name = escape(request.form.get('project_name', '').strip())
            project_type = request.form.get('project_type', '').strip()
            client_email = request.form.get('client_email', '').strip()
            client_phone = escape(request.form.get('client_phone', '').strip())
            description = escape(request.form.get('description', '').strip())
            budget = request.form.get('budget', '').strip()
            timeline = request.form.get('timeline', '').strip()
            intake_submission_id = request.form.get('intake_submission_id')
            
            # Validate required fields
            if not all([client_name, project_name, project_type, client_email]):
                raise ValueError("Missing required fields: client_name, project_name, project_type, client_email")
            
            # Create new project with safe assignment
            project = Project()
            project.client_name = client_name
            project.project_name = project_name
            project.project_type = project_type
            project.client_email = client_email
            project.client_phone = client_phone if client_phone else None
            project.description = description if description else None
            project.budget = budget if budget else None
            project.timeline = timeline if timeline else None
            project.status = 'inquiry'
            project.progress_percentage = 0
            project.current_phase = 'Initial Consultation'
            project.next_milestone = 'Project planning and wireframe creation'
            
            # Link to intake submission if provided
            if intake_submission_id:
                project.intake_submission_id = int(intake_submission_id)
            
            db.session.add(project)
            db.session.commit()
            
            # Create initial timeline event with safe assignment
            initial_event = ProjectTimelineEvent()
            initial_event.project_id = project.id
            initial_event.event_type = 'status_change'
            initial_event.title = 'Project Created'
            initial_event.description = f'Project "{project_name}" created for {client_name}'
            initial_event.created_by = current_user.email or current_user.id
            initial_event.new_status = 'inquiry'
            
            db.session.add(initial_event)
            db.session.commit()
            
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': True, 'project_id': project.id})
            else:
                flash('Project created successfully!', 'success')
                return redirect(url_for('projects'))
                
        except ValueError as e:
            logging.error(f"Validation error creating project: {e}")
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': str(e)}), 400
            else:
                flash(f'Validation error: {str(e)}', 'error')
                return redirect(url_for('create_project'))
        except SQLAlchemyError as e:
            logging.error(f"Database error creating project: {e}")
            db.session.rollback()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Database error occurred'}), 500
            else:
                flash('Database error creating project. Please try again.', 'error')
                return redirect(url_for('create_project'))
        except Exception as e:
            logging.error(f"Unexpected error creating project: {e}")
            db.session.rollback()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Unexpected error occurred'}), 500
            else:
                flash('Unexpected error creating project. Please try again.', 'error')
                return redirect(url_for('create_project'))
    
    # GET request - show create form with optional intake submission
    intake_submission_id = request.args.get('intake_id')
    intake_submission = None
    if intake_submission_id:
        intake_submission = IntakeSubmission.query.get_or_404(intake_submission_id)
    
    return render_template('create_project.html', intake_submission=intake_submission)

@app.route('/projects/<int:project_id>')
@require_login
def project_detail(project_id):
    """View detailed project information and timeline"""
    project = Project.query.get_or_404(project_id)
    timeline_events = project.timeline_events.order_by(ProjectTimelineEvent.event_date.desc()).all()
    
    return render_template('project_detail.html', project=project, timeline_events=timeline_events)

@app.route('/projects/<int:project_id>/update_status', methods=['POST'])
@require_login
def update_project_status(project_id):
    """Update project status and progress"""
    try:
        project = Project.query.get_or_404(project_id)
        old_status = project.status
        
        # Get form data
        new_status = request.form.get('status')
        progress = request.form.get('progress', type=int)
        current_phase = request.form.get('current_phase')
        next_milestone = request.form.get('next_milestone')
        notes = request.form.get('notes')
        
        # Update project
        if new_status:
            project.status = new_status
        if progress is not None:
            project.progress_percentage = min(100, max(0, progress))
        if current_phase:
            project.current_phase = current_phase
        if next_milestone:
            project.next_milestone = next_milestone
        if notes:
            project.notes = notes
            
        # Set completion date if completed
        if new_status == 'completed' and not project.actual_completion:
            project.actual_completion = datetime.utcnow()
            project.progress_percentage = 100
        
        db.session.commit()
        
        # Create timeline event for status change with safe assignment
        if new_status and new_status != old_status:
            event = ProjectTimelineEvent()
            event.project_id = project.id
            event.event_type = 'status_change'
            event.title = f'Status Updated to {project.get_status_display()}'
            event.description = f'Project status changed from {old_status} to {new_status}'
            event.created_by = current_user.email or current_user.id
            event.old_status = old_status
            event.new_status = new_status
            
            db.session.add(event)
            db.session.commit()
        
        return jsonify({'success': True, 'message': 'Project updated successfully'})
        
    except SQLAlchemyError as e:
        logging.error(f"Database error updating project: {e}")
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logging.error(f"Unexpected error updating project: {e}")
        db.session.rollback()
        return jsonify({'error': 'Unexpected error occurred'}), 500

@app.route('/projects/<int:project_id>/add_event', methods=['POST'])
@require_login
def add_timeline_event(project_id):
    """Add a new timeline event to a project"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Get form data
        event_type = request.form.get('event_type')
        title = request.form.get('title')
        description = request.form.get('description', '')
        is_milestone = request.form.get('is_milestone') == 'true'
        
        # Create timeline event with safe assignment
        event = ProjectTimelineEvent()
        event.project_id = project.id
        event.event_type = event_type
        event.title = escape(title) if title else ''
        event.description = escape(description) if description else ''
        event.created_by = current_user.email or current_user.id
        event.is_milestone = is_milestone
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Timeline event added successfully'})
        
    except SQLAlchemyError as e:
        logging.error(f"Database error adding timeline event: {e}")
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logging.error(f"Unexpected error adding timeline event: {e}")
        db.session.rollback()
        return jsonify({'error': 'Unexpected error occurred'}), 500

@app.route('/admin/console')
@require_login
def admin_console():
    """Admin console with optimized queries and error handling"""
    try:
        # Get submission counts efficiently
        contact_count = ContactSubmission.query.count()
        intake_count = IntakeSubmission.query.count()
        
        # Get recent submissions (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_contacts = ContactSubmission.query.filter(ContactSubmission.submitted_at >= week_ago).count()
        recent_intakes = IntakeSubmission.query.filter(IntakeSubmission.submitted_at >= week_ago).count()
        recent_count = recent_contacts + recent_intakes
        
        # Get recent submissions for activity feed with optimized queries
        contact_submissions = ContactSubmission.query.order_by(ContactSubmission.submitted_at.desc()).limit(10).all()
        intake_submissions = IntakeSubmission.query.order_by(IntakeSubmission.submitted_at.desc()).limit(10).all()
        
        # Combine and sort recent submissions efficiently
        recent_submissions = (
            list(contact_submissions[:5]) + 
            list(intake_submissions[:5])
        )
        recent_submissions.sort(key=lambda x: x.submitted_at, reverse=True)
        recent_submissions = recent_submissions[:5]  # Take only the 5 most recent
        
        return render_template('admin_console.html',
                             contact_count=contact_count,
                             intake_count=intake_count,
                             recent_count=recent_count,
                             contact_submissions=contact_submissions,
                             intake_submissions=intake_submissions,
                             recent_submissions=recent_submissions)
    except SQLAlchemyError as e:
        logging.error(f'Database error loading admin console: {e}')
        flash('Error loading admin data. Please refresh the page.', 'error')
        return render_template('admin_console.html',
                             contact_count=0,
                             intake_count=0,
                             recent_count=0,
                             contact_submissions=[],
                             intake_submissions=[],
                             recent_submissions=[])

@app.route('/admin/submissions')
@require_login
def admin_submissions():
    contact_submissions = ContactSubmission.query.order_by(ContactSubmission.submitted_at.desc()).all()
    intake_submissions = IntakeSubmission.query.order_by(IntakeSubmission.submitted_at.desc()).all()
    return render_template('admin_submissions.html', 
                         contact_submissions=contact_submissions,
                         intake_submissions=intake_submissions)

@app.route('/admin/add-first-post')
@require_login
def add_first_post():
    """Add your first blog post to the database"""
    # Check if the post already exists
    existing_post = BlogPost.query.filter_by(slug='why-small-businesses-need-websites').first()
    if existing_post:
        flash('First blog post already exists!', 'info')
        return redirect(url_for('blog'))
    
    # Create the first blog post with safe assignment
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
    
    try:
        db.session.add(first_post)
        db.session.commit()
        clear_sitemap_cache()  # Clear cache so new post appears in sitemap
        flash('First blog post added successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error adding first blog post: {e}")
        flash('Database error adding blog post. Please try again.', 'error')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error adding first blog post: {e}")
        flash('Unexpected error adding blog post. Please try again.', 'error')
    
    return redirect(url_for('blog'))

@app.route('/add-featured-post')
def add_featured_post():
    """Add a new featured blog post to the database"""
    # Check if the post already exists
    existing_post = BlogPost.query.filter_by(slug='future-of-web-design-2025').first()
    if existing_post:
        # Update existing post with featured image
        existing_post.featured_image = "https://hosting.photobucket.com/ffe76a37-34ae-4a9f-949c-780379ff74c1/e492cf05-51b9-4103-b275-9fde5aaf7461.jpeg?width=590&height=370&fit=bounds"
        try:
            db.session.commit()
            flash('Featured blog post updated with image!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Database error updating blog post: {e}")
            flash('Database error updating blog post. Please try again.', 'error')
        return redirect(url_for('blog'))
    
    # Create the new featured blog post
    featured_post = BlogPost()
    featured_post.title = "Will AI Take My Web Designer's Job? A No-Nonsense Guide for Small Businesses"
    featured_post.slug = "future-of-web-design-2025"
    featured_post.content = """<h2>Will <span style="color: #E0218A;">AI</span> Take My <span style="color: #E0218A;">Web Designer</span>'s Job? A <span style="color: #E0218A;">No</span>-Nonsense Guide for <span style="color: #E0218A;">Small</span> <span style="color: #7A7A7A;">Businesses</span></h2>

<p>Let's talk about the elephant in the room: Artificial Intelligence. You've seen it everywhere. It writes, it creates art, and now, it builds websites. As a small business owner in Texas, you're probably wondering, "Can I just use AI to build my website? Is it cheaper? Is it better?"</p>

<p>These are the right questions to ask. And as a developer who is constantly learning and adapting, I've spent a lot of time exploring these tools myself.</p>

<p>So, let's have an honest conversation about AI in web design and development—the good, the bad, and how it can actually help your business thrive without replacing the human touch.</p>

<h2><span style="color: #E0218A;">The Pros</span>: Where AI Shines (and Saves You Money)</h2>

<p>AI is an incredible tool, and when used correctly, it can make the development process faster and more efficient.</p>

<p><span style="color: #E0218A;">Speed & Efficiency</span>: AI can generate code snippets, design mockups, and even write first drafts of content in a fraction of the time it would take a human. For you, this means a quicker turnaround time on your project.</p>

<p><span style="color: #E0218A;">Cost-Effectiveness</span>: By automating repetitive tasks, I can spend more time on the things that really matter—like your brand strategy and custom features—which gives you more value for your investment.</p>

<p><span style="color: #E0218A;">Data-Driven Design</span>: AI can analyze data to suggest layouts and color schemes that are proven to convert, taking some of the guesswork out of the design process.</p>

<h2><span style="color: #E0218A;">The Cons</span>: Where a Human Is Still Essential</h2>

<p>Here is the honest truth: AI is a brilliant assistant, but it's a terrible artist. It can't capture the heart of your brand.</p>

<p><span style="color: #E0218A;">Lack</span> of Originality: AI models are trained on existing data, which means they often produce designs that feel generic or derivative. Your business is unique; your website should be too.</p>

<p>No Strategic "<span style="color: #E0218A;">Why</span>": AI can build a page, but it can't understand your business goals, your target audience's pain points, or the story you want to tell. It can't build a customer journey that feels empathetic and authentic.</p>

<p>The "<span style="color: #E0218A;">Good Enough</span>" Trap: AI often produces work that is technically correct but lacks soul. It can't make the intuitive design choices that create a truly memorable user experience.</p>

<h2><span style="color: #E0218A;">The</span> <span style="color: #7A7A7A;">Grey</span> <span style="color: #E0218A;">Canvas Approach</span>: AI as a Co-Pilot, Not the Pilot</h2>

<p>At The Grey Canvas, I use AI as a powerful co-pilot. It helps me work faster and smarter, but it never takes the driver's seat. I use it to automate the boring stuff so I can pour my energy into the parts of your project that require a human touch: the strategy, the creativity, and the collaborative partnership we build together.</p>

<h2>Top AI Tools in My Toolkit (2025)</h2>

<p>For those who are curious, here are some of the cost-efficient tools that are making waves in the development world.</p>

<h3>Top 10 AI Tools for <span style="color: #E0218A;">Front</span>-<span style="color: #E0218A;">End</span> & <span style="color: #E0218A;">Web</span> <span style="color: #7A7A7A;">Design</span>:</h3>

<ol>
<li><strong>GitHub Copilot</strong>: An AI pair programmer that suggests code and entire functions right in the editor.</li>
<li><strong>v0.dev by Vercel</strong>: Generates React components and UI layouts based on text prompts.</li>
<li><strong>Midjourney & DALL-E 3</strong>: For creating custom graphics, icons, and background textures.</li>
<li><strong>Uizard</strong>: Quickly turns hand-drawn sketches into digital wireframes and mockups.</li>
<li><strong>Khroma</strong>: An AI color tool that generates endless color palettes based on your preferences.</li>
<li><strong>Canva Magic Design</strong>: Instantly creates branded templates and mockups from a single image.</li>
<li><strong>Galileo AI</strong>: Creates high-fidelity UI designs from a simple text description.</li>
<li><strong>Fronty</strong>: Converts images into clean HTML and CSS code.</li>
<li><strong>ChatGPT-4o</strong>: Excellent for brainstorming content ideas, writing meta descriptions, and generating placeholder text.</li>
<li><strong>Jasper.ai</strong>: A powerful AI copywriter for crafting compelling headlines and website content.</li>
</ol>

<h3>Top 10 AI Tools for <span style="color: #E0218A;">Back</span>-<span style="color: #E0218A;">End</span> <span style="color: #7A7A7A;">Development</span>:</h3>

<ol>
<li><strong>CodeWhisperer (Amazon)</strong>: A real-time code suggestion tool that's great for server-side logic.</li>
<li><strong>Tabnine</strong>: An AI assistant that learns your coding patterns to provide personalized suggestions.</li>
<li><strong>Mutable.ai</strong>: An AI-powered tool that helps refactor and improve existing codebases.</li>
<li><strong>AskCodi</strong>: A developer's toolkit that can explain code, generate documentation, and write tests.</li>
<li><strong>Replit AI</strong>: A coding assistant built directly into the Replit development environment.</li>
<li><strong>Mintlify</strong>: Automatically generates beautiful, easy-to-read documentation for your code.</li>
<li><strong>Adrenaline</strong>: An AI that can help debug code and explain complex errors.</li>
<li><strong>Bugasura</strong>: An AI-powered bug tracker that helps manage and prioritize issues.</li>
<li><strong>CodePal</strong>: Offers code generation, unit testing, and a "code reviewer" feature.</li>
<li><strong>Akkio</strong>: A no-code AI platform that can be used to build and deploy data models for your application.</li>
</ol>

<h2>How You Can Leverage AI for Your Business (Even if You're Not a Coder)</h2>

<p>You don't need to be a developer to make AI work for you. Here are a few simple tips:</p>

<p>Use AI for <span style="color: #E0218A;">Inspiration</span>, Not <span style="color: #E0218A;">Imitation</span>: Use tools like Midjourney or Canva to brainstorm visual ideas for your brand, but always bring them to a designer to refine and make them unique.</p>

<p>Draft Content with AI: Use ChatGPT or Jasper.ai to create a first draft of your "About Us" page or a blog post, then edit it to add your personal voice and story.</p>

<p>Work with a Developer Who Understands AI: The best approach is to partner with a professional who knows how to leverage these tools to your advantage, saving you time and money while still delivering a high-quality, custom product.</p>

<h2>The <span style="color: #E0218A;">Final</span> Word</h2>

<p>AI is a powerful tool, but it's just that—a tool. It can't replace the empathy, strategy, and creative spark that comes from a true human partnership. At The Grey Canvas, I'm committed to using the best of both worlds to build you a website that is not only technically excellent but also deeply authentic to your brand.</p>

<p>Ready to build something with heart and purpose? Let's start your project today.</p>"""
    featured_post.excerpt = "The honest truth about AI in web design: where it shines, where it fails, and how The Grey Canvas uses AI as a co-pilot (not the pilot) to deliver authentic, strategic websites for Texas small businesses."
    featured_post.tags = "web design trends, 2025, AI design, mobile-first, UX design, small business, Texas, future of web"
    featured_post.meta_description = "Will AI replace web designers? Get the honest truth about AI in web design, including 20 top AI tools and how to leverage AI for your small business without losing the human touch."
    featured_post.featured_image = "https://hosting.photobucket.com/ffe76a37-34ae-4a9f-949c-780379ff74c1/e492cf05-51b9-4103-b275-9fde5aaf7461.jpeg?width=590&height=370&fit=bounds"
    featured_post.published = True
    
    try:
        db.session.add(featured_post)
        db.session.commit()
        clear_sitemap_cache()  # Clear cache so new post appears in sitemap
        flash('Featured blog post added successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error adding featured blog post: {e}")
        flash('Database error adding blog post. Please try again.', 'error')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unexpected error adding featured blog post: {e}")
        flash('Unexpected error adding blog post. Please try again.', 'error')
    
    return redirect(url_for('blog'))

@app.route('/robots.txt')
def robots_txt():
    """Generate comprehensive robots.txt for optimal SEO crawling"""
    robots_content = """User-agent: *
Allow: /

# Allow all search engines to index the site
# Sitemap location for enhanced crawling
Sitemap: {}/sitemap.xml

# IMPORTANT: Disallow admin areas for security
Disallow: /admin/
Disallow: /auth/
Disallow: /api/
Disallow: /projects/

# Allow all important business pages for indexing
Allow: /
Allow: /services
Allow: /overview
Allow: /packages
Allow: /plans
Allow: /portfolio
Allow: /about
Allow: /owner
Allow: /company
Allow: /contact
Allow: /intake
Allow: /blog
Allow: /blog/*

Allow: /thegrey
Allow: /privacy-policy
Allow: /terms-of-service

# Allow static assets
Allow: /static/

# Respectful crawling - prevent server overload
Crawl-delay: 1

# Additional directives for comprehensive SEO
User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Bingbot
Allow: /
Crawl-delay: 1

User-agent: Slurp
Allow: /
Crawl-delay: 2

# Block common scrapers that add no SEO value
User-agent: CCBot
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Claude-Web
Disallow: /
""".format(request.url_root.rstrip('/'))
    
    response = make_response(robots_content)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
    return response

# Sitemap cache variables
_sitemap_cache = None
_sitemap_cache_time = None
_sitemap_cache_duration = 3600  # 1 hour in seconds

def clear_sitemap_cache():
    """Clear the sitemap cache to force regeneration"""
    global _sitemap_cache, _sitemap_cache_time
    _sitemap_cache = None
    _sitemap_cache_time = None

@app.route('/sitemap.xml')
def sitemap():
    """Generate comprehensive XML sitemap for enhanced SEO and search engine crawling"""
    from datetime import datetime, timedelta
    
    global _sitemap_cache, _sitemap_cache_time
    
    # Check if we have a valid cached sitemap
    current_time = datetime.now()
    if (_sitemap_cache and _sitemap_cache_time and 
        (current_time - _sitemap_cache_time).total_seconds() < _sitemap_cache_duration):
        response = make_response(_sitemap_cache)
        response.headers['Content-Type'] = 'application/xml; charset=utf-8'
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    
    # Use request URL to get the actual domain (supports both dev and production)
    base_url = request.url_root.rstrip('/')
    
    # Static pages with optimized priorities and change frequencies for better crawling
    static_pages = [
        # High priority pages - main business pages
        {'url': '/', 'priority': '1.0', 'changefreq': 'weekly', 'lastmod': datetime.now()},
        {'url': '/services', 'priority': '0.9', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/contact', 'priority': '0.9', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/intake', 'priority': '0.9', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        
        # Service detail pages - important for conversion
        {'url': '/overview', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/packages', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/plans', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': datetime.now()},

        
        # Portfolio and content pages
        {'url': '/portfolio', 'priority': '0.8', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/blog', 'priority': '0.8', 'changefreq': 'weekly', 'lastmod': datetime.now()},
        
        # About and company pages
        {'url': '/about', 'priority': '0.7', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/owner', 'priority': '0.7', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/company', 'priority': '0.7', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        {'url': '/thegrey', 'priority': '0.6', 'changefreq': 'monthly', 'lastmod': datetime.now()},
        
        # Legal pages - lower priority but important for trust
        {'url': '/privacy-policy', 'priority': '0.3', 'changefreq': 'yearly', 'lastmod': datetime.now()},
        {'url': '/terms-of-service', 'priority': '0.3', 'changefreq': 'yearly', 'lastmod': datetime.now()},
    ]
    
    try:
        # Get all published blog posts with error handling
        blog_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    except Exception as e:
        logging.error(f"Error fetching blog posts for sitemap: {e}")
        blog_posts = []
    
    # Generate XML sitemap with proper encoding and namespaces
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    sitemap_xml += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    sitemap_xml += 'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 '
    sitemap_xml += 'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
    
    # Add static pages with proper XML formatting
    for page in static_pages:
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>{base_url}{page["url"]}</loc>\n'
        sitemap_xml += f'    <lastmod>{page["lastmod"].strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        sitemap_xml += f'    <priority>{page["priority"]}</priority>\n'
        sitemap_xml += '  </url>\n'
    
    # Add blog posts with dynamic content handling
    for post in blog_posts:
        # Use the actual post update date for better crawling
        last_modified = post.updated_at if post.updated_at else post.created_at
        
        # Determine change frequency based on post age
        post_age = datetime.utcnow() - post.created_at
        if post_age.days < 30:
            change_freq = 'weekly'
            priority = '0.7'
        elif post_age.days < 90:
            change_freq = 'monthly'
            priority = '0.6'
        else:
            change_freq = 'yearly'
            priority = '0.5'
        
        sitemap_xml += '  <url>\n'
        sitemap_xml += f'    <loc>{base_url}/blog/{post.slug}</loc>\n'
        sitemap_xml += f'    <lastmod>{last_modified.strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_xml += f'    <changefreq>{change_freq}</changefreq>\n'
        sitemap_xml += f'    <priority>{priority}</priority>\n'
        sitemap_xml += '  </url>\n'
    
    sitemap_xml += '</urlset>'
    
    # Cache the generated sitemap
    _sitemap_cache = sitemap_xml
    _sitemap_cache_time = current_time
    
    # Create response with proper headers for search engines
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
    return response

@app.route('/admin/export-data')
@require_login
def export_data():
    """Export all data as XML"""
    from datetime import datetime
    
    # Get all data from database
    contact_submissions = ContactSubmission.query.all()
    intake_submissions = IntakeSubmission.query.all()
    blog_posts = BlogPost.query.all()
    
    # Create XML export
    xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_data += f'<grey_canvas_data export_date="{datetime.now().isoformat()}">\n'
    
    # Export contact submissions
    xml_data += '  <contact_submissions>\n'
    for contact in contact_submissions:
        xml_data += f'    <submission id="{contact.id}">\n'
        xml_data += f'      <name><![CDATA[{contact.name}]]></name>\n'
        xml_data += f'      <email><![CDATA[{contact.email}]]></email>\n'
        xml_data += f'      <phone><![CDATA[{contact.phone or ""}]]></phone>\n'
        xml_data += f'      <subject><![CDATA[{contact.subject}]]></subject>\n'
        xml_data += f'      <message><![CDATA[{contact.message}]]></message>\n'
        xml_data += f'      <submitted_at>{contact.submitted_at.isoformat()}</submitted_at>\n'
        xml_data += f'    </submission>\n'
    xml_data += '  </contact_submissions>\n'
    
    # Export intake submissions
    xml_data += '  <intake_submissions>\n'
    for intake in intake_submissions:
        xml_data += f'    <submission id="{intake.id}">\n'
        xml_data += f'      <business_name><![CDATA[{intake.business_name}]]></business_name>\n'
        xml_data += f'      <contact_name><![CDATA[{intake.contact_name}]]></contact_name>\n'
        xml_data += f'      <email><![CDATA[{intake.email}]]></email>\n'
        xml_data += f'      <phone><![CDATA[{intake.phone or ""}]]></phone>\n'
        xml_data += f'      <website_type><![CDATA[{intake.website_type}]]></website_type>\n'
        xml_data += f'      <timeline><![CDATA[{intake.timeline}]]></timeline>\n'
        xml_data += f'      <budget><![CDATA[{intake.budget}]]></budget>\n'
        xml_data += f'      <project_description><![CDATA[{intake.project_description}]]></project_description>\n'
        xml_data += f'      <additional_notes><![CDATA[{intake.additional_notes or ""}]]></additional_notes>\n'
        xml_data += f'      <submitted_at>{intake.submitted_at.isoformat()}</submitted_at>\n'
        xml_data += f'    </submission>\n'
    xml_data += '  </intake_submissions>\n'
    
    # Export blog posts
    xml_data += '  <blog_posts>\n'
    for post in blog_posts:
        xml_data += f'    <post id="{post.id}">\n'
        xml_data += f'      <title><![CDATA[{post.title}]]></title>\n'
        xml_data += f'      <slug><![CDATA[{post.slug}]]></slug>\n'
        xml_data += f'      <content><![CDATA[{post.content}]]></content>\n'
        xml_data += f'      <excerpt><![CDATA[{post.excerpt or ""}]]></excerpt>\n'
        xml_data += f'      <author><![CDATA[{post.author}]]></author>\n'
        xml_data += f'      <published>{str(post.published).lower()}</published>\n'
        xml_data += f'      <featured_image><![CDATA[{post.featured_image or ""}]]></featured_image>\n'
        xml_data += f'      <tags><![CDATA[{post.tags or ""}]]></tags>\n'
        xml_data += f'      <meta_description><![CDATA[{post.meta_description or ""}]]></meta_description>\n'
        xml_data += f'      <created_at>{post.created_at.isoformat()}</created_at>\n'
        xml_data += f'      <updated_at>{post.updated_at.isoformat()}</updated_at>\n'
        xml_data += f'    </post>\n'
    xml_data += '  </blog_posts>\n'
    
    xml_data += '</grey_canvas_data>'
    
    response = make_response(xml_data)
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = f'attachment; filename=grey_canvas_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xml'
    return response

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """Handle newsletter subscription from footer form"""
    form = NewsletterForm()
    
    if form.validate_on_submit():
        try:
            # Check if email already exists
            existing_subscription = NewsletterSubscription.query.filter_by(email=form.email.data).first()
            
            if existing_subscription:
                if existing_subscription.is_active:
                    flash('You are already subscribed to our newsletter!', 'info')
                else:
                    # Reactivate subscription
                    existing_subscription.is_active = True
                    db.session.commit()
                    flash('Welcome back! Your newsletter subscription has been reactivated.', 'success')
            else:
                # Create new subscription
                subscription = NewsletterSubscription()
                subscription.email = form.email.data
                db.session.add(subscription)
                db.session.commit()
                
                # Send welcome email if configured
                if app.config.get('MAIL_DEFAULT_SENDER'):
                    msg = Message(
                        subject='Welcome to The Grey Canvas Newsletter!',
                        recipients=[form.email.data] if form.email.data else [],
                        body=f"""
                        Welcome to The Grey Canvas Newsletter!
                        
                        Thank you for subscribing to our newsletter. You'll receive:
                        - Web design tips and trends
                        - Small business digital marketing insights
                        - Latest projects and case studies
                        - Special offers and announcements
                        
                        We promise no spam - just pixels, stories, and the occasional existential crisis!
                        
                        Best regards,
                        Krysta McAlister
                        The Grey Canvas Co.
                        """
                    )
                    # Send notification to admin
                    admin_msg = Message(
                        subject='New Newsletter Subscription',
                        recipients=[app.config['MAIL_DEFAULT_SENDER']],
                        body=f'New newsletter subscription from: {form.email.data}'
                    )
                    mail.send(msg)
                    mail.send(admin_msg)
                
                flash('Thank you for subscribing! Check your email for a welcome message.', 'success')
                
        except IntegrityError:
            db.session.rollback()
            flash('You are already subscribed to our newsletter!', 'info')
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f'Database error saving newsletter subscription: {e}')
            flash('Sorry, there was an error subscribing you to our newsletter. Please try again.', 'error')
        except Exception as e:
            db.session.rollback()
            logging.error(f'Unexpected error saving newsletter subscription: {e}')
            flash('Sorry, there was an unexpected error. Please try again.', 'error')
    else:
        flash('Please enter a valid email address.', 'error')
    
    # Redirect back to the page they came from or home (safely)
    return safe_redirect(request.referrer, 'index')

@app.route('/test-sentry')
def test_sentry():
    """Test route to trigger Sentry error reporting - only for development"""
    if os.environ.get('SENTRY_ENVIRONMENT') == 'production':
        flash('Error testing is disabled in production.', 'warning')
        return redirect(url_for('index'))
    
    # This will trigger a Sentry error report
    division_by_zero = 1 / 0
    return "<p>This should never be reached</p>"

@app.route('/test-sentry-message')
def test_sentry_message():
    """Test route to send a custom message to Sentry"""
    if os.environ.get('SENTRY_ENVIRONMENT') == 'production':
        flash('Error testing is disabled in production.', 'warning')
        return redirect(url_for('index'))
    
    import sentry_sdk
    sentry_sdk.capture_message("Test message from The Grey Canvas", level="info")
    flash('Test message sent to Sentry successfully!', 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
