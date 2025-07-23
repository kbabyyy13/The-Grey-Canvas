#!/usr/bin/env python3
"""
Legal Document Compliance Audit for The Grey Canvas
Comprehensive code review and compliance testing for Privacy Policy and Terms of Service
"""

import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class LegalComplianceAudit:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.issues = []
        self.warnings = []
        self.recommendations = []

    def log_issue(self, severity, category, message):
        """Log compliance issues with severity levels"""
        entry = {
            "severity": severity,
            "category": category,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        if severity == "CRITICAL":
            self.issues.append(entry)
        elif severity == "WARNING":
            self.warnings.append(entry)
        elif severity == "RECOMMENDATION":
            self.recommendations.append(entry)

    def get_page_content(self, url):
        """Fetch page content and return BeautifulSoup object"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            self.log_issue(
                "CRITICAL", "Accessibility", f"Failed to fetch {url}: {str(e)}"
            )
            return None

    def check_html_structure(self, soup, page_name):
        """Check HTML structure and semantic markup"""
        if not soup:
            return

        # Check for proper heading hierarchy
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        if not headings:
            self.log_issue("CRITICAL", "Structure", f"{page_name}: No headings found")
            return

        h1_count = len(soup.find_all("h1"))
        if h1_count != 1:
            self.log_issue(
                "WARNING",
                "SEO",
                f"{page_name}: Found {h1_count} H1 tags, should be exactly 1",
            )

        # Check heading sequence
        prev_level = 0
        for heading in headings:
            current_level = int(heading.name[1])
            if current_level > prev_level + 1:
                self.log_issue(
                    "WARNING",
                    "Accessibility",
                    f"{page_name}: Heading level jump from H{prev_level} to H{current_level}",
                )
            prev_level = current_level

    def check_legal_content_completeness(self, soup, page_type):
        """Check for required legal content sections"""
        text_content = soup.get_text().lower()

        if page_type == "privacy":
            required_sections = [
                ("data collection", "information.*collect"),
                ("data usage", "how.*use.*information"),
                ("data sharing", "shar.*information"),
                ("user rights", "your.*rights"),
                ("data security", "security"),
                ("contact information", "contact.*email"),
                ("effective date", "effective.*date"),
                ("policy updates", "chang.*policy"),
            ]
        else:  # terms of service
            required_sections = [
                ("content usage", "use.*content"),
                ("user conduct", "user.*conduct|conduct"),
                ("liability", "liability"),
                ("disclaimer", "disclaimer"),
                ("effective date", "effective.*date"),
                ("terms updates", "chang.*terms"),
            ]

        for section_name, pattern in required_sections:
            if not re.search(pattern, text_content):
                self.log_issue(
                    "WARNING",
                    "Completeness",
                    f"{page_type.title()}: Missing or unclear {section_name} section",
                )

    def check_accessibility_compliance(self, soup, page_name):
        """Check accessibility compliance"""
        # Check for alt text on images
        images = soup.find_all("img")
        for img in images:
            if not img.get("alt"):
                self.log_issue(
                    "CRITICAL",
                    "Accessibility",
                    f"{page_name}: Image missing alt text: {img.get('src', 'unknown')}",
                )

        # Check for proper link text
        links = soup.find_all("a")
        for link in links:
            link_text = link.get_text().strip()
            if not link_text or link_text.lower() in [
                "click here",
                "here",
                "read more",
            ]:
                self.log_issue(
                    "WARNING",
                    "Accessibility",
                    f"{page_name}: Non-descriptive link text: '{link_text}'",
                )

        # Check for lang attribute
        html_tag = soup.find("html")
        if not html_tag or not html_tag.get("lang"):
            self.log_issue(
                "WARNING",
                "Accessibility",
                f"{page_name}: Missing lang attribute on html tag",
            )

    def check_legal_language_quality(self, soup, page_type):
        """Check legal language for clarity and completeness"""
        text_content = soup.get_text()

        # Check for vague language
        vague_terms = ["reasonable", "appropriate", "sufficient", "adequate", "may"]
        vague_count = sum(text_content.lower().count(term) for term in vague_terms)

        if vague_count > 10:
            self.log_issue(
                "RECOMMENDATION",
                "Legal Quality",
                f"{page_type.title()}: High use of vague terms "
                f"({vague_count} instances). Consider more specific language.",
            )

        # Check for contact information
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        if not re.search(email_pattern, text_content):
            self.log_issue(
                "WARNING",
                "Legal Quality",
                f"{page_type.title()}: No contact email found for legal inquiries",
            )

    def check_gdpr_compliance(self, soup, page_type):
        """Check GDPR compliance indicators"""
        if page_type != "privacy":
            return

        text_content = soup.get_text().lower()

        gdpr_requirements = [
            ("lawful basis", "lawful.*basis|legal.*basis"),
            ("data retention", "retention|how long"),
            ("data portability", "portability|transfer.*data"),
            ("right to deletion", "delet.*data|right.*erasure|forget"),
            ("data processing", "process.*data"),
            ("consent", "consent"),
        ]

        for requirement, pattern in gdpr_requirements:
            if not re.search(pattern, text_content):
                self.log_issue(
                    "RECOMMENDATION",
                    "GDPR",
                    f"Privacy Policy: Consider adding {requirement} information for GDPR compliance",
                )

    def check_css_and_styling(self, soup, page_name):
        """Check CSS and styling quality"""
        # Check for inline styles (should be minimal)
        inline_styles = soup.find_all(attrs={"style": True})
        if len(inline_styles) > 5:
            self.log_issue(
                "RECOMMENDATION",
                "Code Quality",
                f"{page_name}: High use of inline styles ({len(inline_styles)}). Consider CSS classes.",
            )

        # Check for responsive design indicators
        meta_viewport = soup.find("meta", attrs={"name": "viewport"})
        if not meta_viewport:
            self.log_issue(
                "WARNING",
                "Responsive Design",
                f"{page_name}: Missing viewport meta tag",
            )

    def check_seo_optimization(self, soup, page_name):
        """Check SEO optimization"""
        # Check meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if not meta_desc:
            self.log_issue("WARNING", "SEO", f"{page_name}: Missing meta description")
        elif meta_desc.get("content"):
            desc_length = len(meta_desc.get("content"))
            if desc_length < 120 or desc_length > 160:
                self.log_issue(
                    "RECOMMENDATION",
                    "SEO",
                    f"{page_name}: Meta description length ({desc_length}) not optimal (120-160 chars)",
                )

        # Check title tag
        title = soup.find("title")
        if not title:
            self.log_issue("CRITICAL", "SEO", f"{page_name}: Missing title tag")
        elif title.get_text():
            title_length = len(title.get_text())
            if title_length > 60:
                self.log_issue(
                    "RECOMMENDATION",
                    "SEO",
                    f"{page_name}: Title too long ({title_length} chars), should be under 60",
                )

    def check_performance_indicators(self, soup, page_name):
        """Check performance optimization indicators"""
        # Check for external stylesheets
        external_css = soup.find_all("link", attrs={"rel": "stylesheet"})
        if len(external_css) > 3:
            self.log_issue(
                "RECOMMENDATION",
                "Performance",
                f"{page_name}: Many external CSS files ({len(external_css)}). Consider bundling.",
            )

        # Check for external scripts
        external_scripts = soup.find_all("script", attrs={"src": True})
        blocking_scripts = [
            s for s in external_scripts if not s.get("async") and not s.get("defer")
        ]
        if len(blocking_scripts) > 2:
            self.log_issue(
                "RECOMMENDATION",
                "Performance",
                f"{page_name}: {len(blocking_scripts)} blocking scripts. Consider async/defer.",
            )

    def audit_page(self, path, page_name, page_type=None):
        """Audit a single page"""
        url = f"{self.base_url}{path}"
        print(f"\n🔍 Auditing {page_name} ({url})")

        soup = self.get_page_content(url)
        if not soup:
            return

        # Run all checks
        self.check_html_structure(soup, page_name)
        self.check_accessibility_compliance(soup, page_name)
        self.check_css_and_styling(soup, page_name)
        self.check_seo_optimization(soup, page_name)
        self.check_performance_indicators(soup, page_name)

        # Legal-specific checks
        if page_type:
            self.check_legal_content_completeness(soup, page_type)
            self.check_legal_language_quality(soup, page_type)
            if page_type == "privacy":
                self.check_gdpr_compliance(soup, page_type)

    def run_audit(self):
        """Run complete legal document audit"""
        print("🏛️  LEGAL DOCUMENT COMPLIANCE AUDIT")
        print("=" * 50)
        print(f"Target: {self.base_url}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Audit legal pages
        pages_to_audit = [
            ("/privacy-policy", "Privacy Policy", "privacy"),
            ("/terms-of-service", "Terms of Service", "terms"),
        ]

        for path, name, page_type in pages_to_audit:
            self.audit_page(path, name, page_type)

        self.generate_report()

    def generate_report(self):
        """Generate final audit report"""
        print("\n" + "=" * 50)
        print("📋 LEGAL COMPLIANCE AUDIT REPORT")
        print("=" * 50)

        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"Critical Issues: {len(self.issues)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Recommendations: {len(self.recommendations)}")

        # Critical Issues
        if self.issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  ❌ [{issue['category']}] {issue['message']}")

        # Warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠️  [{warning['category']}] {warning['message']}")

        # Recommendations
        if self.recommendations:
            print(f"\n💡 RECOMMENDATIONS ({len(self.recommendations)}):")
            for rec in self.recommendations:
                print(f"  💡 [{rec['category']}] {rec['message']}")

        # Compliance Score
        total_items = len(self.issues) + len(self.warnings) + len(self.recommendations)
        if total_items == 0:
            score = 100
        else:
            # Weight critical issues more heavily
            weighted_score = max(
                0,
                100
                - (len(self.issues) * 10)
                - (len(self.warnings) * 5)
                - (len(self.recommendations) * 2),
            )
            score = weighted_score

        print(f"\n🎯 COMPLIANCE SCORE: {score}/100")

        if score >= 90:
            print("✅ Excellent compliance level!")
        elif score >= 75:
            print("✅ Good compliance level with minor improvements needed.")
        elif score >= 60:
            print("⚠️  Moderate compliance level. Several improvements recommended.")
        else:
            print("❌ Poor compliance level. Immediate action required.")

        print("\n" + "=" * 50)
        print("Audit completed successfully!")


if __name__ == "__main__":
    audit = LegalComplianceAudit()
    audit.run_audit()
