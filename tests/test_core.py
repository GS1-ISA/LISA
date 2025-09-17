"""
Tests for core components.
"""

import json
import logging

import pytest

from isa_superapp.core.config import (
    Config,
    ConfigManager,
)
from isa_superapp.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ISAError,
    OrchestrationError,
    ValidationError,
    VectorStoreError,
)
from isa_superapp.core.logging_config import get_logger, setup_logging
from isa_superapp.core.metrics import MetricsCollector
from isa_superapp.core.security import SecurityManager, decrypt_data, encrypt_data
from isa_superapp.core.validation import validate_config, validate_document


class TestConfig:
    """Test cases for configuration management."""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "app": {"name": "ISA_SuperApp", "version": "1.0.0", "debug": False},
            "vector_store": {
                "provider": "chroma",
                "collection_name": "isa_documents",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            },
            "orchestrator": {
                "max_workers": 4,
                "task_timeout": 300,
                "retry_attempts": 3,
            },
        }

    def test_config_initialization(self, sample_config):
        """Test configuration initialization."""
        config = Config(sample_config)

        assert config.get("app.name") == "ISA_SuperApp"
        assert config.get("app.version") == "1.0.0"
        assert config.get("vector_store.provider") == "chroma"
        assert config.get("nonexistent.key") is None

    def test_config_get_with_default(self, sample_config):
        """Test configuration get with default value."""
        config = Config(sample_config)

        assert config.get("app.debug", True) is False
        assert config.get("nonexistent.key", "default") == "default"

    def test_config_set_nested_value(self, sample_config):
        """Test setting nested configuration values."""
        config = Config(sample_config)

        config.set("new.section.key", "new_value")
        assert config.get("new.section.key") == "new_value"

    def test_config_update(self, sample_config):
        """Test configuration update."""
        config = Config(sample_config)

        updates = {"app.debug": True, "vector_store.provider": "pinecone"}
        config.update(updates)

        assert config.get("app.debug") is True
        assert config.get("vector_store.provider") == "pinecone"

    def test_config_validation(self, sample_config):
        """Test configuration validation."""
        config = Config(sample_config)

        # Valid configuration should not raise
        config.validate()

        # Invalid configuration should raise
        invalid_config = Config({"app": {"name": 123}})  # name should be string
        with pytest.raises(ConfigurationError):
            invalid_config.validate()


