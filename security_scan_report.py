#!/usr/bin/env python3
"""
Comprehensive Security Code Scan for The Grey Canvas
Analyzes the entire codebase for security vulnerabilities and best practices
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


class SecurityScanner:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []

    def log_issue(
        self, severity, category, file_path, line_num, description, code_snippet=""
    ):
        """Log a security issue"""
        self.issues.append(
            {
                "severity": severity,
                "category": category,
                "file": file_path,
                "line": line_num,
                "description": description,
                "code": code_snippet,
            }
        )

    def log_warning(self, category, file_path, description):
        """Log a security warning"""
        self.warnings.append(
            {"category": category, "file": file_path, "description": description}
        )

    def log_info(self, category, description):
        """Log informational finding"""
        self.info.append({"category": category, "description": description})

    def scan_sensitive_files(self):
        """Scan for files containing sensitive information"""
        print("🔍 Scanning for sensitive files...")

        sensitive_extensions = [".key", ".pem", ".p12", ".pfx", ".jks", ".keystore"]
        sensitive_filenames = [
            "private.key",
            "id_rsa",
            "id_dsa",
            "id_ecdsa",
            "id_ed25519",
            ".env",
            "config.json",
            "secrets.json",
            "credentials.json",
        ]

        for root, dirs, files in os.walk("."):
            # Skip cache and dependency directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", ".cache"]
            ]

            for file in files:
                file_path = os.path.join(root, file)

                # Check file extensions
                if any(file.endswith(ext) for ext in sensitive_extensions):
                    self.log_issue(
                        "HIGH",
                        "Sensitive Files",
                        file_path,
                        0,
                        f"Potential sensitive file found: {file}",
                    )

                # Check filenames
                if file.lower() in [f.lower() for f in sensitive_filenames]:
                    self.log_issue(
                        "HIGH",
                        "Sensitive Files",
                        file_path,
                        0,
                        f"Sensitive filename detected: {file}",
                    )

    def scan_hardcoded_secrets(self):
        """Scan for hardcoded secrets in Python files"""
        print("🔍 Scanning for hardcoded secrets...")

        secret_patterns = [
            (r'password\s*=\s*["\']([^"\']{8,})["\']', "Hardcoded Password"),
            (r'api_key\s*=\s*["\']([^"\']{16,})["\']', "API Key"),
            (r'secret_key\s*=\s*["\']([^"\']{16,})["\']', "Secret Key"),
            (r'token\s*=\s*["\']([^"\']{16,})["\']', "Token"),
            (r'private_key\s*=\s*["\']([^"\']{32,})["\']', "Private Key"),
            (r'["\'][A-Za-z0-9+/]{40,}={0,2}["\']', "Base64 Encoded Secret"),
            (r"[A-Za-z0-9]{32,}", "Potential Token/Hash"),
        ]

        for root, dirs, files in os.walk("."):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", ".cache"]
            ]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        # Skip comments and environment variable usage
                        if line.strip().startswith("#") or "os.environ.get" in line:
                            continue

                        for pattern, description in secret_patterns:
                            matches = re.finditer(pattern, line, re.IGNORECASE)
                            for match in matches:
                                # Skip obvious false positives
                                if any(
                                    keyword in line.lower()
                                    for keyword in [
                                        "example",
                                        "test",
                                        "placeholder",
                                        "your_",
                                        "dev-key",
                                    ]
                                ):
                                    continue

                                self.log_issue(
                                    "HIGH",
                                    "Hardcoded Secrets",
                                    file_path,
                                    line_num,
                                    f"{description} found in code",
                                    line.strip(),
                                )
                except Exception as e:
                    self.log_warning(
                        "File Access", file_path, f"Could not read file: {e}"
                    )

    def scan_sql_injection(self):
        """Scan for potential SQL injection vulnerabilities"""
        print("🔍 Scanning for SQL injection vulnerabilities...")

        sql_patterns = [
            r'cursor\.execute\s*\(\s*["\'][^"\']*%[s|d][^"\']*["\']',
            r'\.execute\s*\(\s*["\'][^"\']*\+[^"\']*["\']',
            r'f["\'][^"\']*SELECT[^"\']*\{[^}]*\}',
            r'["\'][^"\']*SELECT[^"\']*["\']\s*\+',
        ]

        for root, dirs, files in os.walk("."):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", ".cache"]
            ]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        for pattern in sql_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                self.log_issue(
                                    "HIGH",
                                    "SQL Injection",
                                    file_path,
                                    line_num,
                                    "Potential SQL injection vulnerability",
                                    line.strip(),
                                )
                except Exception as e:
                    self.log_warning(
                        "File Access", file_path, f"Could not read file: {e}"
                    )

    def scan_xss_vulnerabilities(self):
        """Scan for XSS vulnerabilities"""
        print("🔍 Scanning for XSS vulnerabilities...")

        xss_patterns = [
            r"render_template_string\s*\(",
            r"\|safe\b",
            r"Markup\s*\(",
            r"innerHTML\s*=",
            r"document\.write\s*\(",
        ]

        for root, dirs, files in os.walk("."):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", ".cache"]
            ]

            for file in files:
                if not (
                    file.endswith(".py")
                    or file.endswith(".html")
                    or file.endswith(".js")
                ):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        for pattern in xss_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                self.log_issue(
                                    "MEDIUM",
                                    "XSS",
                                    file_path,
                                    line_num,
                                    "Potential XSS vulnerability",
                                    line.strip(),
                                )
                except Exception as e:
                    self.log_warning(
                        "File Access", file_path, f"Could not read file: {e}"
                    )

    def scan_authentication_security(self):
        """Scan for authentication and authorization issues"""
        print("🔍 Scanning authentication security...")

        # Check for proper CSRF protection
        try:
            with open("app.py", "r") as f:
                app_content = f.read()
                if "CSRFProtect" not in app_content:
                    self.log_issue(
                        "HIGH",
                        "Authentication",
                        "app.py",
                        0,
                        "CSRF protection not configured",
                    )
                else:
                    self.log_info(
                        "Authentication", "CSRF protection properly configured"
                    )
        except FileNotFoundError:
            pass

        # Check for secure session configuration
        try:
            with open("app.py", "r") as f:
                lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    if "secret_key" in line and "dev-key" in line:
                        self.log_issue(
                            "MEDIUM",
                            "Authentication",
                            "app.py",
                            line_num,
                            "Development secret key detected",
                            line.strip(),
                        )
        except FileNotFoundError:
            pass

    def scan_input_validation(self):
        """Scan for input validation issues"""
        print("🔍 Scanning input validation...")

        validation_keywords = ["escape", "sanitize", "validate", "validators"]

        for root, dirs, files in os.walk("."):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", ".cache"]
            ]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check for form handling
                    if "request.form" in content:
                        has_validation = any(
                            keyword in content for keyword in validation_keywords
                        )
                        if not has_validation:
                            self.log_warning(
                                "Input Validation",
                                file_path,
                                "Form handling without apparent input validation",
                            )
                        else:
                            self.log_info(
                                "Input Validation",
                                f"Input validation found in {file_path}",
                            )

                except Exception as e:
                    self.log_warning(
                        "File Access", file_path, f"Could not read file: {e}"
                    )

    def scan_file_permissions(self):
        """Scan for insecure file permissions"""
        print("🔍 Scanning file permissions...")

        sensitive_files = ["app.py", "models.py", "routes.py", "admin_auth.py"]

        for file in sensitive_files:
            if os.path.exists(file):
                try:
                    stat = os.stat(file)
                    mode = oct(stat.st_mode)[-3:]

                    # Check if world-writable
                    if mode[-1] in ["2", "3", "6", "7"]:
                        self.log_issue(
                            "MEDIUM",
                            "File Permissions",
                            file,
                            0,
                            f"File is world-writable (permissions: {mode})",
                        )

                    # Check if world-readable for sensitive files
                    if mode[-1] in ["4", "5", "6", "7"] and file in [
                        "admin_auth.py",
                        "models.py",
                    ]:
                        self.log_warning(
                            "File Permissions",
                            file,
                            f"Sensitive file is world-readable (permissions: {mode})",
                        )

                except Exception as e:
                    self.log_warning(
                        "File Permissions", file, f"Could not check permissions: {e}"
                    )

    def check_dependencies(self):
        """Check for security issues in dependencies"""
        print("🔍 Checking dependencies...")

        # Check if pyproject.toml exists and scan for known vulnerable packages
        if os.path.exists("pyproject.toml"):
            try:
                with open("pyproject.toml", "r") as f:
                    content = f.read()

                # List of packages with known security issues (example)
                vulnerable_packages = {
                    "jinja2": "< 2.11.3",
                    "flask": "< 2.0.0",
                    "werkzeug": "< 2.0.0",
                    "urllib3": "< 1.26.5",
                }

                for package, version_info in vulnerable_packages.items():
                    if package in content:
                        self.log_warning(
                            "Dependencies",
                            "pyproject.toml",
                            f"Check {package} version against known vulnerabilities ({version_info})",
                        )

            except Exception as e:
                self.log_warning(
                    "Dependencies", "pyproject.toml", f"Could not read file: {e}"
                )

    def generate_report(self):
        """Generate comprehensive security report"""
        print("\n" + "=" * 80)
        print("🔒 COMPREHENSIVE SECURITY SCAN REPORT")
        print("=" * 80)
        print(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Issues Found: {len(self.issues)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Info Items: {len(self.info)}")

        # Critical and High Severity Issues
        critical_issues = [
            i for i in self.issues if i["severity"] in ["CRITICAL", "HIGH"]
        ]
        if critical_issues:
            print(f"\n🚨 CRITICAL/HIGH SEVERITY ISSUES ({len(critical_issues)})")
            print("-" * 50)
            for issue in critical_issues:
                print(f"▶ {issue['severity']} - {issue['category']}")
                print(f"  File: {issue['file']}:{issue['line']}")
                print(f"  Issue: {issue['description']}")
                if issue["code"]:
                    print(f"  Code: {issue['code']}")
                print()

        # Medium Severity Issues
        medium_issues = [i for i in self.issues if i["severity"] == "MEDIUM"]
        if medium_issues:
            print(f"\n⚠️  MEDIUM SEVERITY ISSUES ({len(medium_issues)})")
            print("-" * 50)
            for issue in medium_issues:
                print(f"▶ {issue['category']}")
                print(f"  File: {issue['file']}:{issue['line']}")
                print(f"  Issue: {issue['description']}")
                if issue["code"]:
                    print(f"  Code: {issue['code']}")
                print()

        # Warnings
        if self.warnings:
            print(f"\n💡 WARNINGS ({len(self.warnings)})")
            print("-" * 50)
            for warning in self.warnings:
                print(f"▶ {warning['category']}")
                print(f"  File: {warning['file']}")
                print(f"  Warning: {warning['description']}")
                print()

        # Positive Findings
        if self.info:
            print(f"\n✅ POSITIVE SECURITY FINDINGS ({len(self.info)})")
            print("-" * 50)
            for info in self.info:
                print(f"▶ {info['category']}: {info['description']}")
            print()

        # Summary and Recommendations
        print("\n📋 SECURITY RECOMMENDATIONS")
        print("-" * 50)

        if critical_issues:
            print("🔴 IMMEDIATE ACTION REQUIRED:")
            print("   - Address all CRITICAL and HIGH severity issues immediately")
            print("   - Review and secure any exposed sensitive files")
            print("   - Regenerate any compromised keys or secrets")

        if medium_issues:
            print("🟡 RECOMMENDED ACTIONS:")
            print("   - Review and fix MEDIUM severity issues")
            print("   - Implement additional security controls where needed")

        print("🔵 GENERAL RECOMMENDATIONS:")
        print("   - Regularly update dependencies to latest secure versions")
        print("   - Implement automated security scanning in CI/CD pipeline")
        print("   - Regular security code reviews")
        print("   - Penetration testing for production deployment")

        # Security Score
        total_possible_score = 100
        deductions = (
            len(critical_issues) * 20 + len(medium_issues) * 10 + len(self.warnings) * 2
        )
        security_score = max(0, total_possible_score - deductions)

        print(f"\n🎯 SECURITY SCORE: {security_score}/100")
        if security_score >= 80:
            print("   Status: GOOD - Minimal security issues found")
        elif security_score >= 60:
            print("   Status: FAIR - Some security improvements needed")
        else:
            print("   Status: POOR - Significant security issues require attention")

        print("\n" + "=" * 80)

        return {
            "total_issues": len(self.issues),
            "critical_high": len(critical_issues),
            "medium": len(medium_issues),
            "warnings": len(self.warnings),
            "security_score": security_score,
        }

    def run_full_scan(self):
        """Run complete security scan"""
        print("🚀 Starting Comprehensive Security Scan...")
        print("=" * 60)

        # Run all security checks
        self.scan_sensitive_files()
        self.scan_hardcoded_secrets()
        self.scan_sql_injection()
        self.scan_xss_vulnerabilities()
        self.scan_authentication_security()
        self.scan_input_validation()
        self.scan_file_permissions()
        self.check_dependencies()

        # Generate and return report
        return self.generate_report()


if __name__ == "__main__":
    scanner = SecurityScanner()
    results = scanner.run_full_scan()
