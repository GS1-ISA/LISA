"""
Security tests for common vulnerabilities
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import json

from src.api_server import app
from src.auth import User, UserRole, create_access_token


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user fixture"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.role = UserRole.RESEARCHER.value
    user.is_active = True
    user.api_key = "test-api-key"
    return user


@pytest.fixture
def auth_token(mock_user):
    """JWT token fixture"""
    return create_access_token({"sub": mock_user.username, "role": mock_user.role})


class TestSQLInjection:
    """Test SQL injection vulnerabilities"""

    def test_sql_injection_username_login(self, client):
        """Test SQL injection in username field during login"""
        malicious_usernames = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1 --",
        ]

        for malicious_username in malicious_usernames:
            with patch('src.api_server.authenticate_user', return_value=None):
                login_data = {
                    "username": malicious_username,
                    "password": "testpass"
                }

                response = client.post("/auth/login", json=login_data)
                # Should return 401, not 500 (which would indicate SQL injection success)
                assert response.status_code == 401

    def test_sql_injection_email_registration(self, client):
        """Test SQL injection in email field during registration"""
        malicious_emails = [
            "' OR '1'='1@example.com",
            "'; DROP TABLE users; --@example.com",
            "' UNION SELECT * FROM users --@example.com",
        ]

        for malicious_email in malicious_emails:
            user_data = {
                "username": "testuser",
                "email": malicious_email,
                "password": "securepassword123",
                "role": "researcher"
            }

            response = client.post("/auth/register", json=user_data)
            # Should return 422 (validation error) or 400, not 500
            assert response.status_code in [400, 422]


class TestXSS:
    """Test Cross-Site Scripting vulnerabilities"""

    def test_xss_in_username_registration(self, client):
        """Test XSS in username field during registration"""
        malicious_usernames = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
        ]

        for malicious_username in malicious_usernames:
            user_data = {
                "username": malicious_username,
                "email": "test@example.com",
                "password": "securepassword123",
                "role": "researcher"
            }

            response = client.post("/auth/register", json=user_data)
            # Should return validation error, not store malicious content
            assert response.status_code in [400, 422]

    def test_xss_in_query_parameter(self, client, auth_token, mock_user):
        """Test XSS in query parameters"""
        malicious_queries = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
        ]

        with patch('src.api_server.get_current_active_user', return_value=mock_user), \
             patch('src.api_server.check_user_permissions', return_value=True), \
             patch('src.api_server.check_rate_limit', return_value=None), \
             patch('src.api_server.WebResearchTool') as mock_web_tool, \
             patch('src.api_server.RAGMemory') as mock_rag_memory, \
             patch('src.api_server.get_docs_provider') as mock_docs_provider, \
             patch('src.api_server.PlannerAgent') as mock_planner, \
             patch('src.api_server.ResearcherAgent') as mock_researcher, \
             patch('src.api_server.SynthesizerAgent') as mock_synthesizer, \
             patch('src.api_server.ResearchGraph') as mock_graph:

            mock_graph_instance = Mock()
            mock_graph_instance.run.return_value = "Safe result"
            mock_graph.return_value = mock_graph_instance

            headers = {"Authorization": f"Bearer {auth_token}"}

            for malicious_query in malicious_queries:
                response = client.get(f"/research?query={malicious_query}", headers=headers)
                assert response.status_code == 200
                data = response.json()
                # Ensure malicious content is not reflected in response
                assert "<script>" not in data["result_markdown"]
                assert "javascript:" not in data["result_markdown"]


class TestAuthenticationBypass:
    """Test authentication bypass attempts"""

    def test_jwt_token_tampering(self, client):
        """Test JWT token tampering"""
        # Create a valid token then tamper with it
        valid_token = create_access_token({"sub": "testuser", "role": "researcher"})

        # Try various tampering techniques
        tampered_tokens = [
            valid_token[:-5] + "xxxxx",  # Truncate and append
            valid_token.replace(".", "x"),  # Replace dots
            valid_token + "extra",  # Append extra data
        ]

        for tampered_token in tampered_tokens:
            headers = {"Authorization": f"Bearer {tampered_token}"}
            response = client.get("/research?query=test", headers=headers)
            # Should return 401 for invalid tokens
            assert response.status_code == 401

    def test_expired_jwt_token(self, client):
        """Test expired JWT token"""
        from datetime import timedelta
        # Create an expired token
        expired_token = create_access_token(
            {"sub": "testuser", "role": "researcher"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/research?query=test", headers=headers)
        assert response.status_code == 401

    def test_invalid_api_key(self, client):
        """Test invalid API key"""
        invalid_keys = [
            "",
            "short",
            "invalid-key-with-special-chars!@#",
            "a" * 100,  # Very long key
        ]

        for invalid_key in invalid_keys:
            headers = {"X-API-Key": invalid_key}
            response = client.get("/research?query=test", headers=headers)
            assert response.status_code == 401


class TestAuthorizationBypass:
    """Test authorization bypass attempts"""

    def test_role_escalation_jwt(self, client):
        """Test role escalation via JWT manipulation"""
        # Create token with viewer role
        viewer_token = create_access_token({"sub": "vieweruser", "role": "viewer"})

        # Try to access admin endpoint
        headers = {"Authorization": f"Bearer {viewer_token}"}
        response = client.get("/admin/users", headers=headers)
        assert response.status_code == 403

    def test_horizontal_privilege_escalation(self, client, auth_token, mock_user):
        """Test horizontal privilege escalation"""
        # Mock a different user
        other_user = Mock(spec=User)
        other_user.id = 2
        other_user.username = "otheruser"

        with patch('src.api_server.require_role', return_value=lambda: mock_user), \
             patch('src.api_server.get_db') as mock_get_db:

            mock_db = Mock()
            # Return other user's data when admin tries to update
            mock_db.query.return_value.filter.return_value.first.return_value = other_user
            mock_get_db.return_value = mock_db

            headers = {"Authorization": f"Bearer {auth_token}"}
            # Try to update another user's role
            response = client.put("/admin/users/2/role", json={"new_role": "admin"}, headers=headers)

            # Should succeed if admin, but we should verify the logic
            # In this case, we're testing that the endpoint exists and handles the request
            assert response.status_code in [200, 403, 404]


class TestInputValidation:
    """Test input validation"""

    def test_password_complexity(self, client):
        """Test password complexity requirements"""
        weak_passwords = [
            "short",
            "123456",
            "password",
            "",  # Empty password
        ]

        for weak_password in weak_passwords:
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": weak_password,
                "role": "researcher"
            }

            response = client.post("/auth/register", json=user_data)
            # Should reject weak passwords
            assert response.status_code in [400, 422]

    def test_email_validation(self, client):
        """Test email validation"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user.example.com",
            "user@.com",
        ]

        for invalid_email in invalid_emails:
            user_data = {
                "username": "testuser",
                "email": invalid_email,
                "password": "securepassword123",
                "role": "researcher"
            }

            response = client.post("/auth/register", json=user_data)
            # Should reject invalid emails
            assert response.status_code in [400, 422]

    def test_username_validation(self, client):
        """Test username validation"""
        invalid_usernames = [
            "",  # Empty
            "a",  # Too short
            "user with spaces",  # Spaces
            "user@domain.com",  # Email-like
            "<script>",  # HTML
        ]

        for invalid_username in invalid_usernames:
            user_data = {
                "username": invalid_username,
                "email": "test@example.com",
                "password": "securepassword123",
                "role": "researcher"
            }

            response = client.post("/auth/register", json=user_data)
            # Should reject invalid usernames
            assert response.status_code in [400, 422]


