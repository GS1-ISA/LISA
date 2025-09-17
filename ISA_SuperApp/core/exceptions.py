"""
Exception classes for ISA SuperApp.

This module defines the base exception hierarchy for the ISA SuperApp framework.
All custom exceptions inherit from ISAException to provide consistent error handling.
"""

from typing import Any


class ISAException(Exception):
    """
    Base exception class for ISA SuperApp.

    All ISA-specific exceptions should inherit from this class to maintain
    consistency and provide common functionality across the framework.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary format for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """String representation of the exception."""
        return self.message

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"message='{self.message}', "
            f"error_code='{self.error_code}', "
            f"details={self.details}, "
            f"cause={self.cause})"
        )


class ISANotFoundError(ISAException):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize not found error."""
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        details.update(kwargs)

        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details,
        )


class ISAValidationError(ISAException):
    """
    Exception raised for validation errors.

    This exception is used when data validation fails, providing detailed
    information about what validation rules were violated.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        expected_type: str | None = None,
        validation_rule: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message describing the validation failure
            field: Field name that failed validation
            value: Value that failed validation
            expected_type: Expected type or format
            validation_rule: Specific validation rule that failed
            **kwargs: Additional details
        """
        details = {
            "field": field,
            "value": value,
            "expected_type": expected_type,
            "validation_rule": validation_rule,
            **kwargs,
        }
        # Remove None values
        details = {k: v for k, v in details.items() if v is not None}

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ISAConfigurationError(ISAException):
    """Exception raised for configuration-related errors."""

    def __init__(
        self, message: str, config_key: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize configuration error."""
        details = {"config_key": config_key, **kwargs} if config_key else kwargs
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details,
        )


class ISADataError(ISAException):
    """Exception raised for data-related errors."""

    def __init__(
        self, message: str, data_source: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize data error."""
        details = {"data_source": data_source, **kwargs} if data_source else kwargs
        super().__init__(
            message=message,
            error_code="DATA_ERROR",
            details=details,
        )


class ISANetworkError(ISAException):
    """Exception raised for network-related errors."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize network error."""
        details = {}
        if url:
            details["url"] = url
        if status_code:
            details["status_code"] = status_code
        details.update(kwargs)

        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            details=details,
        )


class ISAConnectionError(ISANetworkError):
    """Exception raised for connection-related errors."""

    def __init__(
        self,
        message: str,
        host: str | None = None,
        port: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize connection error."""
        details = {}
        if host:
            details["host"] = host
        if port is not None:
            details["port"] = port
        details.update(kwargs)

        super().__init__(
            message=message,
            error_code="CONNECTION_ERROR",
            details=details,
        )


class ISAAIError(ISAException):
    """Exception raised for AI/ML-related errors."""

    def __init__(
        self,
        message: str,
        model_name: str | None = None,
        error_type: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize AI error."""
        details = {}
        if model_name:
            details["model_name"] = model_name
        if error_type:
            details["error_type"] = error_type
        details.update(kwargs)

        super().__init__(
            message=message,
            error_code="AI_ERROR",
            details=details,
        )


class ISASecurityError(ISAException):
    """Exception raised for security-related errors."""

    def __init__(
        self, message: str, security_context: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize security error."""
        details = (
            {"security_context": security_context, **kwargs}
            if security_context
            else kwargs
        )
        super().__init__(
            message=message,
            error_code="SECURITY_ERROR",
            details=details,
        )


class ISATimeoutError(ISAException):
    """Exception raised for timeout errors."""

    def __init__(
        self,
        message: str,
        timeout_seconds: int | float | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize timeout error."""
        details = {}
        if timeout_seconds is not None:
            details["timeout_seconds"] = timeout_seconds
        if operation:
            details["operation"] = operation
        details.update(kwargs)

        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            details=details,
        )


class ISANotImplementedError(ISAException):
    """Exception raised for not implemented functionality."""

    def __init__(
        self, message: str, feature: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize not implemented error."""
        details = {"feature": feature, **kwargs} if feature else kwargs
        super().__init__(
            message=message,
            error_code="NOT_IMPLEMENTED_ERROR",
            details=details,
        )


class ISAResourceError(ISAException):
    """Exception raised for resource-related errors (memory, disk, etc.)."""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        requested_amount: int | float | None = None,
        available_amount: int | float | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize resource error."""
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if requested_amount is not None:
            details["requested_amount"] = requested_amount
        if available_amount is not None:
            details["available_amount"] = available_amount
        details.update(kwargs)

        super().__init__(
            message=message,
            error_code="RESOURCE_ERROR",
            details=details,
        )


class ISADependencyError(ISAException):
    """Exception raised for missing or incompatible dependencies."""

    def __init__(
        self,
        message: str,
        dependency_name: str | None = None,
        required_version: str | None = None,
        installed_version: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize dependency error."""
        details = {}
        if dependency_name:
            details["dependency_name"] = dependency_name
        if required_version:
            details["required_version"] = required_version
        if installed_version:
            details["installed_version"] = installed_version
        details.update(kwargs)

        super().__init__(
            message=message,
            error_code="DEPENDENCY_ERROR",
            details=details,
        )


class AuthenticationError(ISAException):
    """Exception raised for authentication-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize authentication error."""
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            details=kwargs,
        )


class LLMError(Exception):
    """Exception raised for LLM-related errors."""
    pass


class ConfigurationError(ISAException):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize configuration error."""
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=kwargs,
        )


class AgentError(ISAException):
    """Exception raised for agent-related errors."""

    def __init__(
        self, message: str, agent_id: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize agent error."""
        details = {"agent_id": agent_id, **kwargs} if agent_id else kwargs
        super().__init__(
            message=message,
            error_code="AGENT_ERROR",
            details=details,
        )


class AuthorizationError(ISAException):
    """Exception raised for authorization-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize authorization error."""
        super().__init__(
            message=message,
            error_code="AUTHZ_ERROR",
            details=kwargs,
        )


class LLMRateLimitError(Exception):
    """Exception raised for LLM rate limit errors."""
    pass


class LLMTimeoutError(Exception):
    """Exception raised for LLM timeout errors."""
    pass


class VectorStoreConnectionError(Exception):
    """Exception raised for vector store connection errors."""
    pass


class RetrievalError(Exception):
    """Exception raised for retrieval-related errors."""
    pass


class VectorStoreError(ISAException):
    """Exception raised for vector store-related errors."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize vector store error."""
        super().__init__(
            message=message,
            error_code="VECTOR_STORE_ERROR",
            details=kwargs,
        )


# Alias for backward compatibility
class ISAError(ISAException):
    """Alias for ISAException with default error code."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize ISA error with default error code."""
        super().__init__(
            message=message,
            error_code="ISA_ERROR",
            details=kwargs,
        )

ValidationError = ISAValidationError
class OrchestrationError(ISAException):
    """Exception raised for orchestration-related errors."""

    def __init__(
        self, message: str, orchestration_step: str | None = None, **kwargs: Any
    ) -> None:
        """Initialize orchestration error."""
        details = {"orchestration_step": orchestration_step, **kwargs} if orchestration_step else kwargs
        super().__init__(
            message=message,
            error_code="ORCHESTRATION_ERROR",
            details=details,
        )


# Alias for backward compatibility
ISAError = ISAException
