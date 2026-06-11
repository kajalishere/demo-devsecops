# DevSecOps Portfolio: Automated Vulnerability Detection Pipeline

![Security](https://img.shields.io/badge/Security-Active_Scanning-blue) ![Python](https://img.shields.io/badge/Python-3.9+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

##  Project Overview

A production-grade DevSecOps demonstration featuring an intentionally vulnerable Flask web application with an automated security scanning pipeline. This project showcases real-world vulnerability management, threat hunting, and incident response practices.

---

##  Architecture
### System Design

This project implements a **production-grade DevSecOps pipeline** for automated vulnerability detection and security scanning. The architecture demonstrates industry-standard practices for continuous security assessment in CI/CD workflows.

┌─────────────────────────────────────────────────────────────────┐
│                  Automated Security Scanning Pipeline             │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Code       │ -> │   Setup      │ -> │  Install     │       │
│  │   Checkout   │    │   Environment│    │  Dependencies│       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                    │                    │               │
│         └────────────────────┴────────────────────┘               │
│                              │                                    │
│    ┌─────────────────────────┴─────────────────────────┐          │
│    │                                                   │          │
│    ▼                    ▼                    ▼          ▼          │
│  ┌────────────────┐ ┌──────────────┐ ┌──────────┐ ┌────────┐    │
│  │ SAST Scanning  │ │ Dependency   │ │Unit &    │ │Artifact│    │
│  │(Code Analysis) │ │ Vulnerability│ │Security  │ │Upload  │    │
│  │                │ │ Checks       │ │Tests     │ │Reports │    │
│  └────────────────┘ └──────────────┘ └──────────┘ └────────┘    │
│         │                    │              │          │         │
│         └────────────────────┴──────────────┴──────────┘         │
│                              │                                    │
│                    ┌──────────────────────┐                      │
│                    │  Generate Reports    │                      │
│                    │  (JSON + PDF)        │                      │
│                    └──────────────────────┘                      │
│                              │                                    │
│                    ┌─────────┴──────────┐                        │
│                    ▼                    ▼                        │
│            ┌──────────────┐    ┌──────────────┐                 │
│            │ Machine      │    │ Human        │                 │
│            │ Readable     │    │ Readable     │                 │
│            │ (JSON)       │    │ (PDF)        │                 │
│            └──────────────┘    └──────────────┘                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

### Components

#### 1. **Code Repository**
- Source code to be analyzed
- Triggers pipeline on every push/PR
- Supports multiple branches (main, develop)
- Version controlled with Git

#### 2. **Static Application Security Testing (SAST)**
- **Tool:** Bandit
- **Purpose:** Analyzes Python source code for security vulnerabilities
- **Detects:**
  - Hardcoded credentials and secrets
  - Unsafe function usage
  - SQL injection risks
  - Weak cryptographic practices
  - Authentication/authorization flaws
- **Output:** JSON report with severity levels

#### 3. **Dependency Vulnerability Scanning**
- **Tool:** Safety
- **Purpose:** Identifies known vulnerabilities in installed packages
- **Analyzes:** All project dependencies against CVE databases
- **Reports:**
  - Package versions with known issues
  - CVE identifiers and descriptions
  - Remediation recommendations
  - Severity levels
- **Output:** Structured JSON with detailed vulnerability data

#### 4. **Automated Testing**
- **Tool:** PyTest
- **Scope:**
  - Unit tests for functionality
  - Security-focused test cases
  - Integration tests
- **Ensures:** Code quality and security controls

#### 5. **Report Generation Engine**
- **Tool:** ReportLab (PDF generation)
- **Input:** Raw vulnerability data (JSON)
- **Output:** Professional, formatted reports
- **Features:**
  - Executive summaries
  - Detailed vulnerability tables
  - Package-level analysis
  - Remediation recommendations
  - Timestamp and metadata

#### 6. **CI/CD Orchestration**
- **Platform:** GitHub Actions
- **Trigger:** Automatic on code push/PR
- **Environment:** Ubuntu Latest, Python 3.9+
- **Workflow:**
  1. Checkout repository
  2. Install dependencies
  3. Run SAST scan (Bandit)
  4. Run dependency scan (Safety)
  5. Execute test suite
  6. Generate reports (JSON + PDF)
  7. Upload artifacts
  8. Summary and notifications

### Technology Stack

| Layer | Technology | Function |
|-------|-----------|----------|
| **Version Control** | Git + GitHub | Code management & pipeline trigger |
| **CI/CD Platform** | GitHub Actions | Workflow automation |
| **Environment** | Python 3.9+ | Runtime environment |
| **SAST Analysis** | Bandit | Code vulnerability detection |
| **Dependency Scan** | Safety | Known CVE detection |
| **Testing** | PyTest | Quality assurance |
| **Report Generation** | ReportLab | Professional document creation |

### Security Scanning Features

**Automated Detection:**
- Known vulnerability databases (CVE, CVSS scores)
- Code quality issues
- Dependency version conflicts
- Security misconfigurations

**Comprehensive Reporting:**
- JSON output for automated processing
- PDF reports for stakeholder review
- Severity classification
- Remediation guidance
- CVE references with external links

**Continuous Integration:**
- Runs on every code change
- Fails on critical vulnerabilities (configurable)
- Generates artifacts for review
- Historical tracking of security metrics

### Scanning Workflow

The pipeline demonstrates a **shift-left security** approach:
## 📊 Security Scan Results

### Latest Scan Report

The automated security scanning pipeline generates comprehensive reports on every code push:

**Scan Summary:**
- **Packages Analyzed:** 51
- **Vulnerabilities Found:** 26
- **Scan Date:** 2026-06-10 20:20:05
- **Safety Version:** 2.3.5

**Top Vulnerable Packages:**
| Package | Version | Vulnerabilities |
|---------|---------|-----------------|
| werkzeug | 2.3.6 | 8 |
| jinja2 | 3.1.2 | 5 |
| pillow | 11.3.0 | 6 |
| urllib3 | 2.6.3 | 2 |
| pip | 26.0.1 | 2 |

### Download Reports

The latest security scan reports are available as GitHub Actions artifacts:

- **📄 JSON Report:** Machine-readable vulnerability data
  - Command: `safety check --json`
  - Format: Structured JSON with full CVE details

- **📑 PDF Report:** Professional executive summary
  - Generated via ReportLab
  - Includes vulnerability tables, recommendations
  - Ready for stakeholder review

**Access Reports:**
1. Go to [GitHub Actions](https://github.com/kajalishere/demo-devsecops/actions)
2. Click the latest "Security Scanning Pipeline" run
3. Download artifacts:
   - `safety-report-json`
   - `security-pdf-report`

### Vulnerability Categories (OWASP 2025)

The scanning pipeline detects vulnerabilities across all OWASP Top 10 categories:

- **A01:2025 – Broken Access Control**
- **A02:2025 – Cryptographic Failures**
- **A04:2025 – Insecure Design**
- **A05:2025 – Injection**
- **A07:2025 – Identification and Authentication Failures**
- **A08:2025 – Software and Data Integrity Failures**

See [`docs/VULNERABILITIES_2025.md`](docs/VULNERABILITIES_2025.md) for detailed analysis.
