#!/usr/bin/env python3
"""
Security Analysis for The Grey Canvas
Quick security assessment focused on critical vulnerabilities
"""

import ast
import os
import re
import subprocess
from datetime import datetime


def check_critical_security():
    """Check for critical security vulnerabilities"""
    print("🔒 Security Analysis for The Grey Canvas")
    print("=" * 50)
    
    critical_issues = []
    high_issues = []
    medium_issues = []
    
    # 1. Check for hardcoded secrets
    print("\n🔍 Checking for hardcoded secrets...")
    python_files = ['app.py', 'routes.py', 'models.py', 'admin_auth.py']
    
    for file_path in python_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for environment variable usage (GOOD)
            if 'os.environ.get' in content or 'getenv' in content:
                print(f"   ✅ {file_path}: Uses environment variables")
            
            # Check for hardcoded credentials (BAD)
            secret_patterns = [
                r'secret_key\s*=\s*["\'][^"\']{10,}["\']',
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']'
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if 'os.environ' not in content:
                        critical_issues.append(f"Hardcoded secret in {file_path}")
    
    # 2. Check session configuration
    print("\n🔑 Checking session security...")
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            app_content = f.read()
            
        if 'os.environ.get("SESSION_SECRET")' in app_content:
            print("   ✅ Session secret uses environment variable")
        elif 'secret_key' in app_content and '"' in app_content:
            critical_issues.append("Session secret may be hardcoded")
    
    # 3. Check CSRF protection
    print("\n🛡️  Checking CSRF protection...")
    if os.path.exists('routes.py'):
        with open('routes.py', 'r') as f:
            routes_content = f.read()
            
        if 'csrf.protect' in routes_content or 'CSRFProtect' in routes_content:
            print("   ✅ CSRF protection configured")
        elif 'FlaskForm' in routes_content:
            print("   ✅ Using WTForms (includes CSRF protection)")
        else:
            high_issues.append("No clear CSRF protection found")
    
    # 4. Check SQL injection prevention
    print("\n💉 Checking SQL injection prevention...")
    sql_injection_safe = True
    if os.path.exists('routes.py'):
        with open('routes.py', 'r') as f:
            routes_content = f.read()
            
        # Look for dangerous SQL patterns
        dangerous_patterns = [
            r'\.execute\s*\(\s*["\'].*%.*["\']',  # String formatting in SQL
            r'\.execute\s*\(\s*.*\+.*\)',         # String concatenation in SQL
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, routes_content):
                critical_issues.append("Potential SQL injection vulnerability")
                sql_injection_safe = False
                
        if sql_injection_safe and 'SQLAlchemy' in routes_content:
            print("   ✅ Using SQLAlchemy ORM (protects against SQL injection)")
    
    # 5. Check input validation
    print("\n🔍 Checking input validation...")
    if os.path.exists('forms.py'):
        with open('forms.py', 'r') as f:
            forms_content = f.read()
            
        if 'validators=' in forms_content and 'DataRequired' in forms_content:
            print("   ✅ Form validation implemented")
        else:
            medium_issues.append("Limited form validation found")
    
    # 6. Check file permissions
    print("\n📁 Checking file permissions...")
    sensitive_files = ['app.py', 'routes.py', 'models.py']
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            stats = os.stat(file_path)
            mode = oct(stats.st_mode)[-3:]
            if mode[2] in ['4', '5', '6', '7']:  # World readable
                medium_issues.append(f"File {file_path} is world-readable")
    
    # 7. Check for debug mode in production
    print("\n🐛 Checking debug configuration...")
    if os.path.exists('main.py'):
        with open('main.py', 'r') as f:
            main_content = f.read()
            
        if 'debug=True' in main_content:
            high_issues.append("Debug mode enabled in main.py")
        else:
            print("   ✅ Debug mode not hardcoded")
    
    # Generate security report
    print("\n" + "=" * 50)
    print("🎯 SECURITY ASSESSMENT SUMMARY")
    print("=" * 50)
    
    total_issues = len(critical_issues) + len(high_issues) + len(medium_issues)
    
    if len(critical_issues) > 0:
        print(f"\n🚨 CRITICAL ISSUES ({len(critical_issues)}):")
        for issue in critical_issues:
            print(f"   • {issue}")
    
    if len(high_issues) > 0:
        print(f"\n⚠️  HIGH PRIORITY ISSUES ({len(high_issues)}):")
        for issue in high_issues:
            print(f"   • {issue}")
    
    if len(medium_issues) > 0:
        print(f"\n📋 MEDIUM PRIORITY ISSUES ({len(medium_issues)}):")
        for issue in medium_issues:
            print(f"   • {issue}")
    
    # Calculate security score
    security_score = 100
    security_score -= len(critical_issues) * 30
    security_score -= len(high_issues) * 15
    security_score -= len(medium_issues) * 5
    security_score = max(0, security_score)
    
    print(f"\n🏆 SECURITY SCORE: {security_score}/100")
    
    if security_score >= 90:
        print("✅ EXCELLENT: Production-ready security")
    elif security_score >= 75:
        print("✅ GOOD: Minor security improvements needed")
    elif security_score >= 60:
        print("⚠️  FAIR: Several security issues to address")
    else:
        print("🚨 POOR: Critical security improvements required")
    
    return security_score, critical_issues, high_issues, medium_issues

def check_production_readiness():
    """Check production deployment readiness"""
    print("\n\n🚀 PRODUCTION READINESS CHECK")
    print("=" * 50)
    
    production_ready = True
    issues = []
    
    # Check environment variables
    required_env_vars = ['SESSION_SECRET', 'DATABASE_URL']
    for var in required_env_vars:
        if var in os.environ:
            print(f"   ✅ {var} is configured")
        else:
            print(f"   ⚠️  {var} not found in environment")
            issues.append(f"Missing environment variable: {var}")
            production_ready = False
    
    # Check for development settings
    dev_indicators = ['debug=True', 'DEBUG=True', 'localhost']
    for file_path in ['app.py', 'main.py', 'routes.py']:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                for indicator in dev_indicators:
                    if indicator in content and 'os.environ' not in content:
                        issues.append(f"Development setting in {file_path}: {indicator}")
                        production_ready = False
    
    # Check HTTPS readiness
    if os.path.exists('app.py'):
        with open('app.py', 'r') as f:
            app_content = f.read()
            if 'ProxyFix' in app_content:
                print("   ✅ HTTPS proxy configuration found")
            else:
                issues.append("Missing HTTPS proxy configuration")
                production_ready = False
    
    if production_ready:
        print("\n✅ PRODUCTION READY!")
    else:
        print(f"\n⚠️  {len(issues)} issues to address before production:")
        for issue in issues:
            print(f"   • {issue}")
    
    return production_ready, issues

if __name__ == "__main__":
    print("Starting security analysis...\n")
    
    # Run security check
    score, critical, high, medium = check_critical_security()
    
    # Run production readiness check  
    ready, prod_issues = check_production_readiness()
    
    print(f"\n{'='*50}")
    print("FINAL ASSESSMENT")
    print(f"{'='*50}")
    print(f"Security Score: {score}/100")
    print(f"Production Ready: {'Yes' if ready else 'No'}")
    
    if score >= 75 and ready:
        print("\n🎉 Website is secure and ready for deployment!")
    elif score >= 75:
        print("\n✅ Website is secure but needs production configuration")
    else:
        print("\n🚨 Website needs security improvements before deployment")