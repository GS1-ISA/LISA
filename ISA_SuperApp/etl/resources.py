"""
Dagster resources for ISA_D ETL system.

This module defines all external resources used by the ETL pipelines,
including database connections, API clients, and monitoring resources.
"""

import os
from typing import Any, Dict, Optional

from dagster import ConfigurableResource, InitResourceContext
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from ..core.logger import get_logger


class DatabaseResource(ConfigurableResource):
    """Database resource for ETL operations."""

    connection_string: str
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30

    def create_resource(self, context: InitResourceContext) -> Engine:
        """Create SQLAlchemy engine."""
        logger = get_logger("etl.database")

        try:
            engine = create_engine(
                self.connection_string,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_pre_ping=True,
                echo=False,
            )

            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                logger.info("Database connection established")

            return engine

        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise


class EurostatAPIResource(ConfigurableResource):
    """Eurostat API resource for data ingestion."""

    base_url: str = "https://ec.europa.eu/eurostat/api/dissemination"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

    def create_resource(self, context: InitResourceContext) -> Dict[str, Any]:
        """Create Eurostat API client configuration."""
        logger = get_logger("etl.eurostat_api")

        config = {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "headers": {
                "User-Agent": "ISA_D_ETL/1.0.0",
                "Accept": "application/json",
            },
        }

        logger.info("Eurostat API resource configured")
        return config


class ESMAApiResource(ConfigurableResource):
    """ESMA API resource for data ingestion."""

    base_url: str = "https://registers.esma.europa.eu"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

    def create_resource(self, context: InitResourceContext) -> Dict[str, Any]:
        """Create ESMA API client configuration."""
        logger = get_logger("etl.esma_api")

        config = {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "headers": {
                "User-Agent": "ISA_D_ETL/1.0.0",
                "Accept": "application/json",
            },
        }

        logger.info("ESMA API resource configured")
        return config


class MonitoringResource(ConfigurableResource):
    """Monitoring and alerting resource."""

    datadog_api_key: Optional[str] = None
    sentry_dsn: Optional[str] = None
    prometheus_gateway: Optional[str] = None

    def create_resource(self, context: InitResourceContext) -> Dict[str, Any]:
        """Create monitoring configuration."""
        logger = get_logger("etl.monitoring")

        config = {
            "datadog": {"api_key": self.datadog_api_key} if self.datadog_api_key else None,
            "sentry": {"dsn": self.sentry_dsn} if self.sentry_dsn else None,
            "prometheus": {"gateway": self.prometheus_gateway} if self.prometheus_gateway else None,
        }

        logger.info("Monitoring resource configured")
        return config


# Resource instances
database_resource = DatabaseResource(
    connection_string=os.getenv("DATABASE_URL", "sqlite:///./isa_etl.db")
)

eurostat_api_resource = EurostatAPIResource()

esma_api_resource = ESMAApiResource()

monitoring_resource = MonitoringResource(
    datadog_api_key=os.getenv("DATADOG_API_KEY"),
    sentry_dsn=os.getenv("SENTRY_DSN"),
    prometheus_gateway=os.getenv("PROMETHEUS_GATEWAY"),
)