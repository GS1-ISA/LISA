"""
Centralized path constants for ISA_D project
This module contains commonly used database URLs and path constants
"""

# Database URL constants for different environments and purposes
DATABASE_URLS = {
    "MEMORY": "sqlite:///:memory:",  # In-memory SQLite for testing
    "TEST": "sqlite:///test.db",     # Test database file
    "AUTH": "sqlite:///./isa_auth.db",     # Authentication database
    "AUDIT": "sqlite:///./isa_audit.db",   # Audit logging database
    "MAIN": "sqlite:///./isa.db"          # Main application database
}

# Default database URL for backward compatibility
DEFAULT_DATABASE_URL = DATABASE_URLS["AUTH"]
