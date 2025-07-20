# Secure Admin Login Setup Guide

## Overview

Your Grey Canvas website now includes a comprehensive secure admin authentication system with customizable login URLs and strong password requirements. This system operates independently from the existing Replit OAuth system, giving you complete control over your admin access.

## Key Features

### 🔒 Security Features
- **Custom Login URLs**: Hide your admin panel with unique, customizable URLs
- **Strong Password Requirements**: Enforced 12+ character passwords with complexity rules
- **Account Lockout**: Automatic protection against brute force attacks
- **Session Management**: Secure session handling with configurable timeouts
- **Audit Logging**: Track login attempts and security events

### 🛡️ Password Requirements
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*)

### 🔗 URL Management
- Generate secure, random login URLs
- Customize URLs with your preferred naming
- Change URLs anytime for enhanced security
- URLs use only safe characters (letters, numbers, hyphens, underscores)

## Getting Started

### Step 1: Create Your First Admin User

Run the interactive setup script:

```bash
python create_admin.py
```

This will guide you through:
- Creating your admin username and email
- Setting a secure password
- Choosing a custom login URL (or auto-generating one)

### Step 2: Access Your Admin Panel

Once created, you can access your admin panel at:
```
https://yoursite.com/your-custom-url
```

## Admin Management

### Command Line Tools

Use the admin management utility for advanced operations:

```bash
# List all admin users
python admin_management.py list

# Unlock a locked account
python admin_management.py unlock -u username

# Change password
python admin_management.py password -u username

# Generate new login URL
python admin_management.py url -u username

# Deactivate/activate account
python admin_management.py deactivate -u username
python admin_management.py activate -u username

# Security audit
python admin_management.py audit
```

### Web Interface

Access these features through your admin panel:

1. **Login**: Use your custom URL to access the secure login page
2. **Dashboard**: View and manage website inquiries and projects
3. **Settings**: Change passwords, update login URLs, view security status
4. **Password Change**: Update your password with security validation

## Security Best Practices

### 1. Custom Login URLs
- Change your login URL regularly (monthly recommended)
- Keep your URL confidential
- Use complex URLs that aren't easily guessable
- Consider using random generated URLs for maximum security

### 2. Password Management
- Use a strong, unique password
- Update passwords every 90 days
- Never reuse passwords from other accounts
- Consider using a password manager

### 3. Account Security
- Monitor login attempts and failed access
- Log out completely when finished
- Use secure connections (HTTPS) only
- Regularly run security audits

### 4. Access Control
- Only create admin accounts when necessary
- Deactivate unused accounts
- Review account activity regularly
- Use account lockout features

## Available Routes

### Public Routes (No Authentication)
- `/admin/setup` - First-time admin setup (only if no admin exists)

### Dynamic Login Routes
- `/your-custom-url` - Your personalized login page
- Each admin can have a unique URL

### Authenticated Routes (Login Required)
- `/admin/logout` - Sign out
- `/admin/change-password` - Update password
- `/admin/settings` - Account management
- `/admin/security-check` - Security status API
- `/admin/dashboard` - Main admin dashboard
- `/projects` - Project management
- All existing admin routes remain protected

## Technical Implementation

### Database Schema
The system adds an `admin_users` table with:
- User credentials (username, email, password hash)
- Security settings (custom URLs, lockout status)
- Audit information (login attempts, timestamps)
- Account status (active/inactive, password age)

### Security Features
- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection on all forms
- SQL injection prevention
- XSS protection with input escaping

### Integration
- Works alongside existing Replit OAuth system
- Maintains existing admin functionality
- Backwards compatible with current admin routes
- Secure session handling

## Troubleshooting

### Can't Access Admin Panel
1. Verify your custom login URL is correct
2. Check if account is locked (wait 30 minutes or use unlock command)
3. Ensure account is active
4. Confirm password meets requirements

### Forgot Login URL
1. Run `python admin_management.py list` to see current URLs
2. Generate new URL with `python admin_management.py url -u username`

### Password Issues
1. Ensure password meets all requirements
2. Use password change command: `python admin_management.py password -u username`
3. Check for account lockout status

### Account Locked
1. Wait 30 minutes for automatic unlock
2. Use unlock command: `python admin_management.py unlock -u username`
3. Run security audit to identify issues

## Migration Notes

### Existing Users
- Your existing Replit OAuth admin access continues to work
- New secure admin system runs in parallel
- No disruption to current admin functionality
- Can migrate gradually or use both systems

### Data Security
- All admin credentials are securely hashed
- Session data is encrypted
- Failed login attempts are logged
- Account activities are audited

## Support

For additional help:
1. Check the security audit: `python admin_management.py audit`
2. Review admin account status: `python admin_management.py list`
3. Verify system logs for authentication errors
4. Ensure database permissions are correct

## Next Steps

1. Create your first admin user
2. Test login with your custom URL
3. Update your password policy
4. Configure regular security audits
5. Document your custom URLs securely

Your admin panel is now significantly more secure with industry-standard authentication practices and customizable access controls.