"""
ISA SuperApp Test Configuration and Fixtures
===========================================

This module provides shared fixtures and configuration for all tests in the ISA SuperApp project.
It includes database setup, API clients, mock services, and other testing utilities.
"""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from _pytest.config import Config
from _pytest.monkeypatch import MonkeyPatch

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def pytest_configure(config: Config) -> None:
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "flaky: mark test as flaky (may fail intermittently)"
    )
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring external API access"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database access"
    )
    config.addinivalue_line("markers", "requires_redis: mark test as requiring Redis")
    config.addinivalue_line(
        "markers", "requires_chroma: mark test as requiring ChromaDB"
    )


def pytest_collection_modifyitems(config: Config, items: List[pytest.Item]) -> None:
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)


# Environment Configuration
@pytest.fixture(scope="session")
def test_env_vars() -> Dict[str, str]:
    """Provide test environment variables."""
    return {
        "TESTING": "true",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/15",  # Use database 15 for tests
        "CHROMA_PERSIST_DIRECTORY": tempfile.mkdtemp(prefix="chroma_test_"),
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GEMINI_API_KEY": "test-gemini-key",
        "VECTOR_STORE_TYPE": "memory",
        "CACHE_TYPE": "memory",
        "ENABLE_TELEMETRY": "false",
        "ENABLE_MONITORING": "false",
    }


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(
    test_env_vars: Dict[str, str], monkeypatch_session: MonkeyPatch
) -> None:
    """Set up test environment variables."""
    for key, value in test_env_vars.items():
        monkeypatch_session.setenv(key, value)


@pytest.fixture(scope="session")
def monkeypatch_session() -> Generator[MonkeyPatch, None, None]:
    """Provide a session-scoped monkeypatch fixture."""
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


# Mock Services and Clients
@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Provide a mock OpenAI client."""
    mock = MagicMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test response"))]
    )
    mock.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1] * 1536)]
    )
    return mock


@pytest.fixture
def mock_anthropic_client() -> MagicMock:
    """Provide a mock Anthropic client."""
    mock = MagicMock()
    mock.messages.create.return_value = MagicMock(content="Test response")
    return mock


@pytest.fixture
def mock_chroma_client() -> MagicMock:
    """Provide a mock ChromaDB client."""
    mock = MagicMock()
    mock.get_or_create_collection.return_value = MagicMock(
        add=MagicMock(),
        query=MagicMock(return_value={"documents": [["test"]], "metadatas": [[{}]]}),
        get=MagicMock(return_value={"documents": ["test"], "metadatas": [{}]}),
    )
    return mock


@pytest.fixture
def mock_redis_client() -> MagicMock:
    """Provide a mock Redis client."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    mock.flushdb.return_value = True
    return mock


# Database Fixtures
@pytest.fixture(scope="session")
async def test_database() -> AsyncGenerator[Any, None]:
    """Provide a test database session."""
    # This would typically set up a test database
    # For now, we'll use an in-memory SQLite database
    from sqlalchemy import create_engine
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    # Create async engine for SQLite
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create tables
    async with engine.begin() as conn:
        # Import and create your models here
        # await conn.run_sync(Base.metadata.create_all)
        pass

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
async def db_session(test_database: Any) -> AsyncGenerator[Any, None]:
    """Provide a database session for each test."""
    yield test_database
    await test_database.rollback()


# API Test Client
@pytest.fixture
async def test_client() -> AsyncGenerator[Any, None]:
    """Provide a test client for the FastAPI application."""
    from fastapi.testclient import TestClient

    # Import your FastAPI app here
    # from isa_superapp.api.app import app
    # with TestClient(app) as client:
    #     yield client
    yield None


# Vector Store Fixtures
@pytest.fixture
def mock_vector_store() -> MagicMock:
    """Provide a mock vector store."""
    mock = MagicMock()
    mock.add_documents.return_value = ["doc1", "doc2"]
    mock.similarity_search.return_value = [
        MagicMock(page_content="Test content", metadata={"source": "test"})
    ]
    mock.delete.return_value = True
    return mock


