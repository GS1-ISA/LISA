"""
Main ISA SuperApp application module.

This module provides the core application class that orchestrates
all components of the ISA SuperApp system.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent_system import AgentOrchestrator
from .api import APIServer
from .config import ConfigManager, ISAConfig, get_config
from .exceptions import ISAConfigurationError, ISAError, ISANotFoundError
from .logger import get_logger, setup_logging
from .models import Document, SearchQuery, Task, TaskStatus
from .vector_store import VectorStoreManager
from .workflow import WorkflowEngine


class ISASuperApp:
    """Main ISA SuperApp application class."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize ISA SuperApp.

        Args:
            config_path: Optional path to configuration file
        """
        self.logger = get_logger("isa_superapp")
        self.config_path = config_path
        self.config: Optional[ISAConfig] = None
        self.config_manager: Optional[ConfigManager] = None

        # Core components
        self.vector_store: Optional[VectorStoreManager] = None
        self.agent_orchestrator: Optional[AgentOrchestrator] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.api_server: Optional[APIServer] = None

        # Application state
        self.is_initialized = False
        self.is_running = False
        self.shutdown_event = asyncio.Event()

        # Setup signal handlers
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def initialize(self) -> None:
        """
        Initialize the application.

        This method initializes all core components and prepares
        the application for operation.
        """
        try:
            self.logger.info("Initializing ISA SuperApp...")

            # Load configuration
            await self._load_configuration()

            # Setup logging
            await self._setup_logging()

            # Initialize core components
            await self._initialize_vector_store()
            await self._initialize_agent_system()
            await self._initialize_workflow_engine()
            await self._initialize_api_server()

            self.is_initialized = True
            self.logger.info("ISA SuperApp initialization completed successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize ISA SuperApp: {e}")
            raise ISAError(f"Application initialization failed: {e}")

    async def _load_configuration(self) -> None:
        """Load application configuration."""
        self.logger.info("Loading configuration...")

        try:
            self.config_manager = get_config(self.config_path)
            self.config = self.config_manager.config

            # Validate configuration
            validation_errors = self.config_manager.validate()
            if validation_errors:
                raise ISAConfigurationError(
                    "Configuration validation failed", errors=validation_errors
                )

            self.logger.info(
                f"Configuration loaded successfully from {len(self.config_manager._metadata)} sources"
            )

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    async def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger.info("Setting up logging...")

        try:
            setup_logging(self.config.logging)
            self.logger.info("Logging setup completed")

        except Exception as e:
            self.logger.error(f"Failed to setup logging: {e}")
            raise

    async def _initialize_vector_store(self) -> None:
        """Initialize vector store manager."""
        self.logger.info("Initializing vector store...")

        try:
            self.vector_store = VectorStoreManager(self.config.vector_store)
            await self.vector_store.initialize()

            self.logger.info("Vector store initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize vector store: {e}")
            raise

    async def _initialize_agent_system(self) -> None:
        """Initialize agent orchestrator."""
        self.logger.info("Initializing agent system...")

        try:
            self.agent_orchestrator = AgentOrchestrator(
                self.config.agent, self.config.llm, self.vector_store
            )
            await self.agent_orchestrator.initialize()

            self.logger.info("Agent system initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize agent system: {e}")
            raise

    async def _initialize_workflow_engine(self) -> None:
        """Initialize workflow engine."""
        self.logger.info("Initializing workflow engine...")

        try:
            self.workflow_engine = WorkflowEngine(self.agent_orchestrator)
            await self.workflow_engine.initialize()

            self.logger.info("Workflow engine initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize workflow engine: {e}")
            raise

    async def _initialize_api_server(self) -> None:
        """Initialize API server."""
        self.logger.info("Initializing API server...")

        try:
            self.api_server = APIServer(
                self.config.api,
                self.agent_orchestrator,
                self.workflow_engine,
                self.vector_store,
            )

            self.logger.info("API server initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize API server: {e}")
            raise

    async def start(self) -> None:
        """
        Start the application.

        This method starts all running components and begins
        processing operations.
        """
        if not self.is_initialized:
            raise ISAError("Application must be initialized before starting")

        try:
            self.logger.info("Starting ISA SuperApp...")

            # Start API server
            if self.api_server:
                await self.api_server.start()

            # Start agent orchestrator
            if self.agent_orchestrator:
                await self.agent_orchestrator.start()

            # Start workflow engine
            if self.workflow_engine:
                await self.workflow_engine.start()

            self.is_running = True
            self.logger.info("ISA SuperApp started successfully")

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except Exception as e:
            self.logger.error(f"Failed to start ISA SuperApp: {e}")
            raise

    async def shutdown(self) -> None:
        """
        Shutdown the application.

        This method gracefully shuts down all components and
        cleans up resources.
        """
        self.logger.info("Shutting down ISA SuperApp...")

        try:
            # Stop API server
            if self.api_server and self.api_server.is_running:
                await self.api_server.stop()

            # Stop workflow engine
            if self.workflow_engine and self.workflow_engine.is_running:
                await self.workflow_engine.stop()

            # Stop agent orchestrator
            if self.agent_orchestrator and self.agent_orchestrator.is_running:
                await self.agent_orchestrator.stop()

            # Close vector store
            if self.vector_store:
                await self.vector_store.close()

            self.is_running = False
            self.shutdown_event.set()

            self.logger.info("ISA SuperApp shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise

    async def execute_task(self, task: Task) -> str:
        """
        Execute a task using the agent system.

        Args:
            task: Task to execute

        Returns:
            Task execution ID
        """
        if not self.is_initialized:
            raise ISAError("Application must be initialized")

        if not self.agent_orchestrator:
            raise ISAError("Agent orchestrator not available")

        return await self.agent_orchestrator.submit_task(task)

    async def execute_workflow(
        self, workflow_name: str, input_data: Dict[str, Any]
    ) -> str:
        """
        Execute a workflow.

        Args:
            workflow_name: Name of the workflow
            input_data: Input data for the workflow

        Returns:
            Workflow execution ID
        """
        if not self.is_initialized:
            raise ISAError("Application must be initialized")

        if not self.workflow_engine:
            raise ISAError("Workflow engine not available")

        return await self.workflow_engine.execute_workflow(workflow_name, input_data)

    async def search_documents(self, query: SearchQuery) -> List[Document]:
        """
        Search documents in the vector store.

        Args:
            query: Search query

        Returns:
            List of matching documents
        """
        if not self.is_initialized:
            raise ISAError("Application must be initialized")

        if not self.vector_store:
            raise ISAError("Vector store not available")

        return await self.vector_store.search(query)

    async def index_document(self, document: Document) -> str:
        """
        Index a document in the vector store.

        Args:
            document: Document to index

        Returns:
            Document ID
        """
        if not self.is_initialized:
            raise ISAError("Application must be initialized")

        if not self.vector_store:
            raise ISAError("Vector store not available")

        return await self.vector_store.index_document(document)

    def get_status(self) -> Dict[str, Any]:
        """
        Get application status.

        Returns:
            Application status information
        """
        status = {
            "initialized": self.is_initialized,
            "running": self.is_running,
            "version": self.config.app_version if self.config else "unknown",
            "environment": self.config.environment if self.config else "unknown",
            "components": {},
        }

        # Component status
        if self.vector_store:
            status["components"]["vector_store"] = self.vector_store.get_status()

        if self.agent_orchestrator:
            status["components"]["agent_orchestrator"] = (
                self.agent_orchestrator.get_status()
            )

        if self.workflow_engine:
            status["components"]["workflow_engine"] = self.workflow_engine.get_status()

        if self.api_server:
            status["components"]["api_server"] = self.api_server.get_status()

        return status

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health check results
        """
        health = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "checks": {},
        }

        # Check vector store
        if self.vector_store:
            try:
                vector_store_health = await self.vector_store.health_check()
                health["checks"]["vector_store"] = vector_store_health
            except Exception as e:
                health["checks"]["vector_store"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health["status"] = "unhealthy"

        # Check agent orchestrator
        if self.agent_orchestrator:
            try:
                agent_health = await self.agent_orchestrator.health_check()
                health["checks"]["agent_orchestrator"] = agent_health
            except Exception as e:
                health["checks"]["agent_orchestrator"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health["status"] = "unhealthy"

        # Check workflow engine
        if self.workflow_engine:
            try:
                workflow_health = await self.workflow_engine.health_check()
                health["checks"]["workflow_engine"] = workflow_health
            except Exception as e:
                health["checks"]["workflow_engine"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health["status"] = "unhealthy"

        return health


# Application factory
async def create_app(config_path: Optional[str] = None) -> ISASuperApp:
    """
    Create ISA SuperApp instance.

    Args:
        config_path: Optional configuration file path

    Returns:
        ISA SuperApp instance
    """
    app = ISASuperApp(config_path)
    await app.initialize()
    return app


async def run_app(config_path: Optional[str] = None) -> None:
    """
    Run ISA SuperApp.

    Args:
        config_path: Optional configuration file path
    """
    app = await create_app(config_path)

    try:
        await app.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)
    finally:
        await app.shutdown()


# CLI entry point
def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="ISA SuperApp")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument(
        "--create-config",
        type=str,
        help="Create default configuration file at specified path",
    )

    args = parser.parse_args()

    # Create configuration file if requested
    if args.create_config:
        from .config import create_default_config_file

        create_default_config_file(args.create_config)
        print(f"Default configuration file created at: {args.create_config}")
        return

    # Run application
    try:
        asyncio.run(run_app(args.config))
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
