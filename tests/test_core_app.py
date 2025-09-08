"""
Tests for the core ISA SuperApp functionality.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from isa_superapp.core.app import ISASuperApp, create_app
from isa_superapp.core.config import Config
from isa_superapp.core.exceptions import ConfigurationError, ISAError
from isa_superapp.core.models import Document, SearchQuery, Task, TaskType


class TestISASuperApp:
    """Test cases for ISASuperApp class."""

    @pytest.fixture
    async def app(self):
        """Create a test app instance."""
        config = Config(
            vector_store={"provider": "memory", "collection_name": "test_collection"},
            llm={"provider": "mock", "model": "test-model"},
        )
        app = ISASuperApp(config)
        yield app
        await app.shutdown()

    @pytest.mark.asyncio
    async def test_app_initialization(self, app):
        """Test app initialization."""
        assert app.config is not None
        assert app.vector_store is not None
        assert app.llm_provider is not None
        assert app.agent_system is not None
        assert app.workflow_engine is not None

    @pytest.mark.asyncio
    async def test_app_start_stop(self, app):
        """Test app start and stop functionality."""
        await app.start()
        assert app.is_running is True

        await app.shutdown()
        assert app.is_running is False

    @pytest.mark.asyncio
    async def test_create_app_with_config_file(self):
        """Test creating app with configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_data = {
                "vector_store": {"provider": "memory", "collection_name": "test"},
                "llm": {"provider": "mock", "model": "test-model"},
            }
            import yaml

            yaml.dump(config_data, f)
            f.flush()

            app = await create_app(f.name)
            assert app.config.vector_store.provider == "memory"
            await app.shutdown()

            Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_create_app_with_invalid_config(self):
        """Test creating app with invalid configuration."""
        with pytest.raises(ConfigurationError):
            await create_app("nonexistent_config.yaml")

    @pytest.mark.asyncio
    async def test_index_document(self, app):
        """Test document indexing."""
        document = Document(
            title="Test Document",
            content="This is a test document for indexing.",
            source="test_source",
            collection="test_collection",
        )

        doc_id = await app.index_document(document)
        assert doc_id is not None
        assert isinstance(doc_id, str)

    @pytest.mark.asyncio
    async def test_search_documents(self, app):
        """Test document search functionality."""
        # First index a document
        document = Document(
            title="Machine Learning Paper",
            content="This paper discusses machine learning algorithms and their applications.",
            source="test_source",
            collection="test_collection",
        )
        await app.index_document(document)

        # Then search for it
        query = SearchQuery(
            query="machine learning algorithms", limit=10, threshold=0.5
        )

        results = await app.search_documents(query)
        assert isinstance(results, list)
        assert len(results) > 0

        # Check result structure
        result = results[0]
        assert "content" in result
        assert "score" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_execute_task(self, app):
        """Test task execution."""
        task = Task(
            type=TaskType.RESEARCH,
            query="Analyze machine learning trends",
            priority="medium",
            context={"domain": "technology"},
        )

        task_id = await app.execute_task(task)
        assert task_id is not None
        assert isinstance(task_id, str)

    @pytest.mark.asyncio
    async def test_get_task_result(self, app):
        """Test getting task results."""
        # Create and execute a task
        task = Task(
            type=TaskType.ANALYSIS, query="Simple analysis task", priority="low"
        )
        task_id = await app.execute_task(task)

        # Get the result
        result = await app.get_task_result(task_id)
        assert result is not None
        assert result.task_id == task_id
        assert result.status in ["pending", "running", "completed", "failed"]

    @pytest.mark.asyncio
    async def test_get_task_status(self, app):
        """Test getting task status."""
        task = Task(type=TaskType.SEARCH, query="test query", priority="low")
        task_id = await app.execute_task(task)

        status = await app.get_task_status(task_id)
        assert status in ["pending", "running", "completed", "failed"]

    @pytest.mark.asyncio
    async def test_list_tasks(self, app):
        """Test listing tasks."""
        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = Task(
                type=TaskType.RESEARCH, query=f"Research task {i}", priority="medium"
            )
            task_id = await app.execute_task(task)
            tasks.append(task_id)

        # List all tasks
        all_tasks = await app.list_tasks()
        assert len(all_tasks) >= 3

        # List tasks with filters
        research_tasks = await app.list_tasks(task_type=TaskType.RESEARCH)
        assert len(research_tasks) >= 3

    @pytest.mark.asyncio
    async def test_cancel_task(self, app):
        """Test task cancellation."""
        task = Task(
            type=TaskType.RESEARCH, query="Long running research task", priority="low"
        )
        task_id = await app.execute_task(task)

        # Cancel the task
        success = await app.cancel_task(task_id)
        assert success is True

        # Verify task is cancelled
        status = await app.get_task_status(task_id)
        assert status == "cancelled"

    @pytest.mark.asyncio
    async def test_health_check(self, app):
        """Test health check functionality."""
        health = await app.health_check()
        assert isinstance(health, dict)
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_get_metrics(self, app):
        """Test metrics retrieval."""
        metrics = await app.get_metrics()
        assert isinstance(metrics, dict)
        # Should contain basic metrics
        assert len(metrics) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, app):
        """Test error handling in various scenarios."""
        # Test with invalid task type
        with pytest.raises(ISAError):
            task = Task(
                type="invalid_type",  # Invalid task type
                query="test query",
                priority="low",
            )
            await app.execute_task(task)

        # Test with invalid document
        with pytest.raises(ISAError):
            invalid_doc = Document(
                title="",  # Empty title
                content="",  # Empty content
                source="",  # Empty source
            )
            await app.index_document(invalid_doc)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, app):
        """Test concurrent operations."""
        # Create multiple tasks concurrently
        tasks = []
        for i in range(5):
            task = Task(
                type=TaskType.SEARCH, query=f"concurrent search {i}", priority="low"
            )
            tasks.append(app.execute_task(task))

        # Execute all tasks concurrently
        task_ids = await asyncio.gather(*tasks)
        assert len(task_ids) == 5

        # Verify all tasks were created
        all_tasks = await app.list_tasks()
        assert len(all_tasks) >= 5


