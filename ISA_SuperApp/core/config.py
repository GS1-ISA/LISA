"""
Configuration management for ISA SuperApp.

This module provides centralized configuration management with support
for environment variables, configuration files, and runtime updates.
"""

import enum
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import yaml

from .exceptions import ISAConfigurationError, ISAValidationError
from .logger import get_logger

T = TypeVar("T")


class ConfigSource(enum.Enum):
    """Configuration source types."""

    ENVIRONMENT = "environment"
    FILE = "file"
    DEFAULT = "default"
    RUNTIME = "runtime"


class ConfigLevel(enum.Enum):
    """Configuration levels."""

    SYSTEM = "system"
    APPLICATION = "application"
    MODULE = "module"
    USER = "user"


@dataclass
class ConfigMetadata:
    """Configuration metadata."""

    source: ConfigSource
    level: ConfigLevel
    timestamp: datetime
    file_path: Optional[str] = None
    environment_variable: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Database configuration."""

    host: str = "localhost"
    port: int = 5432
    database: str = "isa_superapp"
    username: str = "isa_user"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"
    connection_timeout: int = 30

    def get_connection_string(self) -> str:
        """Get database connection string."""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?sslmode={self.ssl_mode}"
        )


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""

    provider: str = "chroma"
    collection_name: str = "isa_documents"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    distance_metric: str = "cosine"
    max_results: int = 100
    similarity_threshold: float = 0.7
    chunk_size: int = 1000
    chunk_overlap: int = 200
    batch_size: int = 100

    # Chroma-specific settings
    chroma_path: str = "./data/chroma"
    chroma_persistent: bool = True

    # Pinecone-specific settings
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "isa-superapp"

    # Weaviate-specific settings
    weaviate_url: str = "http://localhost:8080"
    weaviate_class_name: str = "Document"


@dataclass
class LLMConfig:
    """LLM configuration."""

    provider: str = "openai"
    model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3
    retry_delay: int = 1

    # OpenAI-specific settings
    openai_api_key: str = ""
    openai_organization: str = ""
    openai_base_url: str = ""

    # Anthropic-specific settings
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"

    # Google-specific settings
    google_api_key: str = ""
    google_model: str = "gemini-pro"

    # Local model settings
    local_model_path: str = ""
    local_model_device: str = "cpu"
    local_model_quantize: bool = False


@dataclass
class AgentConfig:
    """Agent system configuration."""

    max_agents: int = 10
    max_tasks_per_agent: int = 5
    agent_timeout: int = 300
    agent_retry_count: int = 3
    agent_retry_delay: int = 1

    # Agent types configuration
    enable_research_agents: bool = True
    enable_analysis_agents: bool = True
    enable_document_agents: bool = True
    enable_search_agents: bool = True

    # Agent capabilities
    research_agent_model: str = "gpt-4"
    analysis_agent_model: str = "gpt-4"
    document_agent_model: str = "gpt-4"
    search_agent_model: str = "gpt-4"


@dataclass
class WorkflowConfig:
    """Workflow configuration."""

    max_concurrent_executions: int = 5
    execution_timeout: int = 3600  # 1 hour
    step_timeout: int = 300  # 5 minutes
    retry_failed_steps: bool = True
    max_step_retries: int = 3
    retry_delay: int = 5

    # Workflow storage
    workflow_storage_path: str = "./data/workflows"
    execution_history_retention_days: int = 30

    # Workflow templates
    enable_default_templates: bool = True
    template_refresh_interval: int = 3600  # 1 hour


@dataclass
class APIConfig:
    """API configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 1
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 60

    # Security settings
    enable_auth: bool = True
    auth_token_expiry: int = 3600  # 1 hour
    rate_limit_per_minute: int = 100
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

    # SSL settings
    enable_ssl: bool = False
    ssl_cert_path: str = ""
    ssl_key_path: str = ""


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "./logs/isa_superapp.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True

    # Structured logging
    enable_structured_logging: bool = False
    structured_format: str = "json"

    # Performance logging
    enable_performance_logging: bool = True
    performance_log_interval: int = 60  # seconds


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    enable_metrics: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"

    enable_health_checks: bool = True
    health_check_interval: int = 30  # seconds

    enable_tracing: bool = False
    tracing_endpoint: str = "http://localhost:14268/api/traces"
    tracing_sample_rate: float = 0.1

    # Alerting
    enable_alerts: bool = False
    alert_webhook_url: str = ""
    alert_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security configuration."""

    enable_encryption: bool = True
    encryption_key: str = ""

    # API security
    api_key_header: str = "X-API-Key"
    api_key_required: bool = True

    # Data security
    encrypt_sensitive_data: bool = True
    data_retention_days: int = 90

    # Access control
    enable_rbac: bool = True
    default_user_role: str = "user"
    admin_role: str = "admin"


@dataclass
class ISAConfig:
    """Main ISA SuperApp configuration."""

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Application settings
    app_name: str = "ISA SuperApp"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    # Data paths
    data_path: str = "./data"
    models_path: str = "./models"
    logs_path: str = "./logs"
    temp_path: str = "./temp"

    # Feature flags
    enable_experimental_features: bool = False
    enable_beta_features: bool = False

    # Metadata
    metadata: Dict[str, ConfigMetadata] = field(default_factory=dict)


class ConfigManager:
    """Configuration manager for ISA SuperApp."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger("config.manager")
        self.config_path = config_path or self._find_config_file()
        self.config = ISAConfig()
        self._config_cache: Dict[str, Any] = {}
        self._metadata: Dict[str, ConfigMetadata] = {}

        # Load configuration
        self._load_configuration()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        search_paths = [
            "./config.yaml",
            "./config.yml",
            "./config.json",
            "~/.isa_superapp/config.yaml",
            "~/.isa_superapp/config.yml",
            "~/.isa_superapp/config.json",
            "/etc/isa_superapp/config.yaml",
            "/etc/isa_superapp/config.yml",
            "/etc/isa_superapp/config.json",
        ]

        for path in search_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                return str(expanded_path)

        return None

    def _load_configuration(self) -> None:
        """Load configuration from various sources."""
        # Load from file if available
        if self.config_path:
            self._load_from_file(self.config_path)

        # Load from environment variables
        self._load_from_environment()

        # Validate configuration
        self._validate_configuration()

        self.logger.info(f"Configuration loaded from {len(self._metadata)} sources")

    def _load_from_file(self, file_path: str) -> None:
        """Load configuration from file."""
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.warning(f"Configuration file not found: {file_path}")
                return

            with open(path, "r", encoding="utf-8") as f:
                if path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                elif path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    self.logger.warning(
                        f"Unsupported configuration file format: {path.suffix}"
                    )
                    return

            # Update configuration
            self._update_config_from_dict(data)

            # Record metadata
            timestamp = datetime.utcnow()
            for key in self._flatten_dict(data).keys():
                self._metadata[key] = ConfigMetadata(
                    source=ConfigSource.FILE,
                    level=ConfigLevel.APPLICATION,
                    timestamp=timestamp,
                    file_path=file_path,
                )

            self.logger.info(f"Configuration loaded from file: {file_path}")

        except Exception as e:
            self.logger.error(f"Error loading configuration from file {file_path}: {e}")
            raise ISAConfigurationError(
                f"Failed to load configuration from {file_path}: {e}"
            )

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            # Database
            "ISA_DB_HOST": ("database.host", str),
            "ISA_DB_PORT": ("database.port", int),
            "ISA_DB_NAME": ("database.database", str),
            "ISA_DB_USER": ("database.username", str),
            "ISA_DB_PASSWORD": ("database.password", str),
            # Vector Store
            "ISA_VECTOR_PROVIDER": ("vector_store.provider", str),
            "ISA_VECTOR_COLLECTION": ("vector_store.collection_name", str),
            "ISA_VECTOR_MODEL": ("vector_store.embedding_model", str),
            "ISA_VECTOR_DIMENSION": ("vector_store.embedding_dimension", int),
            "ISA_PINECONE_API_KEY": ("vector_store.pinecone_api_key", str),
            "ISA_PINECONE_ENV": ("vector_store.pinecone_environment", str),
            "ISA_WEAVIATE_URL": ("vector_store.weaviate_url", str),
            # LLM
            "ISA_LLM_PROVIDER": ("llm.provider", str),
            "ISA_LLM_MODEL": ("llm.model", str),
            "ISA_OPENAI_API_KEY": ("llm.openai_api_key", str),
            "ISA_ANTHROPIC_API_KEY": ("llm.anthropic_api_key", str),
            "ISA_GOOGLE_API_KEY": ("llm.google_api_key", str),
            # API
            "ISA_API_HOST": ("api.host", str),
            "ISA_API_PORT": ("api.port", int),
            "ISA_API_DEBUG": ("api.debug", bool),
            "ISA_SECRET_KEY": ("security.encryption_key", str),
            # Application
            "ISA_ENVIRONMENT": ("environment", str),
            "ISA_DEBUG": ("debug", bool),
            "ISA_DATA_PATH": ("data_path", str),
            "ISA_LOG_LEVEL": ("logging.level", str),
        }

        timestamp = datetime.utcnow()

        for env_var, (config_path, value_type) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = self._convert_value(os.environ[env_var], value_type)
                    self._set_nested_value(self.config, config_path, value)

                    self._metadata[config_path] = ConfigMetadata(
                        source=ConfigSource.ENVIRONMENT,
                        level=ConfigLevel.SYSTEM,
                        timestamp=timestamp,
                        environment_variable=env_var,
                    )

                except Exception as e:
                    self.logger.warning(f"Error loading {env_var}: {e}")

    def _update_config_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        for key, value in self._flatten_dict(data).items():
            self._set_nested_value(self.config, key, value)

    def _flatten_dict(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionary."""
        result = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten_dict(value, full_key))
            else:
                result[full_key] = value
        return result

    def _set_nested_value(self, obj: Any, path: str, value: Any) -> None:
        """Set nested value using dot notation."""
        keys = path.split(".")
        current = obj

        for key in keys[:-1]:
            if not hasattr(current, key):
                self.logger.warning(f"Configuration path not found: {path}")
                return
            current = getattr(current, key)

        if hasattr(current, keys[-1]):
            setattr(current, keys[-1], value)
        else:
            self.logger.warning(f"Configuration field not found: {path}")

    def _convert_value(self, value: str, value_type: Type[T]) -> T:
        """Convert string value to specified type."""
        if value_type == bool:
            return value.lower() in ("true", "1", "yes", "on")
        elif value_type == int:
            return int(value)
        elif value_type == float:
            return float(value)
        elif value_type == list:
            return [item.strip() for item in value.split(",")]
        else:
            return str(value)

    def _validate_configuration(self) -> None:
        """Validate configuration."""
        errors = []

        # Validate required fields
        if not self.config.database.host:
            errors.append("Database host is required")

        if not self.config.database.database:
            errors.append("Database name is required")

        if not self.config.llm.provider:
            errors.append("LLM provider is required")

        # Validate API keys for selected providers
        if self.config.llm.provider == "openai" and not self.config.llm.openai_api_key:
            errors.append("OpenAI API key is required when using OpenAI provider")

        if (
            self.config.llm.provider == "anthropic"
            and not self.config.llm.anthropic_api_key
        ):
            errors.append("Anthropic API key is required when using Anthropic provider")

        if self.config.llm.provider == "google" and not self.config.llm.google_api_key:
            errors.append("Google API key is required when using Google provider")

        # Validate vector store configuration
        if self.config.vector_store.provider == "pinecone":
            if not self.config.vector_store.pinecone_api_key:
                errors.append(
                    "Pinecone API key is required when using Pinecone vector store"
                )
            if not self.config.vector_store.pinecone_environment:
                errors.append(
                    "Pinecone environment is required when using Pinecone vector store"
                )

        if errors:
            raise ISAConfigurationError(
                "Configuration validation failed", errors=errors
            )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        try:
            keys = key.split(".")
            current = self.config

            for k in keys:
                if hasattr(current, k):
                    current = getattr(current, k)
                else:
                    return default

            return current
        except Exception as e:
            self.logger.warning(f"Error getting configuration key {key}: {e}")
            return default

    def set(
        self, key: str, value: Any, source: ConfigSource = ConfigSource.RUNTIME
    ) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key (dot notation)
            value: Value to set
            source: Configuration source
        """
        try:
            self._set_nested_value(self.config, key, value)

            # Update metadata
            self._metadata[key] = ConfigMetadata(
                source=source, level=ConfigLevel.RUNTIME, timestamp=datetime.utcnow()
            )

            self.logger.info(f"Configuration updated: {key}")

        except Exception as e:
            self.logger.error(f"Error setting configuration key {key}: {e}")
            raise ISAConfigurationError(f"Failed to set configuration {key}: {e}")

    def get_metadata(self, key: str) -> Optional[ConfigMetadata]:
        """
        Get configuration metadata.

        Args:
            key: Configuration key

        Returns:
            Configuration metadata
        """
        return self._metadata.get(key)

    def save_to_file(self, file_path: str, format: str = "yaml") -> None:
        """
        Save configuration to file.

        Args:
            file_path: Output file path
            format: File format (yaml or json)
        """
        try:
            data = asdict(self.config)

            # Remove metadata and other non-serializable fields
            data.pop("metadata", None)

            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                if format.lower() == "yaml":
                    yaml.safe_dump(data, f, default_flow_style=False)
                elif format.lower() == "json":
                    json.dump(data, f, indent=2)
                else:
                    raise ValueError(f"Unsupported format: {format}")

            self.logger.info(f"Configuration saved to {file_path}")

        except Exception as e:
            self.logger.error(f"Error saving configuration to {file_path}: {e}")
            raise ISAConfigurationError(f"Failed to save configuration: {e}")

    def reload(self) -> None:
        """Reload configuration from sources."""
        self.logger.info("Reloading configuration...")
        self._load_configuration()

    def validate(self) -> List[str]:
        """
        Validate current configuration.

        Returns:
            List of validation errors
        """
        errors = []

        try:
            self._validate_configuration()
        except ISAConfigurationError as e:
            errors = e.errors if hasattr(e, "errors") else [str(e)]

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self.config)

    def __str__(self) -> str:
        """String representation."""
        return f"ISAConfig(environment={self.config.environment}, version={self.config.app_version})"


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get global configuration manager.

    Args:
        config_path: Optional configuration file path

    Returns:
        Configuration manager instance
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager(config_path)

    return _config_manager


