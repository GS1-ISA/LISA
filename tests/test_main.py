"""
Tests for main application components.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from isa_superapp.core.config import ISAConfig
from isa_superapp.core.exceptions import ConfigurationError
from isa_superapp.main import ISASuperApp, create_app, main
from isa_superapp.orchestrator.base import TaskDefinition, TaskPriority, TaskStatus
from isa_superapp.retrieval.base import Document, SearchResult


class TestISASuperApp:
    """Test cases for the main ISA SuperApp class."""

    @pytest.fixture
    def app_instance(self):
        """Create an ISA SuperApp instance for testing."""
        config = ISAConfig(
            {
                "app": {"name": "TestApp", "debug": True},
                "vector_store": {"provider": "mock"},
                "orchestrator": {"max_workers": 2},
            }
        )
        return ISASuperApp(config)

    @pytest.fixture
    def mock_components(self, monkeypatch):
        """Mock external components."""
        # Mock vector store
        mock_vector_store = AsyncMock()
        monkeypatch.setattr(
            "isa_superapp.main.VectorStoreFactory.create",
            lambda provider, config: mock_vector_store,
        )

        # Mock orchestrator
        mock_orchestrator = AsyncMock()
        monkeypatch.setattr(
            "isa_superapp.main.Orchestrator", lambda config: mock_orchestrator
        )

        # Mock retrieval service
        mock_retrieval = AsyncMock()
        monkeypatch.setattr(
            "isa_superapp.main.RetrievalService",
            lambda vector_store, config: mock_retrieval,
        )

        return {
            "vector_store": mock_vector_store,
            "orchestrator": mock_orchestrator,
            "retrieval": mock_retrieval,
        }

    @pytest.mark.asyncio
    async def test_app_initialization(self, app_instance, mock_components):
        """Test app initialization."""
        await app_instance.initialize()

        # Verify components were initialized
        assert app_instance.vector_store is not None
        assert app_instance.orchestrator is not None
        assert app_instance.retrieval_service is not None

        # Verify components were called
        mock_components["vector_store"].initialize.assert_called_once()
        mock_components["orchestrator"].initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_app_shutdown(self, app_instance, mock_components):
        """Test app shutdown."""
        await app_instance.initialize()
        await app_instance.shutdown()

        # Verify components were shutdown
        mock_components["vector_store"].close.assert_called_once()
        mock_components["orchestrator"].shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_document(self, app_instance, mock_components):
        """Test storing a document."""
        await app_instance.initialize()

        document = {
            "id": "doc_123",
            "content": "Test document content",
            "metadata": {"source": "test", "author": "test_user"},
        }

        await app_instance.store_document(document)

        # Verify vector store was called
        mock_components["vector_store"].add_document.assert_called_once()
        call_args = mock_components["vector_store"].add_document.call_args[0][0]
        assert call_args.id == "doc_123"
        assert call_args.content == "Test document content"

    @pytest.mark.asyncio
    async def test_search_documents(self, app_instance, mock_components):
        """Test searching documents."""
        await app_instance.initialize()

        # Mock search results
        mock_results = [
            SearchResult(
                document=Document(
                    id="doc_1", content="Relevant content 1", metadata={"score": 0.9}
                ),
                score=0.9,
            ),
            SearchResult(
                document=Document(
                    id="doc_2", content="Relevant content 2", metadata={"score": 0.8}
                ),
                score=0.8,
            ),
        ]
        mock_components["retrieval"].search.return_value = mock_results

        results = await app_instance.search_documents("test query", limit=5)

        # Verify search was called
        mock_components["retrieval"].search.assert_called_once_with(
            query="test query", limit=5, filters=None
        )

        # Verify results
        assert len(results) == 2
        assert results[0].document.id == "doc_1"
        assert results[0].score == 0.9

    @pytest.mark.asyncio
    async def test_execute_task(self, app_instance, mock_components):
        """Test executing a task."""
        await app_instance.initialize()

        task_def = TaskDefinition(
            task_id="task_123",
            task_type="data_processing",
            parameters={"input_file": "test.csv", "output_format": "json"},
            priority=TaskPriority.MEDIUM,
        )

        # Mock task execution result
        mock_components["orchestrator"].submit_task.return_value = "task_123"
        mock_components[
            "orchestrator"
        ].get_task_status.return_value = TaskStatus.COMPLETED
        mock_components["orchestrator"].get_task_result.return_value = {
            "status": "success",
            "output_file": "output.json",
            "records_processed": 100,
        }

        result = await app_instance.execute_task(task_def)

        # Verify task was submitted
        mock_components["orchestrator"].submit_task.assert_called_once_with(task_def)

        # Verify result
        assert result["status"] == "success"
        assert result["output_file"] == "output.json"
        assert result["records_processed"] == 100

    @pytest.mark.asyncio
    async def test_get_task_status(self, app_instance, mock_components):
        """Test getting task status."""
        await app_instance.initialize()

        mock_components[
            "orchestrator"
        ].get_task_status.return_value = TaskStatus.RUNNING

        status = await app_instance.get_task_status("task_123")

        assert status == TaskStatus.RUNNING
        mock_components["orchestrator"].get_task_status.assert_called_once_with(
            "task_123"
        )

    @pytest.mark.asyncio
    async def test_list_tasks(self, app_instance, mock_components):
        """Test listing tasks."""
        await app_instance.initialize()

        mock_tasks = [
            {"task_id": "task_1", "status": "completed"},
            {"task_id": "task_2", "status": "running"},
        ]
        mock_components["orchestrator"].list_tasks.return_value = mock_tasks

        tasks = await app_instance.list_tasks(limit=10)

        assert len(tasks) == 2
        assert tasks[0]["task_id"] == "task_1"
        mock_components["orchestrator"].list_tasks.assert_called_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_health_check(self, app_instance, mock_components):
        """Test health check."""
        await app_instance.initialize()

        # Mock healthy components
        mock_components["vector_store"].health_check.return_value = {
            "status": "healthy"
        }
        mock_components["orchestrator"].health_check.return_value = {
            "status": "healthy"
        }

        health_status = await app_instance.health_check()

        assert health_status["status"] == "healthy"
        assert "vector_store" in health_status
        assert "orchestrator" in health_status
        assert health_status["vector_store"]["status"] == "healthy"
        assert health_status["orchestrator"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_with_unhealthy_component(
        self, app_instance, mock_components
    ):
        """Test health check with unhealthy component."""
        await app_instance.initialize()

        # Mock unhealthy vector store
        mock_components["vector_store"].health_check.return_value = {
            "status": "unhealthy",
            "error": "Connection failed",
        }
        mock_components["orchestrator"].health_check.return_value = {
            "status": "healthy"
        }

        health_status = await app_instance.health_check()

        assert health_status["status"] == "unhealthy"
        assert health_status["vector_store"]["status"] == "unhealthy"
        assert health_status["orchestrator"]["status"] == "healthy"


class TestCreateApp:
    """Test cases for create_app function."""

    @pytest.fixture
    def mock_config_manager(self, monkeypatch):
        """Mock config manager."""
        mock_manager = Mock()
        mock_manager.get_config.return_value = ISAConfig(
            {"app": {"name": "TestApp"}, "vector_store": {"provider": "chroma"}}
        )
        monkeypatch.setattr("isa_superapp.main.ConfigManager", lambda: mock_manager)
        return mock_manager

    @pytest.fixture
    def mock_isa_app(self, monkeypatch):
        """Mock ISA SuperApp instance."""
        mock_app = AsyncMock()
        monkeypatch.setattr("isa_superapp.main.ISASuperApp", lambda config: mock_app)
        return mock_app

    @pytest.mark.asyncio
    async def test_create_app_success(self, mock_config_manager, mock_isa_app):
        """Test successful app creation."""
        app = create_app()

        assert app is not None
        mock_config_manager.load_from_env_vars.assert_called_once()
        mock_isa_app.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_app_with_config_error(self, monkeypatch):
        """Test app creation with configuration error."""
        # Mock config manager to raise error
        mock_manager = Mock()
        mock_manager.load_from_env_vars.side_effect = ConfigurationError(
            "Invalid config"
        )
        monkeypatch.setattr("isa_superapp.main.ConfigManager", lambda: mock_manager)

        with pytest.raises(ConfigurationError):
            create_app()


class TestMainFunction:
    """Test cases for main function."""

    @pytest.fixture
    def mock_create_app(self, monkeypatch):
        """Mock create_app function."""
        mock_app = AsyncMock()
        monkeypatch.setattr("isa_superapp.main.create_app", lambda: mock_app)
        return mock_app

    @pytest.fixture
    def mock_uvicorn(self, monkeypatch):
        """Mock uvicorn run function."""
        mock_run = Mock()
        monkeypatch.setattr("isa_superapp.main.uvicorn.run", mock_run)
        return mock_run

    def test_main_function_success(self, mock_create_app, mock_uvicorn):
        """Test successful main function execution."""
        # Mock command line arguments
        with patch("sys.argv", ["isa_superapp", "--host", "0.0.0.0", "--port", "8000"]):
            main()

        # Verify uvicorn was called with correct parameters
        mock_uvicorn.assert_called_once()
        call_args = mock_uvicorn.call_args
        assert call_args.kwargs["host"] == "0.0.0.0"
        assert call_args.kwargs["port"] == 8000
        assert call_args.kwargs["app"] == mock_create_app

    def test_main_function_with_cli_args(self, mock_create_app, mock_uvicorn):
        """Test main function with various CLI arguments."""
        # Test with different arguments
        with patch("sys.argv", ["isa_superapp", "--reload", "--log-level", "debug"]):
            main()

        call_args = mock_uvicorn.call_args
        assert call_args.kwargs["reload"] is True
        assert call_args.kwargs["log_level"] == "debug"


class TestAppIntegration:
    """Integration tests for the main application."""

    @pytest.mark.asyncio
    async def test_full_document_lifecycle(self):
        """Test complete document storage and retrieval lifecycle."""
        # This would be a more comprehensive integration test
        # that tests the actual components working together
        # For now, we'll create a basic structure

        config = ISAConfig(
            {
                "app": {"name": "IntegrationTest", "debug": True},
                "vector_store": {
                    "provider": "memory"
                },  # Use in-memory store for testing
                "orchestrator": {"max_workers": 1},
            }
        )

        app = ISASuperApp(config)

        try:
            await app.initialize()

            # Store a document
            document = {
                "id": "integration_doc_1",
                "content": "This is a test document for integration testing",
                "metadata": {"test": True, "integration": True},
            }

            await app.store_document(document)

            # Search for the document
            results = await app.search_documents("integration testing")

            # Verify results
            assert len(results) > 0
            assert any(result.document.id == "integration_doc_1" for result in results)

        finally:
            await app.shutdown()

    @pytest.mark.asyncio
    async def test_task_execution_workflow(self):
        """Test complete task execution workflow."""
        config = ISAConfig(
            {
                "app": {"name": "TaskTest", "debug": True},
                "vector_store": {"provider": "memory"},
                "orchestrator": {"max_workers": 2},
            }
        )

        app = ISASuperApp(config)

        try:
            await app.initialize()

            # Create and execute a task
            task_def = TaskDefinition(
                task_id="integration_task_1",
                task_type="test_processing",
                parameters={"input": "test_data"},
                priority=TaskPriority.HIGH,
            )

            # Submit task
            result = await app.execute_task(task_def)

            # Verify task completed successfully
            assert result is not None
            assert "status" in result

            # Check task status
            status = await app.get_task_status("integration_task_1")
            assert status in [TaskStatus.COMPLETED, TaskStatus.RUNNING]

        finally:
            await app.shutdown()


class TestErrorHandling:
    """Test cases for error handling in main application."""

    @pytest.mark.asyncio
    async def test_initialization_with_missing_config(self):
        """Test initialization with missing configuration."""
        config = ISAConfig({})  # Empty config

        app = ISASuperApp(config)

        with pytest.raises(ConfigurationError):
            await app.initialize()

    @pytest.mark.asyncio
    async def test_store_document_with_invalid_data(
        self, app_instance, mock_components
    ):
        """Test storing document with invalid data."""
        await app_instance.initialize()

        # Invalid document (missing required fields)
        invalid_document = {"content": "Test content"}  # Missing 'id' field

        with pytest.raises(ValueError):
            await app_instance.store_document(invalid_document)

    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, app_instance, mock_components):
        """Test searching with empty query."""
        await app_instance.initialize()

        with pytest.raises(ValueError):
            await app_instance.search_documents("")

    @pytest.mark.asyncio
    async def test_execute_task_with_invalid_definition(
        self, app_instance, mock_components
    ):
        """Test executing task with invalid definition."""
        await app_instance.initialize()

        # Invalid task definition (missing required fields)
        invalid_task = TaskDefinition(
            task_id="",
            task_type="test",
            parameters={},  # Empty ID
        )

        with pytest.raises(ValueError):
            await app_instance.execute_task(invalid_task)
