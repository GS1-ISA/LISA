"""
Validation utilities for ISA SuperApp.
"""

from typing import Any

from .exceptions import ValidationError


def validate_config(config: dict[str, Any]) -> None:
    """Validate configuration dictionary."""
    if not isinstance(config, dict):
        raise ValidationError("Configuration must be a dictionary")

    # Basic validation - check for required top-level keys
    required_keys = ["app"]
    for key in required_keys:
        if key not in config:
            raise ValidationError(f"Missing required configuration key: {key}")

    # Validate app section
    if "app" in config:
        app_config = config["app"]
        if not isinstance(app_config, dict):
            raise ValidationError("app configuration must be a dictionary")

        if "name" in app_config and not isinstance(app_config["name"], str):
            raise ValidationError("app.name must be a string")

        if "version" in app_config and not isinstance(app_config["version"], str):
            raise ValidationError("app.version must be a string")


def validate_document(document: dict[str, Any]) -> None:
    """Validate document dictionary."""
    if not isinstance(document, dict):
        raise ValidationError("Document must be a dictionary")

    # Check for required fields
    required_fields = ["id", "content"]
    for field in required_fields:
        if field not in document:
            raise ValidationError(f"Missing required document field: {field}")

    # Validate field types
    if not isinstance(document["id"], str):
        raise ValidationError("Document id must be a string")

    if not isinstance(document["content"], str):
        raise ValidationError("Document content must be a string")

    if len(document["content"].strip()) == 0:
        raise ValidationError("Document content cannot be empty")

    # Validate metadata if present
    if "metadata" in document and not isinstance(document["metadata"], dict):
        raise ValidationError("Document metadata must be a dictionary")