def create_default_config_file(file_path: str, format: str = "yaml") -> None:
    """
    Create a default configuration file.

    Args:
        file_path: Output file path
        format: File format (yaml or json)
    """
    config = ISAConfig()
    manager = ConfigManager()
    manager.config = config
    manager.save_to_file(file_path, format)


# Environment-specific configuration helpers
def get_development_config() -> ISAConfig:
    """Get development configuration."""
    config = ISAConfig()
    config.environment = "development"
    config.debug = True
    config.logging.level = "DEBUG"
    config.api.debug = True
    config.enable_experimental_features = True
    return config


def get_production_config() -> ISAConfig:
    """Get production configuration."""
    config = ISAConfig()
    config.environment = "production"
    config.debug = False
    config.logging.level = "INFO"
    config.api.debug = False
    config.enable_experimental_features = False
    config.security.enable_encryption = True
    config.monitoring.enable_metrics = True
    config.monitoring.enable_health_checks = True
    return config


def get_testing_config() -> ISAConfig:
    """Get testing configuration."""
    config = ISAConfig()
    config.environment = "testing"
    config.debug = True
    config.logging.level = "DEBUG"
    config.api.debug = True
    config.database.database = "isa_superapp_test"
    config.vector_store.collection_name = "isa_documents_test"
    config.enable_experimental_features = True
    return config
