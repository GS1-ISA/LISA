"""
Unit tests for authentication module
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.auth import (
    User, UserCreate, UserRole, hash_password, verify_password,
    create_access_token, verify_token, generate_api_key, hash_api_key,
    verify_api_key, authenticate_user, create_user, check_user_permissions,
    get_user_by_username, get_user_by_email, update_user_password
)


class TestPasswordHashing:
    """Test password hashing functions"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False


class TestJWT:
    """Test JWT token functions"""

    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser", "role": "researcher"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """Test JWT token verification with valid token"""
        data = {"sub": "testuser", "role": "researcher"}
        token = create_access_token(data)
        token_data = verify_token(token)

        assert token_data is not None
        assert token_data.username == "testuser"
        assert token_data.role == UserRole.RESEARCHER

    def test_verify_token_invalid(self):
        """Test JWT token verification with invalid token"""
        invalid_token = "invalid.jwt.token"
        token_data = verify_token(invalid_token)

        assert token_data is None


class TestAPIKey:
    """Test API key functions"""

    def test_generate_api_key(self):
        """Test API key generation"""
        key = generate_api_key()

        assert isinstance(key, str)
        assert len(key) == 32  # Should be 32 characters

    def test_hash_api_key(self):
        """Test API key hashing"""
        key = "testapikey123"
        hashed = hash_api_key(key)

        assert hashed != key
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_api_key_correct(self):
        """Test API key verification with correct key"""
        key = "testapikey123"
        hashed = hash_api_key(key)

        assert verify_api_key(key, hashed) is True

    def test_verify_api_key_incorrect(self):
        """Test API key verification with incorrect key"""
        key = "testapikey123"
        wrong_key = "wrongapikey"
        hashed = hash_api_key(key)

        assert verify_api_key(wrong_key, hashed) is False


class TestUserPermissions:
    """Test user permission functions"""

    def test_check_user_permissions_admin(self):
        """Test admin user permissions"""
        admin_user = Mock()
        admin_user.role = UserRole.ADMIN.value

        assert check_user_permissions(admin_user, UserRole.ADMIN) is True
        assert check_user_permissions(admin_user, UserRole.RESEARCHER) is True
        assert check_user_permissions(admin_user, UserRole.VIEWER) is True

    def test_check_user_permissions_researcher(self):
        """Test researcher user permissions"""
        researcher_user = Mock()
        researcher_user.role = UserRole.RESEARCHER.value

        assert check_user_permissions(researcher_user, UserRole.ADMIN) is False
        assert check_user_permissions(researcher_user, UserRole.RESEARCHER) is True
        assert check_user_permissions(researcher_user, UserRole.VIEWER) is True

    def test_check_user_permissions_viewer(self):
        """Test viewer user permissions"""
        viewer_user = Mock()
        viewer_user.role = UserRole.VIEWER.value

        assert check_user_permissions(viewer_user, UserRole.ADMIN) is False
        assert check_user_permissions(viewer_user, UserRole.RESEARCHER) is False
        assert check_user_permissions(viewer_user, UserRole.VIEWER) is True


class TestUserOperations:
    """Test user database operations"""

    @patch('src.auth.SessionLocal')
    def test_get_user_by_username(self, mock_session):
        """Test getting user by username"""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch('src.auth.get_db', return_value=mock_db):
            result = get_user_by_username(mock_db, "testuser")

        assert result == mock_user
        mock_db.query.assert_called_once_with(User)
        mock_db.query.return_value.filter.assert_called_once()

    @patch('src.auth.SessionLocal')
    def test_get_user_by_email(self, mock_session):
        """Test getting user by email"""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch('src.auth.get_db', return_value=mock_db):
            result = get_user_by_email(mock_db, "test@example.com")

        assert result == mock_user

    @patch('src.auth.SessionLocal')
    def test_authenticate_user_success(self, mock_session):
        """Test successful user authentication"""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        mock_user.hashed_password = hash_password("testpass")
        mock_user.is_active = True

        with patch('src.auth.get_user_by_username', return_value=mock_user), \
             patch('src.auth.verify_password', return_value=True), \
             patch('src.auth.get_db', return_value=mock_db):

            result = authenticate_user(mock_db, "testuser", "testpass")

        assert result == mock_user

    @patch('src.auth.SessionLocal')
    def test_authenticate_user_wrong_password(self, mock_session):
        """Test user authentication with wrong password"""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        mock_user.hashed_password = hash_password("testpass")

        with patch('src.auth.get_user_by_username', return_value=mock_user), \
             patch('src.auth.verify_password', return_value=False), \
             patch('src.auth.get_db', return_value=mock_db):

            result = authenticate_user(mock_db, "testuser", "wrongpass")

        assert result is None

    @patch('src.auth.SessionLocal')
    def test_authenticate_user_not_found(self, mock_session):
        """Test user authentication with non-existent user"""
        mock_db = Mock(spec=Session)

        with patch('src.auth.get_user_by_username', return_value=None), \
             patch('src.auth.get_db', return_value=mock_db):

            result = authenticate_user(mock_db, "nonexistent", "testpass")

        assert result is None

    @patch('src.auth.SessionLocal')
    def test_create_user(self, mock_session):
        """Test user creation"""
        mock_db = Mock(spec=Session)
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role=UserRole.RESEARCHER
        )

        with patch('src.auth.hash_password', return_value="hashedpass"), \
             patch('src.auth.generate_api_key', return_value="testkey"), \
             patch('src.auth.hash_api_key', return_value="hashedkey"), \
             patch('src.auth.get_db', return_value=mock_db):

            result = create_user(mock_db, user_data)

        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called_once()

    @patch('src.auth.SessionLocal')
    def test_update_user_password(self, mock_session):
        """Test password update"""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)

        with patch('src.auth.hash_password', return_value="newhashedpass"), \
             patch('src.auth.get_db', return_value=mock_db):

            update_user_password(mock_db, mock_user, "newpassword")

        assert mock_user.hashed_password == "newhashedpass"
        mock_db.commit.assert_called_once()


class TestUserModel:
    """Test User model validation"""

    def test_user_create_validation(self):
        """Test UserCreate model validation"""
        # Valid user
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="validpassword123",
            role=UserRole.RESEARCHER
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.RESEARCHER

    def test_user_create_password_validation(self):
        """Test password length validation"""
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="short",  # Too short
                role=UserRole.RESEARCHER
            )

    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.RESEARCHER.value == "researcher"
        assert UserRole.VIEWER.value == "viewer"