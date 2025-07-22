#!/usr/bin/env python3
"""
Comprehensive Code and Website Scan for The Grey Canvas
Performs security analysis, code quality review, performance audit, and accessibility testing
"""

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class ComprehensiveScan:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.issues = []
        self.security_issues = []
        self.performance_issues = []
        self.accessibility_issues = []
        self.code_quality_issues = []
        self.seo_issues = []
        
        # Pages to scan
        self.pages = [
            '/',
            '/about',
            '/services', 
            '/packages',
            '/plans',
            '/overview',
            '/contact',
            '/intake',
            '/blog',
            '/company',
            '/owner',
            '/thegrey',
            '/portfolio',
            '/privacy-policy',
            '/terms-of-service'
        ]
        
        print(f"🔍 Starting comprehensive scan of The Grey Canvas website...")
        print(f"📍 Base URL: {base_url}")
        print(f"📅 Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def log_issue(self, category, severity, message, file_path=None, line_number=None):
        """Log an issue with severity and category"""
        issue = {
            'category': category,
            'severity': severity,
            'message': message,
            'file': file_path,
            'line': line_number,
            'timestamp': datetime.now().isoformat()
        }
        
        if category == 'security':
            self.security_issues.append(issue)
        elif category == 'performance':
            self.performance_issues.append(issue)
        elif category == 'accessibility':
            self.accessibility_issues.append(issue)
        elif category == 'code_quality':
            self.code_quality_issues.append(issue)
        elif category == 'seo':
            self.seo_issues.append(issue)
            
        self.issues.append(issue)

    def scan_python_files(self):
        """Scan Python files for security vulnerabilities and code quality"""
        print("\n🐍 Scanning Python Files...")
        
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for file_path in python_files:
            self.scan_python_file(file_path)
            
        print(f"   ✓ Scanned {len(python_files)} Python files")

    def scan_python_file(self, file_path):
        """Scan individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST for security analysis
            try:
                tree = ast.parse(content)
                self.analyze_ast(tree, file_path)
            except SyntaxError as e:
                self.log_issue('code_quality', 'high', f"Syntax error in {file_path}: {e}")
                
            # Check for security patterns
            self.check_security_patterns(content, file_path)
            
            # Check code quality
            self.check_code_quality(content, file_path)
            
        except Exception as e:
            self.log_issue('code_quality', 'medium', f"Error scanning {file_path}: {e}")

    def analyze_ast(self, tree, file_path):
        """Analyze Python AST for security issues"""
        for node in ast.walk(tree):
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['pickle', 'marshal', 'shelve']:
                        self.log_issue('security', 'medium', 
                                     f"Potentially unsafe import: {alias.name}", file_path, node.lineno)
            
            # Check for eval/exec usage
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec', 'compile']:
                    self.log_issue('security', 'high', 
                                 f"Dangerous function call: {node.func.id}", file_path, node.lineno)

    def check_security_patterns(self, content, file_path):
        """Check for security anti-patterns in code"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for hardcoded secrets
            if re.search(r'(password|secret|key|token)\s*=\s*["\'][^"\']{8,}["\']', line, re.IGNORECASE):
                if 'os.environ.get' not in line and 'getenv' not in line:
                    self.log_issue('security', 'critical', 
                                 "Potential hardcoded secret found", file_path, i)
            
            # Check for SQL injection vulnerabilities
            if re.search(r'\.execute\s*\(\s*["\'].*%.*["\']', line):
                self.log_issue('security', 'high', 
                             "Potential SQL injection vulnerability", file_path, i)
            
            # Check for unsafe redirects
            if 'redirect(' in line and 'request.' in line and 'safe_redirect' not in line:
                self.log_issue('security', 'medium', 
                             "Potential open redirect vulnerability", file_path, i)

    def check_code_quality(self, content, file_path):
        """Check Python code quality"""
        lines = content.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.log_issue('code_quality', 'low', 
                             f"Line too long ({len(line)} chars)", file_path, i)
        
        # Check for TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if re.search(r'#.*\b(TODO|FIXME|HACK)\b', line, re.IGNORECASE):
                self.log_issue('code_quality', 'info', 
                             "TODO/FIXME comment found", file_path, i)

    def scan_templates(self):
        """Scan HTML templates for security and accessibility issues"""
        print("\n🌐 Scanning HTML Templates...")
        
        template_files = []
        for root, dirs, files in os.walk('./templates'):
            for file in files:
                if file.endswith('.html'):
                    template_files.append(os.path.join(root, file))
        
        for file_path in template_files:
            self.scan_template_file(file_path)
            
        print(f"   ✓ Scanned {len(template_files)} template files")

    def scan_template_file(self, file_path):
        """Scan individual template file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for missing alt attributes on images
            images = soup.find_all('img')
            for img in images:
                if not img.get('alt'):
                    self.log_issue('accessibility', 'medium', 
                                 "Image missing alt attribute", file_path)
            
            # Check for missing form labels
            inputs = soup.find_all('input', type=['text', 'email', 'password', 'tel'])
            for input_elem in inputs:
                if not input_elem.get('aria-label') and not soup.find('label', {'for': input_elem.get('id')}):
                    self.log_issue('accessibility', 'medium', 
                                 "Form input missing label", file_path)
            
            # Check for inline styles (should use CSS)
            elements_with_style = soup.find_all(style=True)
            if len(elements_with_style) > 10:  # Allow some inline styles for color coding
                self.log_issue('code_quality', 'low', 
                             f"Many inline styles found ({len(elements_with_style)})", file_path)
            
            # Check for missing meta viewport
            if 'base.html' in file_path:
                viewport = soup.find('meta', {'name': 'viewport'})
                if not viewport:
                    self.log_issue('seo', 'high', 
                                 "Missing viewport meta tag", file_path)
                                 
        except Exception as e:
            self.log_issue('code_quality', 'medium', f"Error scanning template {file_path}: {e}")

    def scan_live_website(self):
        """Scan the live website for issues"""
        print(f"\n🌍 Scanning Live Website at {self.base_url}...")
        
        # Test if server is running
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code != 200:
                self.log_issue('performance', 'critical', 
                             f"Server not responding properly (status: {response.status_code})")
                return
        except requests.exceptions.RequestException as e:
            self.log_issue('performance', 'critical', f"Cannot connect to server: {e}")
            return
        
        for page in self.pages:
            self.scan_page(page)
            time.sleep(0.1)  # Be respectful to the server
            
        print(f"   ✓ Scanned {len(self.pages)} pages")

    def scan_page(self, page_path):
        """Scan individual page"""
        try:
            url = urljoin(self.base_url, page_path)
            start_time = time.time()
            response = requests.get(url, timeout=10)
            load_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_issue('performance', 'medium', 
                             f"Page {page_path} returned status {response.status_code}")
                return
            
            # Check page load time
            if load_time > 3.0:
                self.log_issue('performance', 'medium', 
                             f"Slow page load time: {load_time:.2f}s for {page_path}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # SEO checks
            self.check_seo(soup, page_path)
            
            # Accessibility checks
            self.check_accessibility(soup, page_path)
            
            # Performance checks
            self.check_performance(soup, page_path, len(response.content))
            
        except requests.exceptions.RequestException as e:
            self.log_issue('performance', 'medium', f"Error accessing {page_path}: {e}")

    def check_seo(self, soup, page_path):
        """Check SEO optimization"""
        # Check for title tag
        title = soup.find('title')
        if not title or not title.text.strip():
            self.log_issue('seo', 'high', f"Missing or empty title tag on {page_path}")
        elif len(title.text) > 60:
            self.log_issue('seo', 'medium', f"Title tag too long on {page_path}")
            
        # Check for meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if not meta_desc or not meta_desc.get('content'):
            self.log_issue('seo', 'high', f"Missing meta description on {page_path}")
        elif len(meta_desc.get('content', '')) > 160:
            self.log_issue('seo', 'medium', f"Meta description too long on {page_path}")
            
        # Check for h1 tag
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            self.log_issue('seo', 'high', f"Missing H1 tag on {page_path}")
        elif len(h1_tags) > 1:
            self.log_issue('seo', 'medium', f"Multiple H1 tags on {page_path}")

    def check_accessibility(self, soup, page_path):
        """Check accessibility compliance"""
        # Check for skip links
        skip_links = soup.find_all('a', href=re.compile(r'^#'))
        if page_path == '/' and not any('skip' in link.text.lower() for link in skip_links):
            self.log_issue('accessibility', 'medium', f"No skip navigation link found on {page_path}")
            
        # Check for aria-labels on buttons without text
        buttons = soup.find_all('button')
        for button in buttons:
            if not button.text.strip() and not button.get('aria-label'):
                self.log_issue('accessibility', 'medium', f"Button without text or aria-label on {page_path}")

    def check_performance(self, soup, page_path, page_size):
        """Check performance metrics"""
        # Check page size
        if page_size > 1024 * 1024:  # 1MB
            self.log_issue('performance', 'medium', 
                         f"Large page size: {page_size/1024:.1f}KB on {page_path}")
        
        # Check for unoptimized images
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if src and not any(opt in src for opt in ['width=', 'height=', 'fit=']):
                if 'photobucket.com' not in src:  # Photobucket images are optimized
                    self.log_issue('performance', 'low', 
                                 f"Unoptimized image found on {page_path}: {src}")

    def check_dependencies(self):
        """Check for dependency vulnerabilities"""
        print("\n📦 Checking Dependencies...")
        
        # Check if pyproject.toml exists
        if os.path.exists('pyproject.toml'):
            try:
                # Try to run pip-audit if available
                result = subprocess.run(['pip-audit', '--format=json'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    vulnerabilities = json.loads(result.stdout)
                    for vuln in vulnerabilities:
                        self.log_issue('security', 'high', 
                                     f"Dependency vulnerability: {vuln.get('package', 'unknown')}")
                else:
                    print("   ⚠️  pip-audit not available, skipping dependency scan")
            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                print("   ⚠️  Could not run dependency vulnerability scan")
        
        print("   ✓ Dependency check completed")

    def check_file_permissions(self):
        """Check file permissions for security"""
        print("\n🔒 Checking File Permissions...")
        
        sensitive_files = [
            'app.py', 'models.py', 'routes.py', 'admin_auth.py',
            'create_admin.py', 'admin_management.py'
        ]
        
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stats = os.stat(file_path)
                mode = oct(stats.st_mode)[-3:]
                
                # Check if file is world-readable
                if mode[2] in ['4', '5', '6', '7']:
                    self.log_issue('security', 'medium', 
                                 f"File {file_path} is world-readable ({mode})")
                                 
        print("   ✓ File permissions checked")

    def generate_report(self):
        """Generate comprehensive scan report"""
        print("\n📊 Generating Comprehensive Scan Report...")
        
        # Calculate scores
        total_issues = len(self.issues)
        critical_issues = len([i for i in self.issues if i['severity'] == 'critical'])
        high_issues = len([i for i in self.issues if i['severity'] == 'high'])
        medium_issues = len([i for i in self.issues if i['severity'] == 'medium'])
        low_issues = len([i for i in self.issues if i['severity'] == 'low'])
        
        # Calculate overall score (100 - penalty points) with more realistic scoring
        score = 100
        score -= critical_issues * 15  # Critical: -15 each
        score -= high_issues * 8       # High: -8 each  
        score -= medium_issues * 3     # Medium: -3 each
        score -= low_issues * 0.5      # Low: -0.5 each
        score = max(20, score)         # Minimum score of 20
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'comprehensive_scan_report_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Comprehensive Website Scan Report\n\n")
            f.write(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Website:** The Grey Canvas ({self.base_url})\n")
            f.write(f"**Overall Score:** {score}/100\n\n")
            
            f.write(f"## Executive Summary\n\n")
            f.write(f"- **Total Issues Found:** {total_issues}\n")
            f.write(f"- **Critical Issues:** {critical_issues}\n")
            f.write(f"- **High Priority Issues:** {high_issues}\n")
            f.write(f"- **Medium Priority Issues:** {medium_issues}\n")
            f.write(f"- **Low Priority Issues:** {low_issues}\n\n")
            
            # Security Issues
            if self.security_issues:
                f.write(f"## 🔒 Security Issues ({len(self.security_issues)})\n\n")
                for issue in sorted(self.security_issues, key=lambda x: ['info', 'low', 'medium', 'high', 'critical'].index(x['severity']), reverse=True):
                    f.write(f"**{issue['severity'].upper()}:** {issue['message']}")
                    if issue['file']:
                        f.write(f" (`{issue['file']}`")
                        if issue['line']:
                            f.write(f":{issue['line']}")
                        f.write(")")
                    f.write("\n\n")
            
            # Performance Issues  
            if self.performance_issues:
                f.write(f"## ⚡ Performance Issues ({len(self.performance_issues)})\n\n")
                for issue in sorted(self.performance_issues, key=lambda x: ['info', 'low', 'medium', 'high', 'critical'].index(x['severity']), reverse=True):
                    f.write(f"**{issue['severity'].upper()}:** {issue['message']}")
                    if issue['file']:
                        f.write(f" (`{issue['file']}`)")
                    f.write("\n\n")
            
            # Accessibility Issues
            if self.accessibility_issues:
                f.write(f"## ♿ Accessibility Issues ({len(self.accessibility_issues)})\n\n")
                for issue in sorted(self.accessibility_issues, key=lambda x: ['info', 'low', 'medium', 'high', 'critical'].index(x['severity']), reverse=True):
                    f.write(f"**{issue['severity'].upper()}:** {issue['message']}")
                    if issue['file']:
                        f.write(f" (`{issue['file']}`)")
                    f.write("\n\n")
            
            # SEO Issues
            if self.seo_issues:
                f.write(f"## 🔍 SEO Issues ({len(self.seo_issues)})\n\n")
                for issue in sorted(self.seo_issues, key=lambda x: ['info', 'low', 'medium', 'high', 'critical'].index(x['severity']), reverse=True):
                    f.write(f"**{issue['severity'].upper()}:** {issue['message']}")
                    if issue['file']:
                        f.write(f" (`{issue['file']}`)")
                    f.write("\n\n")
            
            # Code Quality Issues
            if self.code_quality_issues:
                f.write(f"## 🔧 Code Quality Issues ({len(self.code_quality_issues)})\n\n")
                for issue in sorted(self.code_quality_issues, key=lambda x: ['info', 'low', 'medium', 'high', 'critical'].index(x['severity']), reverse=True):
                    f.write(f"**{issue['severity'].upper()}:** {issue['message']}")
                    if issue['file']:
                        f.write(f" (`{issue['file']}`")
                        if issue['line']:
                            f.write(f":{issue['line']}")
                        f.write(")")
                    f.write("\n\n")
            
            f.write(f"## Recommendations\n\n")
            
            if critical_issues > 0:
                f.write(f"### 🚨 Critical Priority\n")
                f.write(f"Address all {critical_issues} critical issues immediately before deployment.\n\n")
            
            if high_issues > 0:
                f.write(f"### ⚠️ High Priority\n")
                f.write(f"Resolve {high_issues} high-priority issues to improve security and functionality.\n\n")
            
            if medium_issues > 0:
                f.write(f"### 📋 Medium Priority\n") 
                f.write(f"Consider addressing {medium_issues} medium-priority issues for optimization.\n\n")
            
            f.write(f"### 📈 Overall Assessment\n")
            if score >= 90:
                f.write("**Excellent:** Website is in excellent condition with minimal issues.\n\n")
            elif score >= 80:
                f.write("**Good:** Website is in good condition with some minor issues to address.\n\n")
            elif score >= 70:
                f.write("**Fair:** Website has several issues that should be addressed for optimal performance.\n\n")
            elif score >= 60:
                f.write("**Poor:** Website has significant issues that need immediate attention.\n\n")
            else:
                f.write("**Critical:** Website has critical issues that must be resolved before deployment.\n\n")
                
            f.write(f"---\n")
            f.write(f"*Report generated by The Grey Canvas Comprehensive Scanner*\n")
        
        print(f"   ✅ Report saved to: {report_file}")
        return report_file, score

    def run_comprehensive_scan(self):
        """Run all scan components"""
        start_time = time.time()
        
        # Run all scan components
        self.scan_python_files()
        self.scan_templates()
        self.check_file_permissions()
        self.check_dependencies()
        self.scan_live_website()
        
        # Generate report
        report_file, score = self.generate_report()
        
        scan_time = time.time() - start_time
        
        print(f"\n🎯 Comprehensive Scan Complete!")
        print(f"📊 Overall Score: {score}/100")
        print(f"⏱️  Total Scan Time: {scan_time:.2f} seconds")
        print(f"📄 Full Report: {report_file}")
        print("=" * 80)
        
        return score, report_file

def main():
    """Main scan execution"""
    scanner = ComprehensiveScan()
    score, report = scanner.run_comprehensive_scan()
    
    # Print summary
    print(f"\n🏆 SCAN SUMMARY")
    print(f"Overall Score: {score}/100")
    print(f"Report File: {report}")
    
    if score >= 85:
        print("✅ Website is production-ready!")
    elif score >= 70:
        print("⚠️  Website has minor issues to address")
    else:
        print("🚨 Website needs significant improvements before deployment")

if __name__ == "__main__":
    main()