class TestConfigManager:
    """Test cases for configuration manager."""

    @pytest.fixture
    def config_manager(self):
        """Create a config manager instance."""
        return ConfigManager()

    def test_load_from_dict(self, config_manager, sample_config):
        """Test loading configuration from dictionary."""
        config_manager.load_from_dict(sample_config)

        config = config_manager.get_config()
        assert config.get("app.name") == "ISA_SuperApp"
        assert config.get("vector_store.provider") == "chroma"

    def test_load_from_file(self, config_manager, tmp_path):
        """Test loading configuration from file."""
        config_file = tmp_path / "config.json"
        config_data = {
            "app": {"name": "TestApp", "version": "1.0.0"},
            "database": {"host": "localhost", "port": 5432},
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config_manager.load_from_file(str(config_file))

        config = config_manager.get_config()
        assert config.get("app.name") == "TestApp"
        assert config.get("database.port") == 5432

    def test_load_from_env_vars(self, config_manager, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("ISA_APP_NAME", "EnvApp")
        monkeypatch.setenv("ISA_VECTOR_STORE_PROVIDER", "weaviate")
        monkeypatch.setenv("ISA_ORCHESTRATOR_MAX_WORKERS", "8")

        config_manager.load_from_env_vars()

        config = config_manager.get_config()
        assert config.get("app.name") == "EnvApp"
        assert config.get("vector_store.provider") == "weaviate"
        assert config.get("orchestrator.max_workers") == 8

    def test_merge_configs(self, config_manager):
        """Test merging multiple configurations."""
        base_config = {"app": {"name": "BaseApp", "debug": False}}
        override_config = {"app": {"debug": True}, "new_section": {"key": "value"}}

        merged = config_manager._merge_configs(base_config, override_config)

        assert merged["app"]["name"] == "BaseApp"
        assert merged["app"]["debug"] is True
        assert merged["new_section"]["key"] == "value"

    def test_get_with_fallback(self, config_manager):
        """Test getting configuration with fallback."""
        config_manager.load_from_dict({"app": {"name": "TestApp"}})

        # Should return existing value
        assert config_manager.get("app.name") == "TestApp"

        # Should return fallback for non-existent key
        assert config_manager.get("nonexistent.key", "fallback") == "fallback"


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_isa_error_base(self):
        """Test base ISA error."""
        error = ISAError("Test error message")
        assert str(error) == "Test error message"
        assert error.error_code is None  # ISAError doesn't set a default error_code

    def test_configuration_error(self):
        """Test configuration error."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert error.error_code == "CONFIG_ERROR"

    def test_vector_store_error(self):
        """Test vector store error."""
        error = VectorStoreError("Vector store connection failed")
        assert str(error) == "Vector store connection failed"
        assert error.error_code == "VECTOR_STORE_ERROR"

    def test_orchestration_error(self):
        """Test orchestration error."""
        error = OrchestrationError("Task execution failed")
        assert str(error) == "Task execution failed"
        assert error.error_code == "ORCHESTRATION_ERROR"

    def test_validation_error(self):
        """Test validation error."""
        error = ValidationError("Invalid input data", field="email")
        assert str(error) == "Invalid input data"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details.get("field") == "email"

    def test_authentication_error(self):
        """Test authentication error."""
        error = AuthenticationError("Invalid credentials")
        assert str(error) == "Invalid credentials"
        assert error.error_code == "AUTH_ERROR"

    def test_authorization_error(self):
        """Test authorization error."""
        error = AuthorizationError("Insufficient permissions")
        assert str(error) == "Insufficient permissions"
        assert error.error_code == "AUTHZ_ERROR"


class TestLoggingConfig:
    """Test cases for logging configuration."""

    def test_setup_logging_default(self):
        """Test setting up logging with default configuration."""
        logger = setup_logging()

        assert logger is not None
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logging_custom_level(self):
        """Test setting up logging with custom level."""
        logger = setup_logging(level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_setup_logging_with_file(self, tmp_path):
        """Test setting up logging with file handler."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file))

        # Write a test message
        logger.info("Test log message")

        # Verify file was created and contains the message
        assert log_file.exists()
        log_content = log_file.read_text()
        assert "Test log message" in log_content

    def test_get_logger(self):
        """Test getting a named logger."""
        logger = get_logger("test_module")

        assert logger.name == "test_module"
        assert logger.level == logging.INFO

    def test_get_logger_with_level(self):
        """Test getting a logger with custom level."""
        logger = get_logger("debug_module", level=logging.DEBUG)

        assert logger.name == "debug_module"
        assert logger.level == logging.DEBUG


class TestMetricsCollector:
    """Test cases for metrics collection."""

    @pytest.fixture
    def metrics_collector(self):
        """Create a metrics collector instance."""
        return MetricsCollector()

    def test_counter_metric(self, metrics_collector):
        """Test counter metric."""
        metrics_collector.increment("requests_total", labels={"method": "GET"})
        metrics_collector.increment("requests_total", labels={"method": "POST"})
        metrics_collector.increment("requests_total", labels={"method": "GET"})

        # Should have 2 GET requests and 1 POST request
        assert metrics_collector.get_metric("requests_total", {"method": "GET"}) == 2
        assert metrics_collector.get_metric("requests_total", {"method": "POST"}) == 1

    def test_gauge_metric(self, metrics_collector):
        """Test gauge metric."""
        metrics_collector.set_gauge("active_connections", 10, labels={"service": "api"})
        assert (
            metrics_collector.get_metric("active_connections", {"service": "api"}) == 10
        )

        metrics_collector.set_gauge("active_connections", 5, labels={"service": "api"})
        assert (
            metrics_collector.get_metric("active_connections", {"service": "api"}) == 5
        )

    def test_histogram_metric(self, metrics_collector):
        """Test histogram metric."""
        # Record some values
        for i in range(1, 6):  # 1, 2, 3, 4, 5
            metrics_collector.record_histogram(
                "request_duration", i, labels={"endpoint": "/api"}
            )

        # Get histogram statistics
        stats = metrics_collector.get_histogram_stats(
            "request_duration", {"endpoint": "/api"}
        )

        assert stats["count"] == 5
        assert stats["sum"] == 15
        assert stats["avg"] == 3.0
        assert stats["min"] == 1
        assert stats["max"] == 5

    def test_timer_metric(self, metrics_collector):
        """Test timer metric."""
        with metrics_collector.timer(
            "operation_duration", labels={"operation": "database_query"}
        ):
            # Simulate some work
            import time

            time.sleep(0.01)

        # Verify timer recorded something
        stats = metrics_collector.get_histogram_stats(
            "operation_duration", {"operation": "database_query"}
        )
        assert stats["count"] == 1
        assert stats["sum"] > 0  # Should have recorded some time

    def test_get_all_metrics(self, metrics_collector):
        """Test getting all metrics."""
        metrics_collector.increment("counter1")
        metrics_collector.set_gauge("gauge1", 42)
        metrics_collector.record_histogram("hist1", 10)

        all_metrics = metrics_collector.get_all_metrics()

        assert "counter1" in all_metrics
        assert "gauge1" in all_metrics
        assert "hist1" in all_metrics


class TestValidation:
    """Test cases for validation functions."""

    def test_validate_config_success(self):
        """Test successful configuration validation."""
        config = {
            "app": {"name": "TestApp", "version": "1.0.0"},
            "vector_store": {"provider": "chroma"},
        }

        # Should not raise any exception
        validate_config(config)

    def test_validate_config_missing_required(self):
        """Test configuration validation with missing required fields."""
        config = {"app": {"name": "TestApp"}}  # Missing version

        with pytest.raises(ValidationError):
            validate_config(config)

    def test_validate_config_invalid_type(self):
        """Test configuration validation with invalid types."""
        config = {"app": {"name": 123, "version": "1.0.0"}}  # name should be string

        with pytest.raises(ValidationError):
            validate_config(config)

    def test_validate_document_success(self):
        """Test successful document validation."""
        document = {
            "id": "doc_123",
            "content": "Test document content",
            "metadata": {"source": "test", "author": "test_user"},
        }

        # Should not raise any exception
        validate_document(document)

    def test_validate_document_missing_id(self):
        """Test document validation with missing ID."""
        document = {"content": "Test document content", "metadata": {"source": "test"}}

        with pytest.raises(ValidationError):
            validate_document(document)

    def test_validate_document_empty_content(self):
        """Test document validation with empty content."""
        document = {
            "id": "doc_123",
            "content": "",  # Empty content
            "metadata": {"source": "test"},
        }

        with pytest.raises(ValidationError):
            validate_document(document)


class TestSecurityManager:
    """Test cases for security manager."""

    @pytest.fixture
    def security_manager(self):
        """Create a security manager instance."""
        return SecurityManager(secret_key="test_secret_key_12345")

    def test_encrypt_decrypt_data(self, security_manager):
        """Test data encryption and decryption."""
        original_data = "Sensitive information"

        encrypted = security_manager.encrypt_data(original_data)
        decrypted = security_manager.decrypt_data(encrypted)

        assert encrypted != original_data
        assert decrypted == original_data

    def test_encrypt_decrypt_dict(self, security_manager):
        """Test encryption and decryption of dictionary data."""
        original_data = {
            "username": "test_user",
            "password": "secret_password",
            "api_key": "api_secret_123",
        }

        encrypted = security_manager.encrypt_data(original_data)
        decrypted = security_manager.decrypt_data(encrypted)

        assert encrypted != original_data
        assert decrypted == original_data

    def test_hash_password(self, security_manager):
        """Test password hashing."""
        password = "test_password_123"

        hashed = security_manager.hash_password(password)

        assert hashed != password
        assert security_manager.verify_password(password, hashed) is True
        assert security_manager.verify_password("wrong_password", hashed) is False

    def test_generate_token(self, security_manager):
        """Test token generation and validation."""
        payload = {"user_id": "123", "role": "admin"}

        token = security_manager.generate_token(payload)
        decoded = security_manager.validate_token(token)

        assert decoded["user_id"] == "123"
        assert decoded["role"] == "admin"

    def test_validate_expired_token(self, security_manager):
        """Test validation of expired token."""
        import time

        payload = {"user_id": "123"}

        # Generate token with very short expiration
        token = security_manager.generate_token(payload, expires_in=1)  # 1 second

        # Wait for token to expire
        time.sleep(2)

        # Should raise exception for expired token
        with pytest.raises(AuthenticationError):
            security_manager.validate_token(token)

    def test_validate_invalid_token(self, security_manager):
        """Test validation of invalid token."""
        with pytest.raises(AuthenticationError):
            security_manager.validate_token("invalid_token_string")


class TestSecurityFunctions:
    """Test cases for standalone security functions."""

    def test_encrypt_decrypt_data_function(self):
        """Test standalone encrypt/decrypt functions."""
        original_data = "Test data"
        secret_key = "test_secret_key_12345"

        encrypted = encrypt_data(original_data, secret_key)
        decrypted = decrypt_data(encrypted, secret_key)

        assert encrypted != original_data
        assert decrypted == original_data

    def test_encrypt_decrypt_with_invalid_key(self):
        """Test encryption/decryption with invalid key."""
        original_data = "Test data"
        secret_key = "test_secret_key_12345"
        wrong_key = "wrong_secret_key_67890"

        encrypted = encrypt_data(original_data, secret_key)

        # Should raise exception with wrong key
        with pytest.raises(ValueError):
            decrypt_data(encrypted, wrong_key)
