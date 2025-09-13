"""
Logging functionality for ISA SuperApp.

This module provides structured logging with JSON support, correlation IDs,
and integration with the configuration system.
"""

import json
import logging
import sys
import threading
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .config import ISAConfig, LogLevel
from .exceptions import ISAConfigurationError


class ISALogger:
    """
    Structured logger for ISA SuperApp.

    Provides enhanced logging capabilities including:
    - JSON formatted logs
    - Correlation ID tracking
    - Contextual information
    - Automatic error details
    """

    def __init__(self, name: str, config: Optional[ISAConfig] = None) -> None:
        """
        Initialize the logger.

        Args:
            name: Logger name (typically __name__)
            config: Configuration instance
        """
        self.name = name
        self.config = config or ISAConfig()
        self._logger = None
        self._context = threading.local()

        self._setup_logger()

    def _setup_logger(self) -> None:
        """Set up the underlying logger."""
        self._logger = logging.getLogger(self.name)

        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()

        # Set log level
        try:
            log_level = LogLevel(self.config.logging.level)
            self._logger.setLevel(getattr(logging, log_level.value))
        except (ValueError, AttributeError):
            self._logger.setLevel(logging.INFO)

        # Don't propagate to root logger
        self._logger.propagate = False

        # Add handlers
        if self.config.logging.enable_console:
            self._add_console_handler()

        if self.config.logging.enable_file:
            self._add_file_handler()

    def _add_console_handler(self) -> None:
        """Add console handler."""
        console_handler = logging.StreamHandler(sys.stdout)

        if self.config.logging.enable_json:
            formatter = ISAJSONFormatter()
        else:
            formatter = logging.Formatter(self.config.logging.format)

        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def _add_file_handler(self) -> None:
        """Add file handler."""
        log_file = Path(self.config.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.logging.max_file_size_mb * 1024 * 1024,
            backupCount=self.config.logging.backup_count,
            encoding="utf-8",
        )

        if self.config.logging.enable_json:
            formatter = ISAJSONFormatter()
        else:
            formatter = logging.Formatter(self.config.logging.format)

        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def set_correlation_id(self, correlation_id: str) -> None:
        """
        Set correlation ID for the current thread.

        Args:
            correlation_id: Unique identifier for request tracking
        """
        self._context.correlation_id = correlation_id

    def get_correlation_id(self) -> Optional[str]:
        """Get correlation ID for the current thread."""
        return getattr(self._context, "correlation_id", None)

    def clear_correlation_id(self) -> None:
        """Clear correlation ID for the current thread."""
        if hasattr(self._context, "correlation_id"):
            delattr(self._context, "correlation_id")

    def _log(
        self,
        level: int,
        message: str,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Internal logging method.

        Args:
            level: Log level
            message: Log message
            exc_info: Exception information
            extra: Additional structured data
            **kwargs: Additional keyword arguments
        """
        # Prepare extra data
        log_extra = extra or {}

        # Add correlation ID if available
        correlation_id = self.get_correlation_id()
        if correlation_id:
            log_extra["correlation_id"] = correlation_id

        # Add any additional kwargs to extra
        log_extra.update(kwargs)

        # Log the message
        if exc_info:
            self._logger.log(level, message, exc_info=True, extra=log_extra)
        else:
            self._logger.log(level, message, extra=log_extra)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(
        self, message: str, exc_info: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, exc_info=exc_info, **kwargs)

    def critical(
        self, message: str, exc_info: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, exc_info=exc_info, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._log(logging.ERROR, message, exc_info=True, **kwargs)

    def log_operation(
        self,
        operation: str,
        status: str,
        duration_ms: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Log operation with structured data.

        Args:
            operation: Operation name
            status: Operation status (success, failure, etc.)
            duration_ms: Operation duration in milliseconds
            **kwargs: Additional operation data
        """
        extra = {"operation": operation, "status": status, **kwargs}

        if duration_ms is not None:
            extra["duration_ms"] = duration_ms

        if status == "success":
            self.info(f"Operation completed: {operation}", extra=extra)
        elif status == "failure":
            self.error(f"Operation failed: {operation}", extra=extra)
        else:
            self.info(f"Operation {status}: {operation}", extra=extra)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_agent: Optional[str] = None,
        client_ip: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Log HTTP request with structured data.

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
            user_agent: User agent string
            client_ip: Client IP address
            **kwargs: Additional request data
        """
        extra = {
            "request_method": method,
            "request_path": path,
            "response_status": status_code,
            "duration_ms": duration_ms,
            **kwargs,
        }

        if user_agent:
            extra["user_agent"] = user_agent
        if client_ip:
            extra["client_ip"] = client_ip

        if status_code >= 500:
            self.error(f"Server error: {method} {path} -> {status_code}", extra=extra)
        elif status_code >= 400:
            self.warning(f"Client error: {method} {path} -> {status_code}", extra=extra)
        else:
            self.info(f"Request: {method} {path} -> {status_code}", extra=extra)

    def log_ai_operation(
        self,
        operation: str,
        model: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost_usd: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """
        Log AI operation with usage metrics.

        Args:
            operation: AI operation name
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_usd: Cost in USD
            **kwargs: Additional AI operation data
        """
        extra = {"ai_operation": operation, "model": model, **kwargs}

        if input_tokens is not None:
            extra["input_tokens"] = input_tokens
        if output_tokens is not None:
            extra["output_tokens"] = output_tokens
        if cost_usd is not None:
            extra["cost_usd"] = cost_usd

        self.info(f"AI operation: {operation} with {model}", extra=extra)


class ISAJSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # Add any additional attributes from the record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "extra_data",
            ]:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, separators=(",", ":"))


def get_logger(name: str, config: Optional[ISAConfig] = None) -> ISALogger:
    """
    Get logger instance.

    Args:
        name: Logger name (typically __name__)
        config: Configuration instance

    Returns:
        ISALogger instance
    """
    return ISALogger(name, config)


# Module-level logger
logger = get_logger(__name__)
