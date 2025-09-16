"""
Custom exceptions for ISA_D ETL system.

This module defines custom exception classes for the ETL system.
"""


class ISAETLError(Exception):
    """Base exception for ETL system errors."""
    pass


class ISAConfigurationError(ISAETLError):
    """Raised when there's a configuration error."""
    pass


class ISAValidationError(ISAETLError):
    """Raised when data validation fails."""
    pass


class ISANotFoundError(ISAETLError):
    """Raised when a required resource is not found."""
    pass


class ISAConnectionError(ISAETLError):
    """Raised when connection to external services fails."""
    pass


class ISATransformationError(ISAETLError):
    """Raised when data transformation fails."""
    pass


class ISAStorageError(ISAETLError):
    """Raised when data storage operations fail."""
    pass