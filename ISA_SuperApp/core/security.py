"""
Security utilities for ISA SuperApp.
"""

import hashlib
import secrets
from typing import Any

from cryptography.fernet import Fernet


class SecurityManager:
    """Manages security operations."""

    def __init__(self, secret_key: str):
        """Initialize security manager."""
        self.secret_key = secret_key
        self.cipher = Fernet(secret_key.encode())

    def encrypt_data(self, data: Any) -> str:
        """Encrypt data."""
        if isinstance(data, dict) or not isinstance(data, str):
            data = str(data)

        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        salt = secrets.token_hex(16)
        return hashlib.sha256((password + salt).encode()).hexdigest() + salt

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        if len(hashed) < 64:
            return False
        salt = hashed[64:]
        return hashlib.sha256((password + salt).encode()).hexdigest() + salt == hashed

    def generate_token(self, payload: dict[str, Any], expires_in: int = 3600) -> str:
        """Generate a secure token."""
        # Stub implementation
        return secrets.token_urlsafe(32)

    def validate_token(self, token: str) -> dict[str, Any]:
        """Validate a token."""
        # Stub implementation
        return {"user_id": "123", "role": "user"}


def encrypt_data(data: Any, secret_key: str) -> str:
    """Encrypt data with a secret key."""
    cipher = Fernet(secret_key.encode())
    if isinstance(data, dict) or not isinstance(data, str):
        data = str(data)
    return cipher.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str, secret_key: str) -> str:
    """Decrypt data with a secret key."""
    cipher = Fernet(secret_key.encode())
    return cipher.decrypt(encrypted_data.encode()).decode()
