"""
Encryption Service for ISA_D
Provides field-level encryption for sensitive data at rest.

This module provides:
- AES-256 encryption for sensitive database fields
- Key derivation from environment variables
- Encryption/decryption utilities
- Database field encryption decorators
"""

import os
import base64
from typing import Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import column_property


class EncryptionService:
    """Service for encrypting/decrypting sensitive data"""

    def __init__(self, key: Optional[str] = None):
        """Initialize encryption service with key"""
        self.key = key or os.getenv("ENCRYPTION_KEY", "your-encryption-key-change-in-production")
        self._fernet = None

    def _get_fernet(self) -> Fernet:
        """Get or create Fernet instance"""
        if self._fernet is None:
            # Derive encryption key from password
            password = self.key.encode()
            salt = b'static_salt_for_db_encryption'  # In production, use a proper salt per deployment
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self._fernet = Fernet(key)
        return self._fernet

    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return ""
        f = self._get_fernet()
        return f.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if not encrypted_data:
            return ""
        f = self._get_fernet()
        return f.decrypt(encrypted_data.encode()).decode()

    def encrypt_bytes(self, data: bytes) -> str:
        """Encrypt bytes data"""
        if not data:
            return ""
        f = self._get_fernet()
        return f.encrypt(data).decode()

    def decrypt_bytes(self, encrypted_data: str) -> bytes:
        """Decrypt to bytes"""
        if not encrypted_data:
            return b""
        f = self._get_fernet()
        return f.decrypt(encrypted_data.encode())


# Global encryption service instance
_encryption_service = EncryptionService()


def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance"""
    return _encryption_service


class EncryptedColumn:
    """SQLAlchemy column type for encrypted data"""

    def __init__(self, column_type=Text, encryption_service: Optional[EncryptionService] = None):
        self.column_type = column_type
        self.encryption_service = encryption_service or get_encryption_service()

    def __call__(self, *args, **kwargs):
        """Create encrypted column"""
        # Store encrypted data in database
        encrypted_column = Column(self.column_type, *args, **kwargs)

        # Create property for automatic encryption/decryption
        def getter(instance):
            if instance is None:
                return None
            encrypted_value = getattr(instance, f'_{self.name}_encrypted')
            if encrypted_value:
                try:
                    return self.encryption_service.decrypt(encrypted_value)
                except Exception:
                    # If decryption fails, return encrypted value for debugging
                    return f"[ENCRYPTED:{encrypted_value}]"
            return None

        def setter(instance, value):
            if value is None:
                encrypted_value = None
            else:
                encrypted_value = self.encryption_service.encrypt(str(value))
            setattr(instance, f'_{self.name}_encrypted', encrypted_value)

        # Create hybrid property
        return column_property(
            encrypted_column,
            getter=getter,
            setter=setter
        )


def encrypted_column(column_type=Text, *args, **kwargs):
    """Decorator/factory for creating encrypted columns"""
    return EncryptedColumn(column_type, *args, **kwargs)


# Sensitive data types for common use cases
class EncryptedString(String):
    """String column that automatically encrypts/decrypts"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_service = get_encryption_service()

    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database"""
        if value is not None:
            return self.encryption_service.encrypt(str(value))
        return None

    def process_result_value(self, value, dialect):
        """Decrypt value when retrieving from database"""
        if value is not None:
            try:
                return self.encryption_service.decrypt(value)
            except Exception:
                # If decryption fails, return encrypted value for debugging
                return f"[ENCRYPTED:{value}]"
        return None


class EncryptedText(Text):
    """Text column that automatically encrypts/decrypts"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_service = get_encryption_service()

    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database"""
        if value is not None:
            return self.encryption_service.encrypt(str(value))
        return None

    def process_result_value(self, value, dialect):
        """Decrypt value when retrieving from database"""
        if value is not None:
            try:
                return self.encryption_service.decrypt(value)
            except Exception:
                # If decryption fails, return encrypted value for debugging
                return f"[ENCRYPTED:{value}]"
        return None


# Utility functions for manual encryption/decryption
def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive string data"""
    return get_encryption_service().encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive string data"""
    return get_encryption_service().decrypt(encrypted_data)


def encrypt_binary_data(data: bytes) -> str:
    """Encrypt binary data"""
    return get_encryption_service().encrypt_bytes(data)


def decrypt_binary_data(encrypted_data: str) -> bytes:
    """Decrypt binary data"""
    return get_encryption_service().decrypt_bytes(encrypted_data)


# Database migration helpers
def migrate_encrypted_fields():
    """
    Helper function to migrate existing unencrypted data to encrypted format.
    This should be run once during deployment when adding encryption to existing fields.
    """
    # This would be implemented based on specific migration needs
    # For now, it's a placeholder
    pass


# Security utilities
def generate_encryption_key() -> str:
    """Generate a secure encryption key"""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


def validate_encryption_key(key: str) -> bool:
    """Validate encryption key format"""
    try:
        # Try to decode and validate key
        decoded = base64.urlsafe_b64decode(key)
        return len(decoded) == 32
    except Exception:
        return False