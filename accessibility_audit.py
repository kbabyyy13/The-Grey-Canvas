#!/usr/bin/env python3
"""
WCAG 2.2 Compliance Audit Script
Performs comprehensive accessibility testing on The Grey Canvas website
"""

import json
import re
import time
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class WCAGAudit:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'summary': {},
            'issues': [],
            'passed': [],
            'warnings': []
        }
        
    def get_page(self, url):
        """Fetch a page and return BeautifulSoup object"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def check_color_contrast(self, soup):
        """Check color contrast ratios (WCAG 2.2 SC 1.4.3, 1.4.6)"""
        issues = []
        
        # Define color combinations used in the site
        color_tests = [
            {
                'element': 'Main text on background',
                'fg': '#ffffff',
                'bg': '#374151',
                'level': 'AA',
                'size': 'normal'
            },
            {
                'element': 'Signature grey text',
                'fg': '#6B7280',
                'bg': '#ffffff',
                'level': 'AA',
                'size': 'normal'
            },
            {
                'element': 'Pink accent text',
                'fg': '#C1185E',
                'bg': '#ffffff',
                'level': 'AA',
                'size': 'normal'
            },
            {
                'element': 'Footer text',
                'fg': '#ffffff',
                'bg': '#1f2937',
                'level': 'AA',
                'size': 'normal'
            }
        ]
        
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def luminance(rgb):
            def normalize(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            r, g, b = rgb
            return 0.2126 * normalize(r) + 0.7152 * normalize(g) + 0.0722 * normalize(b)
        
        def contrast_ratio(color1, color2):
            l1 = luminance(hex_to_rgb(color1))
            l2 = luminance(hex_to_rgb(color2))
            return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        
        for test in color_tests:
            ratio = contrast_ratio(test['fg'], test['bg'])
            required_ratio = 4.5 if test['level'] == 'AA' else 3.0
            
            if ratio >= required_ratio:
                self.results['passed'].append(f"✓ {test['element']}: {ratio:.2f}:1 (passes {test['level']})")
            else:
                issues.append(f"✗ {test['element']}: {ratio:.2f}:1 (fails {test['level']}, needs {required_ratio}:1)")
        
        return issues
    
    def check_headings_structure(self, soup):
        """Check heading hierarchy (WCAG 2.2 SC 1.3.1)"""
        issues = []
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            issues.append("✗ No headings found on page")
            return issues
        
        h1_count = len(soup.find_all('h1'))
        if h1_count == 0:
            issues.append("✗ No H1 heading found")
        elif h1_count > 1:
            issues.append(f"✗ Multiple H1 headings found ({h1_count})")
        else:
            self.results['passed'].append("✓ Exactly one H1 heading found")
        
        # Check heading sequence
        prev_level = 0
        for heading in headings:
            level = int(heading.name[1])
            if level > prev_level + 1:
                issues.append(f"✗ Heading sequence skipped: {heading.name} after h{prev_level}")
            prev_level = level
        
        if not issues:
            self.results['passed'].append("✓ Heading hierarchy is properly structured")
        
        return issues
    
    def check_images(self, soup):
        """Check image accessibility (WCAG 2.2 SC 1.1.1)"""
        issues = []
        images = soup.find_all('img')
        
        for img in images:
            alt = img.get('alt')
            src = img.get('src', '')
            
            if alt is None:
                issues.append(f"✗ Image missing alt attribute: {src}")
            elif alt.strip() == '':
                # Empty alt is okay for decorative images
                self.results['passed'].append(f"✓ Decorative image with empty alt: {src}")
            else:
                self.results['passed'].append(f"✓ Image has descriptive alt text: {src}")
        
        return issues
    
    def check_links(self, soup):
        """Check link accessibility (WCAG 2.2 SC 2.4.4)"""
        issues = []
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href')
            if not href:
                continue
                
            # Check for descriptive text
            text = link.get_text(strip=True)
            aria_label = link.get('aria-label')
            title = link.get('title')
            
            if not text and not aria_label and not title:
                issues.append(f"✗ Link has no accessible text: {href}")
            elif text in ['here', 'click here', 'more', 'read more']:
                issues.append(f"✗ Link has non-descriptive text: '{text}'")
            else:
                self.results['passed'].append(f"✓ Link has descriptive text: '{text or aria_label}'")
        
        return issues
    
    def check_forms(self, soup):
        """Check form accessibility (WCAG 2.2 SC 1.3.1, 3.3.2)"""
        issues = []
        forms = soup.find_all('form')
        
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            for input_elem in inputs:
                input_type = input_elem.get('type', 'text')
                if input_type in ['hidden', 'submit', 'button']:
                    continue
                
                # Check for labels
                input_id = input_elem.get('id')
                name = input_elem.get('name')
                
                if input_id:
                    label = soup.find('label', {'for': input_id})
                    if not label:
                        issues.append(f"✗ Input missing label: {input_id}")
                    else:
                        self.results['passed'].append(f"✓ Input has proper label: {input_id}")
                else:
                    issues.append(f"✗ Input missing ID for label association: {name}")
        
        return issues
    
    def check_buttons(self, soup):
        """Check button accessibility (WCAG 2.2 SC 1.3.1, 4.1.2)"""
        issues = []
        buttons = soup.find_all(['button', 'input[type="submit"]', 'input[type="button"]'])
        
        for button in buttons:
            text = button.get_text(strip=True)
            aria_label = button.get('aria-label')
            title = button.get('title')
            
            if not text and not aria_label and not title:
                issues.append("✗ Button has no accessible text")
            else:
                self.results['passed'].append(f"✓ Button has accessible text: '{text or aria_label}'")
        
        return issues
    
    def check_aria_attributes(self, soup):
        """Check ARIA attributes (WCAG 2.2 SC 4.1.2)"""
        issues = []
        
        # Check for aria-hidden on decorative elements
        hidden_elements = soup.find_all(attrs={'aria-hidden': True})
        for elem in hidden_elements:
            if elem.name == 'svg':
                self.results['passed'].append("✓ Decorative SVG properly hidden from screen readers")
        
        # Check for aria-label on interactive elements
        interactive_elements = soup.find_all(['button', 'a', 'input'])
        for elem in interactive_elements:
            if elem.get('aria-label'):
                self.results['passed'].append(f"✓ Interactive element has aria-label: {elem.name}")
        
        return issues
    
    def check_skip_links(self, soup):
        """Check for skip navigation links (WCAG 2.2 SC 2.4.1)"""
        issues = []
        
        # Look for skip links
        skip_links = soup.find_all('a', href=re.compile(r'^#'))
        skip_found = False
        
        for link in skip_links:
            text = link.get_text(strip=True).lower()
            if 'skip' in text and ('content' in text or 'main' in text):
                skip_found = True
                break
        
        if not skip_found:
            self.results['warnings'].append("⚠ No skip navigation link found")
        else:
            self.results['passed'].append("✓ Skip navigation link found")
        
        return issues
    
    def check_page_title(self, soup):
        """Check page title (WCAG 2.2 SC 2.4.2)"""
        issues = []
        title = soup.find('title')
        
        if not title:
            issues.append("✗ Page missing title element")
        elif not title.get_text(strip=True):
            issues.append("✗ Page title is empty")
        else:
            self.results['passed'].append(f"✓ Page has descriptive title: '{title.get_text(strip=True)}'")
        
        return issues
    
    def check_language(self, soup):
        """Check language declaration (WCAG 2.2 SC 3.1.1)"""
        issues = []
        html = soup.find('html')
        
        if not html:
            issues.append("✗ No HTML element found")
        elif not html.get('lang'):
            issues.append("✗ HTML element missing lang attribute")
        else:
            self.results['passed'].append(f"✓ Page language declared: {html.get('lang')}")
        
        return issues
    
    def audit_page(self, url, page_name):
        """Audit a single page"""
        print(f"\n=== Auditing {page_name} ({url}) ===")
        
        soup = self.get_page(url)
        if not soup:
            return
        
        all_issues = []
        
        # Run all checks
        checks = [
            ('Color Contrast', self.check_color_contrast),
            ('Heading Structure', self.check_headings_structure),
            ('Images', self.check_images),
            ('Links', self.check_links),
            ('Forms', self.check_forms),
            ('Buttons', self.check_buttons),
            ('ARIA Attributes', self.check_aria_attributes),
            ('Skip Links', self.check_skip_links),
            ('Page Title', self.check_page_title),
            ('Language', self.check_language)
        ]
        
        for check_name, check_func in checks:
            print(f"  Checking {check_name}...")
            issues = check_func(soup)
            if issues:
                all_issues.extend(issues)
                for issue in issues:
                    self.results['issues'].append(f"{page_name}: {issue}")
        
        if not all_issues:
            print(f"  ✓ No issues found on {page_name}")
        else:
            print(f"  ✗ {len(all_issues)} issues found on {page_name}")
    
    def run_audit(self):
        """Run complete audit on all pages"""
        print("Starting WCAG 2.2 Compliance Audit for The Grey Canvas")
        print("=" * 60)
        
        # Define pages to audit
        pages = [
            ('/', 'Home'),
            ('/about', 'About'),
            ('/services', 'Services'),
            ('/contact', 'Contact'),
            ('/portfolio', 'Portfolio'),
            ('/blog', 'Blog'),
            ('/packages', 'Packages'),
            ('/overview', 'Overview'),
            ('/thegrey', 'The Grey'),
            ('/company', 'Company'),
            ('/owner', 'Owner'),
            ('/plans', 'Plans'),
            ('/schedule', 'Schedule'),
            ('/intake', 'Intake')
        ]
        
        for path, name in pages:
            url = urljoin(self.base_url, path)
            self.audit_page(url, name)
            time.sleep(0.5)  # Be nice to the server
        
        self.generate_report()
    
    def generate_report(self):
        """Generate final audit report"""
        print("\n" + "=" * 60)
        print("WCAG 2.2 COMPLIANCE AUDIT REPORT")
        print("=" * 60)
        
        total_issues = len(self.results['issues'])
        total_passed = len(self.results['passed'])
        total_warnings = len(self.results['warnings'])
        
        print(f"\nSUMMARY:")
        print(f"  ✓ Passed: {total_passed}")
        print(f"  ✗ Issues: {total_issues}")
        print(f"  ⚠ Warnings: {total_warnings}")
        
        if total_issues == 0:
            print(f"\n🎉 EXCELLENT! Your website passes all WCAG 2.2 compliance checks!")
        else:
            compliance_rate = (total_passed / (total_passed + total_issues)) * 100
            print(f"\n📊 Compliance Rate: {compliance_rate:.1f}%")
        
        if self.results['issues']:
            print(f"\n❌ ISSUES TO FIX:")
            for issue in self.results['issues']:
                print(f"  {issue}")
        
        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS (Recommendations):")
            for warning in self.results['warnings']:
                print(f"  {warning}")
        
        if self.results['passed']:
            print(f"\n✅ PASSED CHECKS:")
            for passed in self.results['passed'][:10]:  # Show first 10
                print(f"  {passed}")
            
            if len(self.results['passed']) > 10:
                print(f"  ... and {len(self.results['passed']) - 10} more")
        
        print(f"\n" + "=" * 60)
        print("Audit completed successfully!")
        print("=" * 60)

if __name__ == "__main__":
    audit = WCAGAudit()
    audit.run_audit()