class TestCreateApp:
    """Test cases for create_app function."""

    @pytest.mark.asyncio
    async def test_create_app_default_config(self):
        """Test creating app with default configuration."""
        app = await create_app()
        assert app is not None
        assert isinstance(app, ISASuperApp)
        await app.shutdown()

    @pytest.mark.asyncio
    async def test_create_app_with_env_vars(self):
        """Test creating app with environment variables."""
        with patch.dict(
            "os.environ",
            {"ISA_VECTOR_STORE_PROVIDER": "memory", "ISA_LLM_PROVIDER": "mock"},
        ):
            app = await create_app()
            assert app is not None
            await app.shutdown()


class TestAppConfiguration:
    """Test app configuration scenarios."""

    @pytest.mark.asyncio
    async def test_app_with_different_vector_stores(self):
        """Test app with different vector store configurations."""
        configs = [
            {"provider": "memory", "collection_name": "test"},
            {"provider": "chroma", "collection_name": "test", "path": "/tmp/chroma"},
        ]

        for config in configs:
            app_config = Config(vector_store=config)
            app = ISASuperApp(app_config)
            assert app.vector_store is not None
            await app.shutdown()

    @pytest.mark.asyncio
    async def test_app_with_different_llm_providers(self):
        """Test app with different LLM providers."""
        configs = [
            {"provider": "mock", "model": "test-model"},
            {"provider": "openai", "model": "gpt-3.5-turbo", "api_key": "test-key"},
        ]

        for config in configs:
            app_config = Config(llm=config)
            app = ISASuperApp(app_config)
            assert app.llm_provider is not None
            await app.shutdown()
