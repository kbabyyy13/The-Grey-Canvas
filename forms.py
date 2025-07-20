from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = TelField('Phone', validators=[Optional(), Length(max=20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])

class IntakeForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=100)])
    contact_name = StringField('Contact Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = TelField('Phone', validators=[Optional(), Length(max=20)])
    
    website_type = SelectField('Website Type', choices=[
        ('', 'Select a website type'),
        ('business', 'Business Website'),
        ('ecommerce', 'E-commerce Store'),
        ('portfolio', 'Portfolio Site'),
        ('blog', 'Blog/Content Site'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    timeline = SelectField('Project Timeline', choices=[
        ('', 'Select your timeline'),
        ('asap', 'ASAP (Rush Fee May Apply)'),
        ('1-2weeks', '1-2 Weeks'),
        ('3-4weeks', '3-4 Weeks'),
        ('1-2months', '1-2 Months'),
        ('flexible', 'Flexible')
    ], validators=[DataRequired()])
    
    budget = SelectField('Budget Range', choices=[
        ('', 'Select your budget'),
        ('under1000', 'Under $1,000'),
        ('1000-2500', '$1,000 - $2,500'),
        ('2500-5000', '$2,500 - $5,000'),
        ('5000-10000', '$5,000 - $10,000'),
        ('over10000', 'Over $10,000')
    ], validators=[DataRequired()])
    
    project_description = TextAreaField('Project Description', validators=[DataRequired(), Length(min=20, max=2000)])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])

class NewsletterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