# Cache Fixtures
@pytest.fixture
def mock_cache() -> MagicMock:
    """Provide a mock cache."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    mock.clear.return_value = True
    return mock


# File System Fixtures
@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_documents() -> List[Dict[str, Any]]:
    """Provide sample documents for testing."""
    return [
        {
            "content": "This is a test document about artificial intelligence.",
            "metadata": {"source": "test_doc_1", "category": "AI"},
        },
        {
            "content": "Machine learning is a subset of artificial intelligence.",
            "metadata": {"source": "test_doc_2", "category": "ML"},
        },
        {
            "content": "Deep learning uses neural networks.",
            "metadata": {"source": "test_doc_3", "category": "DL"},
        },
    ]


@pytest.fixture
def sample_query() -> str:
    """Provide a sample query for testing."""
    return "What is artificial intelligence?"


# Performance Testing Fixtures
@pytest.fixture(scope="session")
def performance_benchmark() -> Dict[str, Any]:
    """Provide performance benchmark configuration."""
    return {
        "max_response_time": 2.0,  # seconds
        "max_memory_usage": 100,  # MB
        "max_cpu_usage": 80,  # percentage
    }


# Error Handling Fixtures
@pytest.fixture
def mock_exception() -> Exception:
    """Provide a mock exception for testing error handling."""
    return Exception("Test exception")


@pytest.fixture
def mock_http_error() -> Exception:
    """Provide a mock HTTP error for testing."""
    from requests import HTTPError

    return HTTPError("404 Client Error: Not Found for url: http://example.com")


# Configuration Fixtures
@pytest.fixture
def app_config() -> Dict[str, Any]:
    """Provide application configuration for testing."""
    return {
        "app_name": "ISA SuperApp Test",
        "debug": True,
        "testing": True,
        "log_level": "DEBUG",
        "max_workers": 4,
        "timeout": 30,
        "retry_attempts": 3,
        "backoff_factor": 0.3,
    }


# Async Testing Utilities
@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Provide an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Monitoring and Telemetry Fixtures
@pytest.fixture
def mock_telemetry() -> MagicMock:
    """Provide a mock telemetry client."""
    mock = MagicMock()
    mock.track_event.return_value = None
    mock.track_metric.return_value = None
    mock.track_exception.return_value = None
    return mock


@pytest.fixture
def mock_metrics() -> MagicMock:
    """Provide a mock metrics collector."""
    mock = MagicMock()
    mock.increment.return_value = None
    mock.decrement.return_value = None
    mock.gauge.return_value = None
    mock.histogram.return_value = None
    mock.timing.return_value = None
    return mock


# Cleanup Fixtures
@pytest.fixture(autouse=True)
def cleanup_test_files() -> Generator[None, None, None]:
    """Clean up test files after each test."""
    yield
    # Clean up any test files created during testing
    test_dirs = [
        "data/cache/test_*",
        "data/vector_store/test_*",
        "logs/test_*",
    ]
    for pattern in test_dirs:
        for path in Path(".").glob(pattern):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil

                shutil.rmtree(path, ignore_errors=True)


# Custom Assertions
class ISAAssertions:
    """Custom assertions for ISA SuperApp tests."""

    @staticmethod
    def assert_valid_document(document: Dict[str, Any]) -> None:
        """Assert that a document has valid structure."""
        assert "content" in document, "Document must have content"
        assert isinstance(document["content"], str), "Document content must be string"
        assert len(document["content"]) > 0, "Document content cannot be empty"

        if "metadata" in document:
            assert isinstance(
                document["metadata"], dict
            ), "Document metadata must be dict"

    @staticmethod
    def assert_valid_query(query: str) -> None:
        """Assert that a query is valid."""
        assert isinstance(query, str), "Query must be string"
        assert len(query.strip()) > 0, "Query cannot be empty"
        assert len(query) <= 1000, "Query too long (max 1000 characters)"

    @staticmethod
    def assert_valid_embedding(embedding: List[float]) -> None:
        """Assert that an embedding is valid."""
        assert isinstance(embedding, list), "Embedding must be list"
        assert len(embedding) > 0, "Embedding cannot be empty"
        assert all(
            isinstance(x, (int, float)) for x in embedding
        ), "Embedding must contain numbers"
        assert all(
            -1 <= x <= 1 for x in embedding
        ), "Embedding values must be normalized"


@pytest.fixture
def isa_assertions() -> ISAAssertions:
    """Provide custom assertions for tests."""
    return ISAAssertions()


# Performance Monitoring
@pytest.fixture(scope="session")
def performance_monitor() -> Generator[Any, None, None]:
    """Monitor performance during test execution."""
    import os
    import time

    import psutil

    start_time = time.time()
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / 1024 / 1024  # MB

    yield

    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB

    execution_time = end_time - start_time
    memory_usage = end_memory - start_memory

    logger.info(
        f"Test session performance: {execution_time:.2f}s, {memory_usage:.2f}MB"
    )


# Test Data Generators
@pytest.fixture
def document_generator() -> Any:
    """Provide a document generator for testing."""

    def generate_documents(count: int = 10) -> List[Dict[str, Any]]:
        """Generate test documents."""
        documents = []
        for i in range(count):
            documents.append(
                {
                    "content": f"Test document {i+1} content about various topics.",
                    "metadata": {
                        "source": f"test_doc_{i+1}",
                        "category": f"category_{(i % 3) + 1}",
                        "timestamp": f"2024-01-{i+1:02d}T10:00:00Z",
                    },
                }
            )
        return documents

    return generate_documents


# Export commonly used fixtures for easy import
__all__ = [
    "test_env_vars",
    "mock_openai_client",
    "mock_anthropic_client",
    "mock_chroma_client",
    "mock_redis_client",
    "test_database",
    "db_session",
    "test_client",
    "mock_vector_store",
    "mock_cache",
    "temp_dir",
    "sample_documents",
    "sample_query",
    "performance_benchmark",
    "mock_exception",
    "mock_http_error",
    "app_config",
    "event_loop",
    "mock_telemetry",
    "mock_metrics",
    "isa_assertions",
    "performance_monitor",
    "document_generator",
]
