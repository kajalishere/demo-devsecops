# Setup Guide: Demo DevSecOps

Complete step-by-step guide to set up and run the demo-devsecops project locally.

---

## Prerequisites

Before you start, ensure you have:

- **Python 3.9+** installed
- **Git** installed
- **pip** (Python package manager)
- **Virtual environment support** (venv)
- **~500MB disk space** for dependencies
- **Internet connection** for downloading packages

### Check Your Setup

```bash
python3 --version      # Should be 3.9 or higher
git --version          # Should be 2.0 or higher
pip --version          # Should be 20.0 or higher
```

---

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/kajalishere/demo-devsecops.git

# Navigate to the project directory
cd demo-devsecops
```

### Step 2: Create Virtual Environment

A virtual environment isolates Python dependencies for this project.

#### On macOS/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

#### On Windows (Command Prompt):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

#### On Windows (PowerShell):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# You should see (venv) in your terminal prompt
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Expected output:** You'll see packages installing (Flask, Werkzeug, pytest, bandit, safety, etc.)

### Step 4: Verify Installation

```bash
# Check if Flask is installed
python -c "import flask; print(flask.__version__)"

# Check if Bandit is available
bandit --version

# Check if Safety is available
safety --version
```

If all commands run without errors, installation is successful! ✅

---

## Running the Application

### Option 1: Run Flask App Directly

```bash
# Make sure virtual environment is activated
# Run the Flask development server
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

### Option 2: Run with Flask CLI

```bash
# Set Flask app
export FLASK_APP=app.py     # macOS/Linux
set FLASK_APP=app.py        # Windows

# Run Flask
flask run
```

### Option 3: Run with Gunicorn (Production-like)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Access the Application

Open your browser and go to:
```
http://localhost:5000
```

You should see the application homepage.

---

## Security Testing

### Running Local Security Scans

#### 1. SAST Scan with Bandit

```bash
# Run Bandit on the app folder
bandit -r app/ -f json -o bandit-report.json

# View the report
cat bandit-report.json
```

**What it checks:**
- Hardcoded SQL queries
- Insecure cryptography
- Hardcoded secrets
- Weak password hashing
- Insecure deserialization

**Output location:** `bandit-report.json`

#### 2. Dependency Vulnerability Check with Safety

```bash
# Check for vulnerable packages
safety check --json > safety-report.json

# View the report
cat safety-report.json
```

**What it checks:**
- Known vulnerabilities in installed packages
- Outdated packages
- Security advisories

**Output location:** `safety-report.json`

#### 3. Run Unit Tests

```bash
# Run pytest to execute tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=html
```

**Coverage report location:** `htmlcov/index.html`

#### 4. Manual DAST Testing

```bash
# Start the application
python app.py

# In another terminal, test endpoints
# Test SQL Injection
curl "http://localhost:5000/login?username=' OR '1'='1&password=anything"

# Test XSS
curl "http://localhost:5000/profile?comment=<script>alert('XSS')</script>"

# Test Broken Access Control
curl "http://localhost:5000/admin/users/1/delete"
```

#### 5. OWASP ZAP Scanning (Advanced)

```bash
# Install OWASP ZAP from https://www.zaproxy.org/download/

# Run ZAP in daemon mode
zaproxy -cmd -quickurl http://localhost:5000 -quickout zap-report.html

# View the report
open zap-report.html
```

---

## Project Structure

```
demo-devsecops/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── app.py                # Main application with vulnerabilities
│   └── models.py             # Database models (if applicable)
│
├── docs/
│   ├── VULNERABILITIES.md    # Detailed vulnerability documentation
│   ├── SETUP_GUIDE.md        # This file
│   ├── THREAT_MODEL.md       # Threat hunting methodology
│   └── CI_CD_PIPELINE.md     # GitHub Actions workflow guide
│
├── tests/
│   ├── test_app.py           # Unit tests
│   └── test_security.py      # Security-specific tests
│
├── .github/
│   └── workflows/
│       └── security-scan.yml # GitHub Actions workflow
│
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container configuration
├── README.md                 # Project overview
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
└── app.py                   # Flask application entry point
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# .env
FLASK_ENV=development
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///demo.db
```

**Note:** Never commit `.env` to Git! It's in `.gitignore` by default.

### Flask Configuration

Edit `app.py` to configure Flask:

```python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DEBUG'] = False  # Disable debug in production
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
```

---

## Troubleshooting

### Issue: "Python command not found"

**Solution:**
```bash
# Use python3 instead
python3 app.py

# Or add Python to PATH (Windows)
# Then use: python app.py
```

