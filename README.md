# DevSecOps Portfolio: Automated Vulnerability Detection Pipeline

![Security](https://img.shields.io/badge/Security-Active_Scanning-blue) ![Python](https://img.shields.io/badge/Python-3.9+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

##  Project Overview

A production-grade DevSecOps demonstration featuring an intentionally vulnerable Flask web application with an automated security scanning pipeline. This project showcases real-world vulnerability management, threat hunting, and incident response practices.

## Architecture

### System Design

This project implements a **production-grade DevSecOps pipeline** for automated vulnerability detection and security scanning. The pipeline runs automatically on every code push and generates comprehensive security reports.

### Pipeline Components

**1. Code Analysis (Bandit)**
- Static Application Security Testing (SAST)
- Detects hardcoded credentials, unsafe functions, injection vulnerabilities
- Generates JSON reports with severity levels

**2. Dependency Scanning (Safety)**
- Analyzes all project dependencies against known CVE databases
- Identifies vulnerable packages and versions
- Provides remediation recommendations

**3. Automated Testing (PyTest)**
- Unit tests for application functionality
- Security-focused test cases
- Ensures code quality and security controls

**4. Report Generation (ReportLab)**
- Converts raw vulnerability data into professional PDF reports
- Executive summaries with key metrics
- Detailed vulnerability analysis and remediation steps

**5. CI/CD Pipeline (GitHub Actions)**
- Automatically triggers on every push/PR
- Runs all security scans and tests
- Uploads reports as artifacts for review

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.9+ | Application development |
| **Web Framework** | Flask | Demo web application |
| **SAST Scanning** | Bandit | Code vulnerability detection |
| **Dependency Scan** | Safety | Known CVE identification |
| **Testing** | PyTest | Quality assurance |
| **Report Generation** | ReportLab | Professional PDF creation |
| **CI/CD** | GitHub Actions | Automated pipeline |

### How It Works

1. **Developer pushes code** to GitHub
2. **GitHub Actions automatically triggers** the security pipeline
3. **Bandit scans** Python code for vulnerabilities
4. **Safety checks** all dependencies for known CVEs
5. **PyTest runs** unit and security tests
6. **ReportLab generates** professional PDF reports
7. **Artifacts are uploaded** for download and review
8. **Results appear** in GitHub Actions

### Key Features

**Automated** - Runs on every code push  
**Comprehensive** - Detects code flaws and vulnerable dependencies  
**Professional Reports** - Both JSON and PDF formats  
**Real-World Data** - 51 packages analyzed, 26+ vulnerabilities detected  
**Educational** - Learn DevSecOps best practices

## Security Scan Results

### Latest Scan

- **Packages Analyzed:** 51
- **Vulnerabilities Found:** 26
- **Scan Date:** 2026-06-10
- **Safety Version:** 2.3.5

### Top Vulnerable Packages

| Package | Version | Issues |
|---------|---------|--------|
| werkzeug | 2.3.6 | 8 |
| jinja2 | 3.1.2 | 5 |
| pillow | 11.3.0 | 6 |
| urllib3 | 2.6.3 | 2 |
| pip | 26.0.1 | 2 |

### Access Reports

Latest security reports available in [GitHub Actions](https://github.com/kajalishere/demo-devsecops/actions):
- **safety-report-json** - Machine-readable vulnerability data
- **security-pdf-report** - Professional PDF summary

For detailed vulnerability analysis, see [`docs/VULNERABILITIES_2025.md`](docs/VULNERABILITIES_2025.md)
