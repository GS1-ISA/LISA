"""
ISA SuperApp Test Utilities
==========================

This module provides utility functions and helpers for testing the ISA SuperApp.
It includes functions for creating test data, mocking external services, and
performing common test operations.
"""

import asyncio
import json
import random
import string
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from faker import Faker

# Initialize Faker for generating test data
fake = Faker()


class TestDataGenerator:
    """Generate realistic test data for various scenarios."""

    @staticmethod
    def generate_documents(
        count: int = 10,
        min_length: int = 100,
        max_length: int = 1000,
        include_metadata: bool = True,
    ) -> List[Dict[str, Any]]:
        """Generate test documents with realistic content."""
        documents = []
        categories = ["AI", "ML", "DL", "NLP", "CV", "Robotics", "Data Science"]

        for i in range(count):
            content_length = random.randint(min_length, max_length)
            content = fake.text(max_nb_chars=content_length)

            document = {"content": content}

            if include_metadata:
                document["metadata"] = {
                    "source": f"test_doc_{i+1}",
                    "category": random.choice(categories),
                    "author": fake.name(),
                    "created_date": fake.date_time_this_year().isoformat(),
                    "tags": fake.words(nb=3),
                    "language": "en",
                }

            documents.append(document)

        return documents

    @staticmethod
    def generate_queries(count: int = 5) -> List[str]:
        """Generate realistic search queries."""
        query_templates = [
            "What is {topic}?",
            "How does {topic} work?",
            "Explain {topic} in simple terms.",
            "What are the applications of {topic}?",
            "Compare {topic} with {other_topic}.",
            "What are the benefits of {topic}?",
            "What are the challenges in {topic}?",
        ]

        topics = [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural networks",
            "natural language processing",
            "computer vision",
            "reinforcement learning",
            "data science",
            "big data",
            "cloud computing",
        ]

        queries = []
        for _ in range(count):
            template = random.choice(query_templates)
            topic = random.choice(topics)
            other_topic = random.choice([t for t in topics if t != topic])

            query = template.format(topic=topic, other_topic=other_topic)
            queries.append(query)

        return queries

    @staticmethod
    def generate_embeddings(
        count: int = 10,
        dimension: int = 1536,
        normalize: bool = True,
    ) -> List[List[float]]:
        """Generate random embeddings for testing."""
        embeddings = []

        for _ in range(count):
            # Generate random vector
            embedding = np.random.randn(dimension).tolist()

            if normalize:
                # Normalize to unit vector
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = (embedding / norm).tolist()

            embeddings.append(embedding)

        return embeddings

    @staticmethod
    def generate_metadata(count: int = 10) -> List[Dict[str, Any]]:
        """Generate realistic metadata for documents."""
        metadata_list = []

        for i in range(count):
            metadata = {
                "source": f"document_{i+1}",
                "title": fake.sentence(nb_words=6),
                "author": fake.name(),
                "created_date": fake.date_time_this_year().isoformat(),
                "modified_date": fake.date_time_this_month().isoformat(),
                "category": random.choice(
                    ["Technical", "Research", "Tutorial", "News"]
                ),
                "tags": fake.words(nb=random.randint(2, 5)),
                "language": random.choice(["en", "es", "fr", "de"]),
                "word_count": random.randint(100, 5000),
                "reading_time": random.randint(1, 20),
            }
            metadata_list.append(metadata)

        return metadata_list


