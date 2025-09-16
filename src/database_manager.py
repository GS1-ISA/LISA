"""
Database Connection Manager with SQLAlchemy Connection Pooling

This module provides:
- Connection pooling for improved database performance
- Health monitoring and automatic recovery
- Optimal pool settings for ISA workloads
- Thread-safe session management
"""

import logging
import time
import threading
import hashlib
import json
from typing import Optional, Dict, Any
from contextlib import contextmanager

from sqlalchemy import create_engine, text, exc
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from .cache.multi_level_cache import get_multilevel_cache, MultiLevelCache

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """
    Database connection manager with pooling, health monitoring, and automatic recovery.

    Optimized for ISA workloads with high concurrency and research operations.
    """

    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 30,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
        health_check_interval: int = 60,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the database connection manager.

        Args:
            database_url: Database connection URL
            pool_size: Base pool size (20 for ISA workloads)
            max_overflow: Max additional connections beyond pool_size (30)
            pool_timeout: Seconds to wait for connection from pool (30)
            pool_recycle: Seconds before recycling connections (3600 = 1 hour)
            echo: Enable SQLAlchemy echo logging
            health_check_interval: Seconds between health checks (60)
            max_retries: Max retries for failed operations (3)
            retry_delay: Delay between retries in seconds (1.0)
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo
        self.health_check_interval = health_check_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._engine: Optional[Engine] = None
        self._session_maker: Optional[sessionmaker] = None
        self._health_monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._last_health_check = 0
        self._connection_failures = 0

        # Initialize multi-level cache for query results
        self.cache = get_multilevel_cache()

        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0

        # Initialize connection pool
        self._initialize_engine()

        # Start health monitoring
        self._start_health_monitoring()

    def _initialize_engine(self) -> None:
        """Initialize the SQLAlchemy engine with optimized pool settings."""
        try:
            self._engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=True,  # Check connections before use
                echo=self.echo,
                # Additional optimizations for ISA workloads
                pool_reset_on_return='rollback',  # Reset connections on return
                # isolation_level='READ_COMMITTED',  # SQLite doesn't support this isolation level
            )

            self._session_maker = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )

            logger.info(
                f"Database engine initialized with pool_size={self.pool_size}, "
                f"max_overflow={self.max_overflow}, pool_timeout={self.pool_timeout}s"
            )

        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise

    def _start_health_monitoring(self) -> None:
        """Start the background health monitoring thread."""
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True,
            name="DBHealthMonitor"
        )
        self._health_monitor_thread.start()
        logger.info("Database health monitoring started")

    def _health_monitor_loop(self) -> None:
        """Background loop for health monitoring."""
        while not self._stop_monitoring.is_set():
            try:
                current_time = time.time()
                if current_time - self._last_health_check >= self.health_check_interval:
                    self._perform_health_check()
                    self._last_health_check = current_time
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

            # Sleep for a shorter interval to be responsive to stop signals
            self._stop_monitoring.wait(min(10, self.health_check_interval))

    def _perform_health_check(self) -> None:
        """Perform a health check on the database connection pool."""
        try:
            with self._engine.connect() as conn:
                # Simple health check query
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

            # Reset failure counter on successful check
            if self._connection_failures > 0:
                logger.info(f"Database connection recovered after {self._connection_failures} failures")
                self._connection_failures = 0

        except Exception as e:
            self._connection_failures += 1
            logger.warning(f"Database health check failed (attempt {self._connection_failures}): {e}")

            # Attempt automatic recovery if failures persist
            if self._connection_failures >= 3:
                logger.error("Multiple connection failures detected, attempting recovery")
                self._attempt_recovery()

    def _attempt_recovery(self) -> None:
        """Attempt to recover from connection failures."""
        try:
            logger.info("Attempting database connection recovery")

            # Dispose of current engine
            if self._engine:
                self._engine.dispose()

            # Reinitialize engine
            self._initialize_engine()

            # Test the new connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()

            logger.info("Database connection recovery successful")
            self._connection_failures = 0

        except Exception as e:
            logger.error(f"Database recovery failed: {e}")
            # Don't reset failure counter on recovery failure

    def get_session(self) -> Session:
        """Get a database session with retry logic."""
        return self._execute_with_retry(self._session_maker)

    def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute an operation with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                if callable(operation):
                    return operation(*args, **kwargs)
                else:
                    return operation
            except (exc.DisconnectionError, exc.TimeoutError, exc.DatabaseError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    logger.warning(f"Database operation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Database operation failed after {self.max_retries} attempts: {e}")

        raise last_exception

    @contextmanager
    def session_scope(self):
        """Context manager for database sessions with automatic cleanup."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error, rolled back: {e}")
            raise
        finally:
            session.close()

    def execute_cached_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a SELECT query with multi-level caching."""
        # Generate cache key
        cache_key = self._generate_query_cache_key(query, params)

        # Try to get from cache
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.cache_hits += 1
            return cached_result

        # Cache miss - execute query
        self.cache_misses += 1
        result = self._execute_query(query, params)

        # Cache the result
        try:
            self.cache.set(cache_key, result)
        except Exception as e:
            logger.warning(f"Failed to cache query result: {e}")

        return result

    def _generate_query_cache_key(self, query: str, params: Optional[Dict[str, Any]]) -> str:
        """Generate a cache key for a query."""
        key_data = {
            'query': query.strip(),
            'params': params or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"db_query:{hashlib.sha256(key_string.encode()).hexdigest()}"

    def _execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query and return results."""
        with self.session_scope() as session:
            try:
                result = session.execute(text(query), params or {})
                return result.fetchall()
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get database cache statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'multilevel_cache_stats': self.cache.get_stats()
        }

    def get_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status."""
        if not self._engine:
            return {"status": "not_initialized"}

        pool = self._engine.pool

        # Note: pool.invalid() was removed in SQLAlchemy 2.0
        # Invalid connection tracking is now handled differently in the pool implementation
        # We track connection failures at the manager level instead

        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "checked_out": pool.checkedout(),
            "checked_in": pool.checkedin(),
            "overflow": pool.overflow(),
            "invalid": 0,  # Not available in SQLAlchemy 2.0 - tracked via connection_failures
            "total_connections": pool.size(),
            "available_connections": max(0, pool.size() - pool.checkedout()),
            "connection_failures": self._connection_failures,
            "last_health_check": self._last_health_check
        }

    def is_healthy(self) -> bool:
        """Check if the database connection is healthy."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def shutdown(self) -> None:
        """Shutdown the connection manager and cleanup resources."""
        logger.info("Shutting down database connection manager")

        # Stop health monitoring
        self._stop_monitoring.set()
        if self._health_monitor_thread and self._health_monitor_thread.is_alive():
            self._health_monitor_thread.join(timeout=5)

        # Dispose engine
        if self._engine:
            self._engine.dispose()
            self._engine = None

        logger.info("Database connection manager shutdown complete")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.shutdown()


# Global instance for application-wide use
_db_manager: Optional[DatabaseConnectionManager] = None


def get_db_manager(database_url: Optional[str] = None) -> DatabaseConnectionManager:
    """Get or create the global database manager instance."""
    global _db_manager

    if _db_manager is None:
        if database_url is None:
            import os
            database_url = os.getenv("DATABASE_URL", "sqlite:///./isa_auth.db")

        _db_manager = DatabaseConnectionManager(database_url)

    return _db_manager


def get_db_session() -> Session:
    """Get a database session from the global manager."""
    return get_db_manager().get_session()


@contextmanager
def get_db():
    """Context manager for database sessions with automatic cleanup."""
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()


def get_db_dependency() -> Session:
    """FastAPI dependency that returns a database session directly."""
    return get_db_session()