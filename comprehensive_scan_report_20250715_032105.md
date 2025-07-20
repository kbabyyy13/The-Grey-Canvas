# Comprehensive Website Scan Report

**Scan Date:** 2025-07-15 03:21:05
**Website:** The Grey Canvas (http://localhost:5000)
**Overall Score:** 0/100

## Executive Summary

- **Total Issues Found:** 87
- **Critical Issues:** 0
- **High Priority Issues:** 0
- **Medium Priority Issues:** 11
- **Low Priority Issues:** 74

## 🔒 Security Issues (4)

**MEDIUM:** File app.py is world-readable (644)

**MEDIUM:** File routes.py is world-readable (644)

**MEDIUM:** File create_admin.py is world-readable (644)

**MEDIUM:** File admin_management.py is world-readable (644)

## ⚡ Performance Issues (33)

**MEDIUM:** Slow page load time: 3.10s for /blog

**MEDIUM:** Page /policy returned status 404

**MEDIUM:** Page /terms returned status 404

**LOW:** Unoptimized image found on /: /static/logo.png

**LOW:** Unoptimized image found on /: /static/tgctag.png

**LOW:** Unoptimized image found on /: /static/logo.png

**LOW:** Unoptimized image found on /about: /static/logo.png

**LOW:** Unoptimized image found on /about: /static/logo.png

**LOW:** Unoptimized image found on /services: /static/logo.png

**LOW:** Unoptimized image found on /services: /static/logo.png

**LOW:** Unoptimized image found on /packages: /static/logo.png

**LOW:** Unoptimized image found on /packages: /static/logo.png

**LOW:** Unoptimized image found on /plans: /static/logo.png

**LOW:** Unoptimized image found on /plans: /static/logo.png

**LOW:** Unoptimized image found on /overview: /static/logo.png

**LOW:** Unoptimized image found on /overview: /static/logo.png

**LOW:** Unoptimized image found on /contact: /static/logo.png

**LOW:** Unoptimized image found on /contact: /static/logo.png

**LOW:** Unoptimized image found on /intake: /static/logo.png

**LOW:** Unoptimized image found on /intake: /static/logo.png

**LOW:** Unoptimized image found on /blog: /static/logo.png

**LOW:** Unoptimized image found on /blog: /static/blog-two-featured.jpg

**LOW:** Unoptimized image found on /blog: /static/blog-one-featured.jpg

**LOW:** Unoptimized image found on /blog: /static/logo.png

**LOW:** Unoptimized image found on /company: /static/logo.png

**LOW:** Unoptimized image found on /company: /static/designer.png

**LOW:** Unoptimized image found on /company: /static/logo.png

**LOW:** Unoptimized image found on /owner: /static/logo.png

**LOW:** Unoptimized image found on /owner: /static/logo.png

**LOW:** Unoptimized image found on /thegrey: /static/logo.png

**LOW:** Unoptimized image found on /thegrey: /static/logo.png

**LOW:** Unoptimized image found on /portfolio: /static/logo.png

**LOW:** Unoptimized image found on /portfolio: /static/logo.png

## ♿ Accessibility Issues (3)

**MEDIUM:** Form input missing label (`./templates/admin_dashboard.html`)

**MEDIUM:** Form input missing label (`./templates/blog.html`)

**MEDIUM:** No skip navigation link found on /

## 🔍 SEO Issues (1)

**MEDIUM:** Meta description too long on /

## 🔧 Code Quality Issues (46)

**LOW:** Line too long (133 chars) (`./legal_compliance_audit.py`:132)

**LOW:** Line too long (127 chars) (`./legal_compliance_audit.py`:288)

**LOW:** Line too long (136 chars) (`./models.py`:180)

**LOW:** Line too long (121 chars) (`./models.py`:249)

**LOW:** Line too long (136 chars) (`./seo_code_audit.py`:60)

**LOW:** Line too long (132 chars) (`./seo_code_audit.py`:73)

**LOW:** Line too long (154 chars) (`./seo_code_audit.py`:75)

**LOW:** Line too long (131 chars) (`./seo_code_audit.py`:77)

**LOW:** Line too long (123 chars) (`./seo_code_audit.py`:84)

**LOW:** Line too long (157 chars) (`./seo_code_audit.py`:98)

**LOW:** Line too long (126 chars) (`./seo_code_audit.py`:129)

**LOW:** Line too long (139 chars) (`./seo_code_audit.py`:135)

**LOW:** Line too long (123 chars) (`./seo_code_audit.py`:140)

**LOW:** Line too long (137 chars) (`./seo_code_audit.py`:171)

**LOW:** Line too long (128 chars) (`./seo_code_audit.py`:185)

**LOW:** Line too long (134 chars) (`./seo_code_audit.py`:187)

**LOW:** Line too long (135 chars) (`./seo_code_audit.py`:191)

**LOW:** Line too long (128 chars) (`./seo_code_audit.py`:194)

**LOW:** Line too long (123 chars) (`./routes.py`:155)

**LOW:** Line too long (122 chars) (`./routes.py`:185)

**LOW:** Line too long (257 chars) (`./routes.py`:645)

**LOW:** Line too long (220 chars) (`./routes.py`:648)

**LOW:** Line too long (122 chars) (`./routes.py`:652)

**LOW:** Line too long (125 chars) (`./routes.py`:663)

**LOW:** Line too long (229 chars) (`./routes.py`:676)

**LOW:** Line too long (201 chars) (`./routes.py`:678)

**LOW:** Line too long (235 chars) (`./routes.py`:679)

**LOW:** Line too long (196 chars) (`./routes.py`:681)

**LOW:** Line too long (133 chars) (`./routes.py`:937)

**LOW:** Line too long (154 chars) (`./comprehensive_scan.py`:409)

**LOW:** Line too long (157 chars) (`./comprehensive_scan.py`:421)

**LOW:** Line too long (159 chars) (`./comprehensive_scan.py`:430)

**LOW:** Line too long (149 chars) (`./comprehensive_scan.py`:439)

**LOW:** Line too long (158 chars) (`./comprehensive_scan.py`:448)

**LOW:** Many inline styles found (27) (`./templates/contact.html`)

**LOW:** Many inline styles found (53) (`./templates/overview.html`)

**LOW:** Many inline styles found (12) (`./templates/packages.html`)

**LOW:** Many inline styles found (17) (`./templates/blog.html`)

**LOW:** Many inline styles found (16) (`./templates/thegrey.html`)

**LOW:** Many inline styles found (16) (`./templates/portfolio.html`)

**LOW:** Many inline styles found (32) (`./templates/plans.html`)

**LOW:** Many inline styles found (11) (`./templates/services.html`)

**LOW:** Many inline styles found (18) (`./templates/blog_post.html`)

**LOW:** Many inline styles found (49) (`./templates/index.html`)

**INFO:** TODO/FIXME comment found (`./comprehensive_scan.py`:164)

**INFO:** TODO/FIXME comment found (`./comprehensive_scan.py`:166)

## Recommendations

### 📋 Medium Priority
Consider addressing 11 medium-priority issues for optimization.

### 📈 Overall Assessment
**Critical:** Website has critical issues that must be resolved before deployment.

---
*Report generated by The Grey Canvas Comprehensive Scanner*