class MockFactory:
    """Factory for creating mock objects and responses."""

    @staticmethod
    def create_openai_response(
        content: str = "Test response",
        model: str = "gpt-3.5-turbo",
        usage: Optional[Dict[str, int]] = None,
    ) -> MagicMock:
        """Create a mock OpenAI API response."""
        if usage is None:
            usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

        response = MagicMock()
        response.choices = [MagicMock(message=MagicMock(content=content))]
        response.model = model
        response.usage = MagicMock(**usage)

        return response

    @staticmethod
    def create_anthropic_response(
        content: str = "Test response",
        model: str = "claude-3-sonnet-20240229",
    ) -> MagicMock:
        """Create a mock Anthropic API response."""
        response = MagicMock()
        response.content = content
        response.model = model

        return response

    @staticmethod
    def create_embedding_response(
        embeddings: List[List[float]],
        model: str = "text-embedding-3-small",
    ) -> MagicMock:
        """Create a mock embedding API response."""
        response = MagicMock()
        response.data = [MagicMock(embedding=emb) for emb in embeddings]
        response.model = model

        return response

    @staticmethod
    def create_chroma_query_response(
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        distances: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Create a mock ChromaDB query response."""
        if distances is None:
            distances = [random.uniform(0.1, 0.9) for _ in documents]

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
            "ids": [[f"doc_{i}" for i in range(len(documents))]],
        }

    @staticmethod
    def create_http_response(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = "OK",
    ) -> MagicMock:
        """Create a mock HTTP response."""
        response = MagicMock()
        response.status_code = status_code
        response.text = text
        response.json.return_value = json_data or {}
        response.raise_for_status.return_value = None

        return response


class PerformanceMonitor:
    """Monitor performance metrics during tests."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None

    def start(self) -> None:
        """Start performance monitoring."""
        import os

        import psutil

        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        self.start_memory = process.memory_info().rss / 1024 / 1024  # MB

    def stop(self) -> Dict[str, float]:
        """Stop performance monitoring and return metrics."""
        import os

        import psutil

        self.end_time = time.time()
        process = psutil.Process(os.getpid())
        self.end_memory = process.memory_info().rss / 1024 / 1024  # MB

        return {
            "execution_time": self.end_time - self.start_time,
            "memory_usage": self.end_memory - self.start_memory,
            "peak_memory": self.end_memory,
        }


class AsyncTestHelpers:
    """Helpers for async testing."""

    @staticmethod
    async def run_with_timeout(coro: asyncio.Coroutine, timeout: float = 5.0) -> Any:
        """Run a coroutine with timeout."""
        return await asyncio.wait_for(coro, timeout=timeout)

    @staticmethod
    def create_async_mock(return_value: Any = None) -> AsyncMock:
        """Create an async mock."""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        return mock

    @staticmethod
    async def gather_with_concurrency(
        coros: List[asyncio.Coroutine],
        max_concurrent: int = 10,
    ) -> List[Any]:
        """Run coroutines with limited concurrency."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def sem_coro(coro: asyncio.Coroutine) -> Any:
            async with semaphore:
                return await coro

        return await asyncio.gather(*[sem_coro(coro) for coro in coros])


class TestValidators:
    """Validators for test data and results."""

    @staticmethod
    def validate_document(document: Dict[str, Any]) -> bool:
        """Validate document structure."""
        if not isinstance(document, dict):
            return False

        if "content" not in document:
            return False

        if not isinstance(document["content"], str):
            return False

        if len(document["content"].strip()) == 0:
            return False

        if "metadata" in document and not isinstance(document["metadata"], dict):
            return False

        return True

    @staticmethod
    def validate_embedding(embedding: List[float]) -> bool:
        """Validate embedding structure."""
        if not isinstance(embedding, list):
            return False

        if len(embedding) == 0:
            return False

        if not all(isinstance(x, (int, float)) for x in embedding):
            return False

        return True

    @staticmethod
    def validate_query_result(result: Dict[str, Any]) -> bool:
        """Validate query result structure."""
        required_keys = ["documents", "metadatas", "distances"]

        if not isinstance(result, dict):
            return False

        if not all(key in result for key in required_keys):
            return False

        # Check that all values are lists
        if not all(isinstance(result[key], list) for key in required_keys):
            return False

        # Check that all lists have the same length
        lengths = [len(result[key]) for key in required_keys]
        if len(set(lengths)) > 1:
            return False

        return True


# Context managers for testing
@contextmanager
def temp_env_vars(env_vars: Dict[str, str]) -> None:
    """Temporarily set environment variables."""
    original_vars = {}

    try:
        # Save original values
        for key, value in env_vars.items():
            original_vars[key] = os.environ.get(key)
            os.environ[key] = value

        yield

    finally:
        # Restore original values
        for key, value in original_vars.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@contextmanager
def mock_external_services() -> None:
    """Mock external services for testing."""
    with patch("openai.OpenAI") as mock_openai, patch(
        "anthropic.Anthropic"
    ) as mock_anthropic, patch("chromadb.PersistentClient") as mock_chroma, patch(
        "redis.Redis"
    ) as mock_redis:
        # Configure mocks
        mock_openai.return_value = MockFactory.create_openai_response()
        mock_anthropic.return_value = MockFactory.create_anthropic_response()
        mock_chroma.return_value = MagicMock()
        mock_redis.return_value = MagicMock()

        yield {
            "openai": mock_openai,
            "anthropic": mock_anthropic,
            "chroma": mock_chroma,
            "redis": mock_redis,
        }


# Utility functions
def create_test_file(
    content: str,
    filename: Optional[str] = None,
    directory: Optional[Path] = None,
) -> Path:
    """Create a temporary test file."""
    if directory is None:
        directory = Path(tempfile.mkdtemp())

    if filename is None:
        filename = f"test_{int(time.time())}.txt"

    file_path = directory / filename
    file_path.write_text(content)

    return file_path


def load_test_data(filename: str) -> Dict[str, Any]:
    """Load test data from JSON file."""
    test_data_dir = Path(__file__).parent / "data"
    file_path = test_data_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "r") as f:
        return json.load(f)


def save_test_data(data: Dict[str, Any], filename: str) -> None:
    """Save test data to JSON file."""
    test_data_dir = Path(__file__).parent / "data"
    test_data_dir.mkdir(exist_ok=True)

    file_path = test_data_dir / filename
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def generate_random_string(length: int = 10) -> str:
    """Generate a random string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """Generate a random email address."""
    return fake.email()


def generate_random_url() -> str:
    """Generate a random URL."""
    return fake.url()


# Performance testing functions
def measure_execution_time(func: Callable, *args, **kwargs) -> tuple[Any, float]:
    """Measure the execution time of a function."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()

    return result, end_time - start_time


async def measure_async_execution_time(
    coro: asyncio.Coroutine,
    *args,
    **kwargs,
) -> tuple[Any, float]:
    """Measure the execution time of an async function."""
    start_time = time.time()
    result = await coro(*args, **kwargs)
    end_time = time.time()

    return result, end_time - start_time


# Export commonly used utilities
__all__ = [
    "TestDataGenerator",
    "MockFactory",
    "PerformanceMonitor",
    "AsyncTestHelpers",
    "TestValidators",
    "temp_env_vars",
    "mock_external_services",
    "create_test_file",
    "load_test_data",
    "save_test_data",
    "generate_random_string",
    "generate_random_email",
    "generate_random_url",
    "measure_execution_time",
    "measure_async_execution_time",
]