### Issue: "No module named 'flask'"

**Solution:**
```bash
# Check if virtual environment is activated
# You should see (venv) in your terminal

# If not, activate it:
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# Then install requirements again
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"

**Solution:**
```bash
# Use a different port
python app.py --port 5001

# Or kill the process using port 5000
# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "ModuleNotFoundError" for bandit/safety

**Solution:**
```bash
# Install missing tools
pip install bandit safety

# Verify installation
bandit --version
safety --version
```

### Issue: Permissions denied on Linux/macOS

**Solution:**
```bash
# Make scripts executable
chmod +x venv/bin/activate

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

---

## Development Workflow

### 1. Make Changes to Code

Edit files in the `app/` directory:

```python
# Example: Edit app/app.py
@app.route('/new-endpoint')
def new_endpoint():
    return "Hello, World!"
```

### 2. Test Locally

```bash
# Run the app
python app.py

# Open in browser
# http://localhost:5000/new-endpoint
```

### 3. Run Security Scans

```bash
# SAST scan
bandit -r app/ -f json -o bandit-report.json

# Dependency check
safety check --json > safety-report.json

# Unit tests
pytest tests/ -v
```

### 4. Commit Changes

```bash
# Add changes to git
git add app/app.py

# Commit with descriptive message
git commit -m "feat: add new endpoint for user profiles"

# Push to GitHub (triggers GitHub Actions)
git push origin main
```

### 5. GitHub Actions Runs Automatically

Your security scans run automatically when you push:
- Bandit SAST scan
- Safety dependency check
- Unit tests
- Results appear in Actions tab

---

## Docker Setup (Optional)

### Build Docker Image

```bash
# Build the image
docker build -t demo-devsecops:latest .

# Run the container
docker run -p 5000:5000 demo-devsecops:latest

# Access at http://localhost:5000
```

### Docker Compose (Multiple Services)

```bash
# Install Docker Compose
# Already included in Docker Desktop

# Run services
docker-compose up

# Stop services
docker-compose down
```

---

## Production Deployment (Not Recommended for This Demo!)

**⚠️ WARNING:** This app is intentionally vulnerable. Do NOT deploy to production!

If you absolutely must deploy for educational purposes:

```bash
# 1. Use a production WSGI server
pip install gunicorn

# 2. Disable debug mode
export FLASK_ENV=production

# 3. Set strong secret key
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# 4. Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 5. Use reverse proxy (Nginx)
# 6. Enable HTTPS with Let's Encrypt
# 7. Apply all security headers
# 8. Use Web Application Firewall (WAF)
```

**Better approach:** Use in isolated lab environments only!

---

## Performance Tuning

### Optimize Flask

```python
# In app.py
from flask import Flask
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/data')
@cache.cached(timeout=300)
def get_data():
    # Cache results for 5 minutes
    return expensive_operation()
```

### Monitor Performance

```bash
# Install monitoring tools
pip install flask-profiler

# Profile requests
# See detailed timing in profiler
```

---

## Security Best Practices

### During Development

✅ **DO:**
- Use `.env` for secrets
- Run security scans before committing
- Review Bandit reports
- Keep dependencies updated
- Use parameterized queries
- Escape user input
- Enable CSRF protection

❌ **DON'T:**
- Commit secrets to Git
- Use debug=True in production
- Hardcode credentials
- Trust user input
- Use pickle for untrusted data
- Disable security headers
- Use weak cryptography

---

## Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade Flask

# Save updated versions
pip freeze > requirements.txt
```

---

## Uninstalling / Cleanup

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv              # macOS/Linux
rmdir /s venv           # Windows

# Remove generated files
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf htmlcov
rm bandit-report.json
rm safety-report.json
```

---

## Getting Help

### Documentation

- **Flask Docs:** https://flask.palletsprojects.com/
- **Bandit Docs:** https://bandit.readthedocs.io/
- **Safety Docs:** https://safetycli.com/
- **OWASP Testing Guide:** https://owasp.org/www-project-web-security-testing-guide/

### Common Issues

- Check GitHub Issues: https://github.com/kajalishere/demo-devsecops/issues
- Review README.md for quick start
- Check VULNERABILITIES.md for exploit examples

### Contact

- GitHub: @kajalishere

---

## Quick Reference

```bash
# Complete setup in one go
git clone https://github.com/kajalishere/demo-devsecops.git
cd demo-devsecops
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python app.py

# In another terminal:
bandit -r app/
safety check
pytest tests/
```

---

**Last Updated:** June 2026 | **Status:** Active Development
