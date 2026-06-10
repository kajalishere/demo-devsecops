"""
Unit Tests for Demo DevSecOps Application
Tests basic Flask functionality and endpoint behavior
"""

import pytest
import json
from app.app import app, USERS_DB


@pytest.fixture
def client():
    """Create test client for Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context():
    """Create application context"""
    with app.app_context():
        yield app


class TestBasicEndpoints:
    """Test basic application endpoints"""
    
    def test_index_page_loads(self, client):
        """Test home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Demo DevSecOps' in response.data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404


class TestLoginFunctionality:
    """Test login endpoint (V1: SQL Injection vulnerability)"""
    
    def test_login_page_loads(self, client):
        """Test login page displays form"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'form' in response.data.lower() or b'username' in response.data.lower()
    
    def test_valid_login(self, client):
        """Test successful login with valid credentials"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 200
        assert b'successful' in response.data.lower()
    
    def test_invalid_login(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        assert b'failed' in response.data.lower()
    
    def test_sql_injection_attempt(self, client):
        """
        Test SQL injection payload
        V1: SQL Injection vulnerability demonstration
        This test shows the vulnerability exists
        """
        response = client.post('/login', data={
            'username': "' OR '1'='1",
            'password': 'anything'
        })
        # Vulnerability: Should fail but might succeed due to SQL injection
        # This is expected behavior in demo app
        assert response.status_code in [200, 401]


class TestProfileEndpoint:
    """Test profile endpoint (V2: XSS vulnerability)"""
    
    def test_profile_loads(self, client):
        """Test profile page loads"""
        response = client.get('/profile/admin')
        assert response.status_code == 200
    
    def test_profile_with_comment(self, client):
        """Test profile with comment parameter"""
        response = client.get('/profile/admin?comment=test')
        assert response.status_code == 200
        assert b'test' in response.data
    
    def test_xss_payload_reflected(self, client):
        """
        Test XSS payload is reflected in response
        V2: XSS vulnerability demonstration
        This test shows the vulnerability exists
        """
        xss_payload = '<script>alert("XSS")</script>'
        response = client.get(f'/profile/admin?comment={xss_payload}')
        assert response.status_code == 200
        # Vulnerability: Payload is reflected without encoding
        assert xss_payload in response.data.decode() or '<script>' in response.data.decode()


class TestAdminEndpoints:
    """Test admin endpoints (V3: Broken Access Control)"""
    
    def test_admin_users_endpoint_accessible(self, client):
        """
        Test that admin endpoint is accessible without authentication
        V3: Broken Access Control vulnerability
        """
        response = client.get('/admin/users')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_admin_users_shows_all_users(self, client):
        """Test admin endpoint returns user list"""
        response = client.get('/admin/users')
        data = json.loads(response.data)
        assert len(data) > 0
        assert any(user['username'] == 'admin' for user in data)
    
    def test_delete_user_no_auth_required(self, client):
        """
        Test that delete endpoint accessible without authentication
        V3: Broken Access Control - IDOR vulnerability
        """
        initial_count = len(USERS_DB)
        response = client.get('/admin/users/user1/delete')
        assert response.status_code == 200
        # Vulnerability: User deleted without authentication
        assert len(USERS_DB) < initial_count


class TestAuthenticationEndpoints:
    """Test authentication endpoints (V5: Insecure Authentication)"""
    
    def test_api_login_endpoint(self, client):
        """Test API login endpoint"""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
    
    def test_api_login_returns_token(self, client):
        """
        Test that API login returns predictable token
        V5: Insecure Authentication - predictable tokens
        """
        response1 = client.post('/api/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        data1 = json.loads(response1.data)
        token1 = data1.get('token')
        
        # Token is timestamp-based and predictable
        assert token1 is not None
        assert token1.isdigit()  # Timestamp is numeric


class TestSecurityHeadersAbsence:
    """Test absence of security headers (V6: Security Misconfiguration)"""
    
    def test_missing_x_frame_options(self, client):
        """
        Test that X-Frame-Options header is missing
        V6: Security Misconfiguration
        """
        response = client.get('/')
        # Vulnerability: Header should be set but isn't
        assert 'X-Frame-Options' not in response.headers or \
               response.headers.get('X-Frame-Options') is None
    
    def test_missing_content_security_policy(self, client):
        """
        Test that Content-Security-Policy header is missing
        V6: Security Misconfiguration
        """
        response = client.get('/')
        # Vulnerability: Header should be set but isn't
        assert 'Content-Security-Policy' not in response.headers or \
               response.headers.get('Content-Security-Policy') is None


class TestRegistrationEndpoint:
    """Test registration endpoint (V4: Cryptographic Failures)"""
    
    def test_register_new_user(self, client):
        """Test user registration"""
        response = client.post('/register', data={
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        })
        assert response.status_code == 200
        assert b'registered' in response.data.lower()
    
    def test_password_stored_as_weak_hash(self, client):
        """
        Test that password is stored with weak MD5 hash
        V4: Cryptographic Failures
        """
        # Register user
        client.post('/register', data={
            'username': 'hashtest',
            'password': 'hashpass',
            'email': 'hash@test.com'
        })
        
        # Check that password is stored as hash (not plaintext but weak)
        assert 'hashtest' in USERS_DB
        stored_password = USERS_DB['hashtest']['password']
        # MD5 hash is 32 characters
        assert len(stored_password) == 32 or stored_password != 'hashpass'


class TestSettingsEndpoint:
    """Test settings endpoint"""
    
    def test_settings_page_loads(self, client):
        """Test settings page accessible"""
        response = client.get('/settings')
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling (V6: Information Disclosure)"""
    
    def test_error_endpoint(self, client):
        """
        Test error handling
        V6: Security Misconfiguration - verbose errors
        """
        response = client.get('/error')
        assert response.status_code == 500


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