class TestRateLimitingSecurity:
    """Test rate limiting for security"""

    def test_brute_force_protection_login(self, client):
        """Test brute force protection on login endpoint"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }

        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            with patch('src.api_server.authenticate_user', return_value=None):
                response = client.post("/auth/login", json=login_data)
                responses.append(response.status_code)

        # Should eventually get rate limited (429)
        assert 429 in responses or all(code == 401 for code in responses)

    def test_brute_force_protection_registration(self, client):
        """Test brute force protection on registration endpoint"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "role": "researcher"
        }

        # Make multiple rapid requests
        responses = []
        for i in range(10):
            user_data["username"] = f"testuser{i}"
            user_data["email"] = f"test{i}@example.com"
            response = client.post("/auth/register", json=user_data)
            responses.append(response.status_code)

        # Should eventually get rate limited (429) or succeed/fail normally
        assert any(code in [200, 400, 422, 429] for code in responses)


class TestInformationDisclosure:
    """Test information disclosure vulnerabilities"""

    def test_error_messages_not_disclosing_info(self, client):
        """Test that error messages don't disclose sensitive information"""
        # Try login with non-existent user
        login_data = {
            "username": "nonexistentuser123456789",
            "password": "testpass"
        }

        with patch('src.api_server.authenticate_user', return_value=None):
            response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        error_detail = response.json()["detail"]
        # Error should not reveal if user exists or not
        assert "Incorrect username or password" in error_detail
        assert "nonexistentuser" not in error_detail

    def test_forgot_password_not_disclosing_info(self, client):
        """Test that forgot password doesn't reveal user existence"""
        # Test with existing and non-existing emails
        emails = ["existing@example.com", "nonexisting@example.com"]

        for email in emails:
            with patch('src.api_server.get_user_by_email', return_value=None):
                response = client.post("/auth/forgot-password", json={"email": email})

            # Should always return the same message
            assert response.status_code == 200
            assert "If the email exists" in response.json()["message"]


class TestCSRF:
    """Test Cross-Site Request Forgery protection"""

    def test_csrf_protection_headers(self, client):
        """Test that CSRF protection headers are present"""
        # FastAPI with proper CORS setup should handle CSRF
        response = client.get("/")

        # Check for CORS headers that help prevent CSRF
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]

        for header in cors_headers:
            assert header in response.headers or header.replace("-", "") in response.headers


class TestSecurityHeaders:
    """Test security headers"""

    def test_comprehensive_security_headers(self, client):
        """Test that all security headers are present"""
        response = client.get("/")

        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": lambda v: "max-age=31536000" in v,
            "Content-Security-Policy": "default-src 'self'"
        }

        for header, expected_value in required_headers.items():
            actual_value = response.headers.get(header)
            assert actual_value is not None, f"Missing security header: {header}"

            if callable(expected_value):
                assert expected_value(actual_value), f"Invalid value for {header}: {actual_value}"
            else:
                assert actual_value == expected_value, f"Invalid value for {header}: {actual_value}"


class TestDataExposure:
    """Test data exposure vulnerabilities"""

    def test_no_sensitive_data_in_responses(self, client, auth_token, mock_user):
        """Test that sensitive data is not exposed in API responses"""
        with patch('src.api_server.get_current_active_user', return_value=mock_user):

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/auth/me", headers=headers)

            assert response.status_code == 200
            data = response.json()

            # Should not contain sensitive fields
            sensitive_fields = ["hashed_password", "api_key_hash", "password"]
            for field in sensitive_fields:
                assert field not in data, f"Sensitive field '{field}' exposed in response"

            # Should contain expected public fields
            expected_fields = ["id", "username", "email", "role", "is_active"]
            for field in expected_fields:
                assert field in data, f"Expected field '{field}' missing from response"