"""
Neo4j GDS Configuration Module for ISA Supply Chain Analytics

This module provides configuration management for Neo4j Graph Data Science
integration with ISA's supply chain analytics system.

Configuration includes:
- Database connection settings
- GDS algorithm parameters
- Graph projection configurations
- Performance tuning options
- Environment-specific settings
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .neo4j_gds_client import Neo4jConfig, GDSConfig

logger = logging.getLogger(__name__)


class Neo4jGDSConfiguration:
    """
    Configuration manager for Neo4j GDS integration.

    Handles loading configuration from environment variables,
    configuration files, and provides defaults for all settings.
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv("NEO4J_GDS_CONFIG_FILE")
        self._config = {}
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load configuration from environment variables and config file."""
        # Load from environment variables first
        self._config = self._load_from_environment()

        # Override with config file if provided
        if self.config_file and Path(self.config_file).exists():
            file_config = self._load_from_file(self.config_file)
            self._config.update(file_config)

        logger.info("Neo4j GDS configuration loaded successfully")

    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "neo4j": {
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "username": os.getenv("NEO4J_USERNAME", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "neo4j_password"),
                "database": os.getenv("NEO4J_DATABASE", "neo4j"),
                "max_connection_pool_size": int(os.getenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "50")),
                "connection_timeout": float(os.getenv("NEO4J_CONNECTION_TIMEOUT", "30.0")),
                "max_retry_time": float(os.getenv("NEO4J_MAX_RETRY_TIME", "30.0")),
                "retry_delay": float(os.getenv("NEO4J_RETRY_DELAY", "1.0"))
            },
            "gds": {
                "graph_name": os.getenv("GDS_GRAPH_NAME", "supply-chain-graph"),
                "concurrency": int(os.getenv("GDS_CONCURRENCY", "4")),
                "memory_limit": os.getenv("GDS_MEMORY_LIMIT", "4G"),
                "read_concurrency": int(os.getenv("GDS_READ_CONCURRENCY", "4")),
                "write_concurrency": int(os.getenv("GDS_WRITE_CONCURRENCY", "4"))
            },
            "ingestion": {
                "batch_size": int(os.getenv("GDS_INGESTION_BATCH_SIZE", "1000")),
                "max_workers": int(os.getenv("GDS_INGESTION_MAX_WORKERS", "4")),
                "enable_validation": os.getenv("GDS_ENABLE_VALIDATION", "true").lower() == "true",
                "enable_progress_tracking": os.getenv("GDS_ENABLE_PROGRESS_TRACKING", "true").lower() == "true",
                "retry_failed_batches": os.getenv("GDS_RETRY_FAILED_BATCHES", "true").lower() == "true",
                "max_retries": int(os.getenv("GDS_MAX_RETRIES", "3")),
                "retry_delay": float(os.getenv("GDS_RETRY_DELAY", "1.0")),
                "enable_incremental_updates": os.getenv("GDS_ENABLE_INCREMENTAL_UPDATES", "true").lower() == "true",
                "ingestion_timeout": float(os.getenv("GDS_INGESTION_TIMEOUT", "3600.0"))
            },
            "analytics": {
                "enable_caching": os.getenv("GDS_ENABLE_ANALYTICS_CACHING", "true").lower() == "true",
                "cache_ttl": int(os.getenv("GDS_ANALYTICS_CACHE_TTL", "3600")),
                "max_parallel_algorithms": int(os.getenv("GDS_MAX_PARALLEL_ALGORITHMS", "3")),
                "algorithm_timeout": float(os.getenv("GDS_ALGORITHM_TIMEOUT", "300.0"))
            },
            "monitoring": {
                "enable_metrics": os.getenv("GDS_ENABLE_METRICS", "true").lower() == "true",
                "metrics_prefix": os.getenv("GDS_METRICS_PREFIX", "neo4j_gds"),
                "health_check_interval": int(os.getenv("GDS_HEALTH_CHECK_INTERVAL", "60"))
            }
        }

    def _load_from_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_file}")
            return file_config
        except ImportError:
            logger.warning("PyYAML not available, skipping file configuration")
            return {}
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {e}")
            return {}

    def get_neo4j_config(self) -> Neo4jConfig:
        """Get Neo4j configuration object."""
        neo4j_config = self._config.get("neo4j", {})
        return Neo4jConfig(
            uri=neo4j_config.get("uri", "bolt://localhost:7687"),
            username=neo4j_config.get("username", "neo4j"),
            password=neo4j_config.get("password", "neo4j_password"),
            database=neo4j_config.get("database", "neo4j"),
            max_connection_pool_size=neo4j_config.get("max_connection_pool_size", 50),
            connection_timeout=neo4j_config.get("connection_timeout", 30.0),
            max_retry_time=neo4j_config.get("max_retry_time", 30.0),
            retry_delay=neo4j_config.get("retry_delay", 1.0)
        )

    def get_gds_config(self) -> GDSConfig:
        """Get GDS configuration object."""
        gds_config = self._config.get("gds", {})
        return GDSConfig(
            graph_name=gds_config.get("graph_name", "supply-chain-graph"),
            concurrency=gds_config.get("concurrency", 4),
            memory_limit=gds_config.get("memory_limit", "4G"),
            read_concurrency=gds_config.get("read_concurrency", 4),
            write_concurrency=gds_config.get("write_concurrency", 4)
        )

    def get_ingestion_config(self) -> Dict[str, Any]:
        """Get ingestion configuration."""
        return self._config.get("ingestion", {})

    def get_analytics_config(self) -> Dict[str, Any]:
        """Get analytics configuration."""
        return self._config.get("analytics", {})

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self._config.get("monitoring", {})

    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration."""
        return self._config.copy()

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        def update_nested_dict(base_dict: Dict[str, Any], updates: Dict[str, Any]) -> None:
            for key, value in updates.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    update_nested_dict(base_dict[key], value)
                else:
                    base_dict[key] = value

        update_nested_dict(self._config, updates)
        logger.info("Configuration updated")

    def save_config(self, config_file: Optional[str] = None) -> bool:
        """Save current configuration to file."""
        save_file = config_file or self.config_file
        if not save_file:
            logger.error("No config file specified for saving")
            return False

        try:
            import yaml
            with open(save_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
            logger.info(f"Configuration saved to {save_file}")
            return True
        except ImportError:
            logger.warning("PyYAML not available, cannot save configuration")
            return False
        except Exception as e:
            logger.error(f"Failed to save configuration to {save_file}: {e}")
            return False


# Global configuration instance
_gds_configuration: Optional[Neo4jGDSConfiguration] = None


def get_gds_configuration(config_file: Optional[str] = None) -> Neo4jGDSConfiguration:
    """Get or create the global GDS configuration instance."""
    global _gds_configuration

    if _gds_configuration is None:
        _gds_configuration = Neo4jGDSConfiguration(config_file)

    return _gds_configuration


def initialize_gds_configuration(config_file: Optional[str] = None) -> Neo4jGDSConfiguration:
    """
    Initialize the global GDS configuration instance.

    Args:
        config_file: Optional path to configuration file

    Returns:
        Initialized configuration instance
    """
    global _gds_configuration

    _gds_configuration = Neo4jGDSConfiguration(config_file)
    return _gds_configuration


# Default configuration values for easy reference
DEFAULT_CONFIG = {
    "neo4j": {
        "uri": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "neo4j_password",
        "database": "neo4j",
        "max_connection_pool_size": 50,
        "connection_timeout": 30.0,
        "max_retry_time": 30.0,
        "retry_delay": 1.0
    },
    "gds": {
        "graph_name": "supply-chain-graph",
        "concurrency": 4,
        "memory_limit": "4G",
        "read_concurrency": 4,
        "write_concurrency": 4
    },
    "ingestion": {
        "batch_size": 1000,
        "max_workers": 4,
        "enable_validation": True,
        "enable_progress_tracking": True,
        "retry_failed_batches": True,
        "max_retries": 3,
        "retry_delay": 1.0,
        "enable_incremental_updates": True,
        "ingestion_timeout": 3600.0
    },
    "analytics": {
        "enable_caching": True,
        "cache_ttl": 3600,
        "max_parallel_algorithms": 3,
        "algorithm_timeout": 300.0
    },
    "monitoring": {
        "enable_metrics": True,
        "metrics_prefix": "neo4j_gds",
        "health_check_interval": 60
    }
}