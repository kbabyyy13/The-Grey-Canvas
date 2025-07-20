#!/usr/bin/env python3
"""
Comprehensive SEO & Code Review Audit for The Grey Canvas
Analyzes all pages for SEO optimization, accessibility, performance, and code quality
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import sys
import os

class SEOCodeAudit:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.issues = []
        self.recommendations = []
        self.passed_checks = []
        
    def log_issue(self, severity, category, message):
        """Log SEO and code issues"""
        issue = {
            'severity': severity,
            'category': category,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if severity in ['CRITICAL', 'HIGH']:
            self.issues.append(issue)
        elif severity == 'RECOMMENDATION':
            self.recommendations.append(issue)
        else:
            self.passed_checks.append(issue)
            
    def get_page(self, url):
        """Fetch page content safely"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            self.log_issue('CRITICAL', 'Connectivity', f"Failed to fetch {url}: {e}")
            return None
            
    def check_seo_fundamentals(self, soup, page_name, url):
        """Check core SEO elements"""
        # Title tag analysis
        title = soup.find('title')
        if not title:
            self.log_issue('CRITICAL', 'SEO', f"{page_name}: Missing title tag")
        else:
            title_text = title.get_text().strip()
            if not title_text:
                self.log_issue('CRITICAL', 'SEO', f"{page_name}: Empty title tag")
            elif len(title_text) > 60:
                self.log_issue('HIGH', 'SEO', f"{page_name}: Title too long ({len(title_text)} chars), should be ≤60")
            elif len(title_text) < 30:
                self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: Title quite short ({len(title_text)} chars), consider expanding")
            else:
                self.passed_checks.append({'message': f"{page_name}: Title length optimal ({len(title_text)} chars)"})
        
        # Meta description analysis
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            self.log_issue('CRITICAL', 'SEO', f"{page_name}: Missing meta description")
        else:
            desc_content = meta_desc.get('content', '').strip()
            if not desc_content:
                self.log_issue('CRITICAL', 'SEO', f"{page_name}: Empty meta description")
            elif len(desc_content) > 160:
                self.log_issue('HIGH', 'SEO', f"{page_name}: Meta description too long ({len(desc_content)} chars), should be ≤160")
            elif len(desc_content) < 120:
                self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: Meta description short ({len(desc_content)} chars), consider expanding to 120-160")
            else:
                self.passed_checks.append({'message': f"{page_name}: Meta description length optimal ({len(desc_content)} chars)"})
        
        # H1 tag analysis
        h1_tags = soup.find_all('h1')
        if not h1_tags:
            self.log_issue('CRITICAL', 'SEO', f"{page_name}: Missing H1 tag")
        elif len(h1_tags) > 1:
            self.log_issue('HIGH', 'SEO', f"{page_name}: Multiple H1 tags ({len(h1_tags)}) found, should have exactly one")
        else:
            h1_text = h1_tags[0].get_text().strip()
            if not h1_text:
                self.log_issue('HIGH', 'SEO', f"{page_name}: Empty H1 tag")
            else:
                self.passed_checks.append({'message': f"{page_name}: H1 tag properly implemented"})
        
        # Heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            heading_levels = [int(h.name[1]) for h in headings]
            for i in range(1, len(heading_levels)):
                if heading_levels[i] - heading_levels[i-1] > 1:
                    self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: Heading hierarchy skip detected (H{heading_levels[i-1]} to H{heading_levels[i]})")
                    break
        
        # Canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: Missing canonical URL")
        
        # Lang attribute
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            self.log_issue('HIGH', 'SEO', f"{page_name}: Missing lang attribute on html tag")
        else:
            self.passed_checks.append({'message': f"{page_name}: Lang attribute properly set"})
    
    def check_performance_seo(self, soup, page_name):
        """Check performance-related SEO factors"""
        # Image optimization
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                self.log_issue('HIGH', 'SEO', f"{page_name}: Image missing alt text: {img.get('src', 'unknown')}")
            elif not img.get('alt').strip():
                self.log_issue('HIGH', 'SEO', f"{page_name}: Empty alt text: {img.get('src', 'unknown')}")
        
        # External links
        external_links = soup.find_all('a', href=True)
        for link in external_links:
            href = link.get('href')
            if href and (href.startswith('http://') or href.startswith('https://')) and self.base_url not in href:
                if not link.get('rel') or 'noopener' not in link.get('rel'):
                    self.log_issue('RECOMMENDATION', 'Security', f"{page_name}: External link missing rel='noopener': {href}")
        
        # Scripts and loading
        scripts = soup.find_all('script', src=True)
        blocking_scripts = [s for s in scripts if not s.get('async') and not s.get('defer')]
        if len(blocking_scripts) > 3:
            self.log_issue('RECOMMENDATION', 'Performance', f"{page_name}: {len(blocking_scripts)} blocking scripts, consider async/defer")
        
        # CSS optimization
        css_links = soup.find_all('link', rel='stylesheet')
        if len(css_links) > 5:
            self.log_issue('RECOMMENDATION', 'Performance', f"{page_name}: {len(css_links)} CSS files, consider combining")
    
    def check_structured_data(self, soup, page_name):
        """Check for structured data implementation"""
        # JSON-LD structured data
        json_ld = soup.find_all('script', type='application/ld+json')
        if not json_ld:
            self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: No structured data (JSON-LD) found")
        
        # Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        if not og_tags:
            self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: No Open Graph tags found")
        
        # Twitter Card tags
        twitter_tags = soup.find_all('meta', name=lambda x: x and x.startswith('twitter:'))
        if not twitter_tags:
            self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: No Twitter Card tags found")
    
    def check_accessibility_seo(self, soup, page_name):
        """Check accessibility factors that impact SEO"""
        # Form labels
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_elem in inputs:
                if input_elem.get('type') not in ['hidden', 'submit', 'button']:
                    input_id = input_elem.get('id')
                    if input_id:
                        label = soup.find('label', attrs={'for': input_id})
                        if not label:
                            self.log_issue('RECOMMENDATION', 'Accessibility', f"{page_name}: Input missing associated label: {input_id}")
        
        # Skip links
        skip_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
        if not skip_links:
            self.log_issue('RECOMMENDATION', 'Accessibility', f"{page_name}: No skip navigation links found")
    
    def check_content_quality(self, soup, page_name):
        """Analyze content quality for SEO"""
        # Text content analysis
        text_content = soup.get_text()
        word_count = len(text_content.split())
        
        if word_count < 300:
            self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: Low word count ({word_count}), consider adding more content")
        elif word_count > 2000:
            self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: High word count ({word_count}), ensure content is well-structured")
        
        # Internal linking
        internal_links = soup.find_all('a', href=True)
        internal_count = sum(1 for link in internal_links if link.get('href').startswith('/') or self.base_url in link.get('href', ''))
        
        if internal_count < 3:
            self.log_issue('RECOMMENDATION', 'SEO', f"{page_name}: Few internal links ({internal_count}), consider adding more")
    
    def audit_page(self, path, page_name):
        """Comprehensive audit of a single page"""
        url = f"{self.base_url}{path}"
        print(f"\n🔍 Auditing {page_name} ({url})")
        
        soup = self.get_page(url)
        if not soup:
            return
        
        # Run all checks
        self.check_seo_fundamentals(soup, page_name, url)
        self.check_performance_seo(soup, page_name)
        self.check_structured_data(soup, page_name)
        self.check_accessibility_seo(soup, page_name)
        self.check_content_quality(soup, page_name)
        
        print(f"✅ {page_name} audit completed")
    
    def run_full_audit(self):
        """Run comprehensive audit on all pages"""
        print("🚀 COMPREHENSIVE SEO & CODE REVIEW AUDIT")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define all pages to audit
        pages_to_audit = [
            ('/', 'Homepage'),
            ('/about', 'About'),
            ('/owner', 'Owner'),
            ('/company', 'Company'),
            ('/services', 'Services'),
            ('/packages', 'Packages'),
            ('/plans', 'Plans'),
            ('/overview', 'Overview'),
            ('/portfolio', 'Portfolio'),
            ('/contact', 'Contact'),
            ('/schedule', 'Schedule'),
            ('/intake', 'Intake'),
            ('/thegrey', 'The Grey'),
            ('/blog', 'Blog'),
            ('/privacy-policy', 'Privacy Policy'),
            ('/terms-of-service', 'Terms of Service'),
        ]
        
        for path, name in pages_to_audit:
            try:
                self.audit_page(path, name)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                self.log_issue('CRITICAL', 'System', f"Error auditing {name}: {e}")
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 60)
        print("📊 AUDIT RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"\n✅ PASSED CHECKS: {len(self.passed_checks)}")
        print(f"⚠️  RECOMMENDATIONS: {len(self.recommendations)}")
        print(f"🚨 ISSUES FOUND: {len(self.issues)}")
        
        if self.issues:
            print("\n🚨 CRITICAL & HIGH PRIORITY ISSUES:")
            print("-" * 40)
            for issue in self.issues:
                print(f"[{issue['severity']}] {issue['category']}: {issue['message']}")
        
        if self.recommendations:
            print("\n⚠️  RECOMMENDATIONS:")
            print("-" * 40)
            for rec in self.recommendations[:10]:  # Show top 10
                print(f"[{rec['category']}] {rec['message']}")
            if len(self.recommendations) > 10:
                print(f"... and {len(self.recommendations) - 10} more recommendations")
        
        # Generate detailed report file
        self.write_detailed_report()
        
        print(f"\n📁 Detailed report saved to: seo_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        print("\n🎯 AUDIT COMPLETE")
    
    def write_detailed_report(self):
        """Write detailed audit report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"seo_audit_report_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write("# SEO & Code Review Audit Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Target:** {self.base_url}\n")
            f.write(f"**Audit Type:** Comprehensive SEO & Code Review\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write(f"- ✅ **Passed Checks:** {len(self.passed_checks)}\n")
            f.write(f"- ⚠️  **Recommendations:** {len(self.recommendations)}\n")
            f.write(f"- 🚨 **Issues Found:** {len(self.issues)}\n\n")
            
            if self.issues:
                f.write("## Critical & High Priority Issues\n\n")
                for issue in self.issues:
                    f.write(f"### [{issue['severity']}] {issue['category']}\n")
                    f.write(f"**Issue:** {issue['message']}\n\n")
            
            if self.recommendations:
                f.write("## Recommendations\n\n")
                for rec in self.recommendations:
                    f.write(f"### [{rec['category']}] {rec['message']}\n\n")
            
            f.write("## Passed Checks\n\n")
            for check in self.passed_checks:
                f.write(f"- ✅ {check['message']}\n")

if __name__ == "__main__":
    audit = SEOCodeAudit()
    audit.run_full_audit()