"""
Integration tests for API server endpoints
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
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
    user.full_name = "Test User"
    user.created_at = "2023-01-01T00:00:00"
    user.last_login = "2023-01-01T00:00:00"
    return user


@pytest.fixture
def auth_token(mock_user):
    """JWT token fixture"""
    return create_access_token({"sub": mock_user.username, "role": mock_user.role})


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self, client):
        """Test root health check"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "ok"

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""

    @patch('src.api_server.get_user_by_username')
    @patch('src.api_server.get_user_by_email')
    @patch('src.api_server.create_user')
    @patch('src.api_server.get_db')
    def test_register_success(self, mock_get_db, mock_create_user, mock_get_email, mock_get_username, client):
        """Test successful user registration"""
        mock_get_username.return_value = None
        mock_get_email.return_value = None

        mock_new_user = Mock()
        mock_new_user.username = "newuser"
        mock_new_user.email = "new@example.com"
        mock_create_user.return_value = mock_new_user

        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepassword123",
            "role": "researcher"
        }

        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_existing_username(self, client):
        """Test registration with existing username"""
        with patch('src.api_server.get_user_by_username') as mock_get_user:
            mock_existing_user = Mock()
            mock_existing_user.username = "existinguser"
            mock_get_user.return_value = mock_existing_user

            user_data = {
                "username": "existinguser",
                "email": "new@example.com",
                "password": "securepassword123",
                "role": "researcher"
            }

            response = client.post("/auth/register", json=user_data)
            assert response.status_code == 400
            assert "Username already registered" in response.json()["detail"]

    def test_register_existing_email(self, client):
        """Test registration with existing email"""
        with patch('src.api_server.get_user_by_username') as mock_get_user, \
             patch('src.api_server.get_user_by_email') as mock_get_email:

            mock_get_user.return_value = None
            mock_existing_email = Mock()
            mock_existing_email.email = "existing@example.com"
            mock_get_email.return_value = mock_existing_email

            user_data = {
                "username": "newuser",
                "email": "existing@example.com",
                "password": "securepassword123",
                "role": "researcher"
            }

            response = client.post("/auth/register", json=user_data)
            assert response.status_code == 400
            assert "Email already registered" in response.json()["detail"]

    @patch('src.api_server.authenticate_user')
    def test_login_success(self, mock_authenticate, mock_user, client):
        """Test successful login"""
        mock_authenticate.return_value = mock_user

        login_data = {
            "username": "testuser",
            "password": "testpass"
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @patch('src.api_server.authenticate_user')
    def test_login_failure(self, mock_authenticate, client):
        """Test login failure"""
        mock_authenticate.return_value = None

        login_data = {
            "username": "testuser",
            "password": "wrongpass"
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]


class TestProtectedEndpoints:
    """Test protected endpoints"""

    def test_research_without_auth(self, client):
        """Test research endpoint without authentication"""
        response = client.get("/research?query=test")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_research_with_jwt(self, client, auth_token, mock_user):
        """Test research endpoint with JWT authentication"""
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

            # Setup mocks
            mock_graph_instance = Mock()
            mock_graph_instance.run.return_value = "Test research result"
            mock_graph.return_value = mock_graph_instance

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/research?query=test", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "test"
            assert data["result_markdown"] == "Test research result"

    def test_research_insufficient_permissions(self, client, auth_token, mock_user):
        """Test research endpoint with insufficient permissions"""
        with patch('src.api_server.get_current_active_user', return_value=mock_user), \
             patch('src.api_server.check_user_permissions', return_value=False):

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/research?query=test", headers=headers)

            assert response.status_code == 403
            assert "Insufficient permissions" in response.json()["detail"]

    def test_research_with_api_key(self, client, mock_user):
        """Test research endpoint with API key authentication"""
        with patch('src.api_server.get_user_by_api_key', return_value=mock_user), \
             patch('src.api_server.check_user_permissions', return_value=True), \
             patch('src.api_server.check_rate_limit', return_value=None), \
             patch('src.api_server.WebResearchTool') as mock_web_tool, \
             patch('src.api_server.RAGMemory') as mock_rag_memory, \
             patch('src.api_server.get_docs_provider') as mock_docs_provider, \
             patch('src.api_server.PlannerAgent') as mock_planner, \
             patch('src.api_server.ResearcherAgent') as mock_researcher, \
             patch('src.api_server.SynthesizerAgent') as mock_synthesizer, \
             patch('src.api_server.ResearchGraph') as mock_graph:

            # Setup mocks
            mock_graph_instance = Mock()
            mock_graph_instance.run.return_value = "Test research result"
            mock_graph.return_value = mock_graph_instance

            headers = {"X-API-Key": mock_user.api_key}
            response = client.get("/research?query=test", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "test"
            assert data["result_markdown"] == "Test research result"


class TestUserManagementEndpoints:
    """Test user management endpoints"""

    def test_get_current_user_profile(self, client, auth_token, mock_user):
        """Test getting current user profile"""
        with patch('src.api_server.get_current_active_user', return_value=mock_user):

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/auth/me", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == mock_user.username
            assert data["email"] == mock_user.email
            assert data["role"] == mock_user.role

    def test_update_user_profile(self, client, auth_token, mock_user):
        """Test updating user profile"""
        with patch('src.api_server.get_current_active_user', return_value=mock_user), \
             patch('src.api_server.get_db') as mock_get_db:

            mock_db = Mock()
            mock_get_db.return_value = mock_db

            headers = {"Authorization": f"Bearer {auth_token}"}
            update_data = {
                "full_name": "Updated Name",
                "email": "updated@example.com"
            }

            response = client.put("/auth/me", json=update_data, headers=headers)

            assert response.status_code == 200
            assert "Profile updated successfully" in response.json()["message"]

    def test_change_password_success(self, client, auth_token, mock_user):
        """Test successful password change"""
        with patch('src.api_server.get_current_active_user', return_value=mock_user), \
             patch('src.api_server.verify_password', return_value=True), \
             patch('src.api_server.update_user_password'), \
             patch('src.api_server.get_db') as mock_get_db:

            mock_db = Mock()
            mock_get_db.return_value = mock_db

            headers = {"Authorization": f"Bearer {auth_token}"}
            password_data = {
                "old_password": "oldpass",
                "new_password": "newsecurepass123"
            }

            response = client.post("/auth/change-password", json=password_data, headers=headers)

            assert response.status_code == 200
            assert "Password changed successfully" in response.json()["message"]

    def test_change_password_wrong_old(self, client, auth_token, mock_user):
        """Test password change with wrong old password"""
        with patch('src.api_server.get_current_active_user', return_value=mock_user), \
             patch('src.api_server.verify_password', return_value=False):

            headers = {"Authorization": f"Bearer {auth_token}"}
            password_data = {
                "old_password": "wrongoldpass",
                "new_password": "newsecurepass123"
            }

            response = client.post("/auth/change-password", json=password_data, headers=headers)

            assert response.status_code == 400
            assert "Incorrect old password" in response.json()["detail"]


class TestAdminEndpoints:
    """Test admin-only endpoints"""

    def test_list_users_admin(self, client, auth_token, mock_user):
        """Test listing users as admin"""
        admin_user = Mock(spec=User)
        admin_user.id = 1
        admin_user.username = "admin"
        admin_user.role = UserRole.ADMIN.value
        admin_user.is_active = True

        with patch('src.api_server.require_role', return_value=lambda: admin_user), \
             patch('src.api_server.get_db') as mock_get_db:

            mock_db = Mock()
            mock_users = [mock_user]
            mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_users
            mock_get_db.return_value = mock_db

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/admin/users", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_list_users_non_admin(self, client, auth_token, mock_user):
        """Test listing users as non-admin"""
        with patch('src.api_server.require_role') as mock_require_role:
            mock_require_role.side_effect = HTTPException(status_code=403, detail="Forbidden")

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/admin/users", headers=headers)

            assert response.status_code == 403


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_exceeded(self, client, auth_token, mock_user):
        """Test rate limit exceeded"""
        with patch('src.api_server.get_current_active_user', return_value=mock_user), \
             patch('src.api_server.check_user_permissions', return_value=True), \
             patch('src.api_server.check_rate_limit') as mock_rate_limit:

            mock_rate_limit.side_effect = HTTPException(status_code=429, detail="Rate limit exceeded")

            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/research?query=test", headers=headers)

            assert response.status_code == 429
            assert "Rate limit exceeded" in response.json()["detail"]


class TestSecurityHeaders:
    """Test security headers"""

    def test_security_headers_present(self, client):
        """Test that security headers are present in responses"""
        response = client.get("/")

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "max-age=31536000" in response.headers.get("Strict-Transport-Security", "")
        assert response.headers.get("Content-Security-Policy") == "default-src 'self'"


class TestCORS:
    """Test CORS functionality"""

    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/research", headers={"Origin": "http://localhost:3000"})

        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers