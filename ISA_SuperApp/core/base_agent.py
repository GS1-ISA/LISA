"""
Base agent class for ISA SuperApp.

This module provides the foundational agent infrastructure with common functionality
for all agents in the system.
"""

import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

from .config import ISAConfig
from .exceptions import ISAConfigurationError, ISAValidationError
from .logger import get_logger

T = TypeVar("T", bound="BaseAgent")


class AgentStatus(Enum):
    """Agent status enumeration."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"


class AgentCapability(Enum):
    """Agent capability enumeration."""

    DATA_INGESTION = "data_ingestion"
    DATA_PROCESSING = "data_processing"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    MONITORING = "monitoring"
    AI_PROCESSING = "ai_processing"
    VECTOR_OPERATIONS = "vector_operations"
    ETL_OPERATIONS = "etl_operations"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"


@dataclass
class AgentContext:
    """Agent execution context."""

    agent_id: str
    correlation_id: str
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    duration_ms: float | None = None


@dataclass
class AgentResult:
    """Agent execution result."""

    success: bool
    data: Any | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    correlation_id: str | None = None


@dataclass
class AgentMetrics:
    """Agent performance metrics."""

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time_ms: float = 0.0
    average_execution_time_ms: float = 0.0
    last_execution_time: datetime | None = None
    last_error: str | None = None
    error_count: int = 0


class BaseAgent(ABC):
    """
    Base agent class for ISA SuperApp.

    Provides common functionality for all agents including:
    - Lifecycle management
    - Configuration management
    - Logging and monitoring
    - Error handling
    - Context management
    - Metrics tracking
    """

    def __init__(
        self,
        agent_id: str | None = None,
        name: str | None = None,
        config: ISAConfig | None = None,
        capabilities: list[AgentCapability] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the base agent.

        Args:
            agent_id: Unique agent identifier (auto-generated if not provided)
            name: Agent name
            config: Configuration instance
            capabilities: List of agent capabilities
            metadata: Additional agent metadata
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.config = config or ISAConfig()
        self.capabilities = capabilities or []
        self.metadata = metadata or {}

        # Initialize logger
        self.logger = get_logger(f"agent.{self.name}", self.config)

        # Agent state
        self.status = AgentStatus.IDLE
        self._current_context: AgentContext | None = None
        self._metrics = AgentMetrics()
        self._start_time: datetime | None = None

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

        self.logger.info(
            "Agent initialized",
            agent_id=self.agent_id,
            name=self.name,
            capabilities=[cap.value for cap in self.capabilities],
        )

    @property
    def is_running(self) -> bool:
        """Check if agent is currently running."""
        return self.status == AgentStatus.RUNNING

    @property
    def is_idle(self) -> bool:
        """Check if agent is idle."""
        return self.status == AgentStatus.IDLE

    @property
    def metrics(self) -> AgentMetrics:
        """Get agent metrics."""
        return self._metrics

    def has_capability(self, capability: AgentCapability) -> bool:
        """
        Check if agent has specific capability.

        Args:
            capability: Capability to check

        Returns:
            True if agent has capability, False otherwise
        """
        return capability in self.capabilities

    def add_capability(self, capability: AgentCapability) -> None:
        """
        Add capability to agent.

        Args:
            capability: Capability to add
        """
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.logger.info(f"Added capability: {capability.value}")

    def remove_capability(self, capability: AgentCapability) -> None:
        """
        Remove capability from agent.

        Args:
            capability: Capability to remove
        """
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.logger.info(f"Removed capability: {capability.value}")

    def add_event_handler(self, event: str, handler: Callable) -> None:
        """
        Add event handler.

        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def remove_event_handler(self, event: str, handler: Callable) -> None:
        """
        Remove event handler.

        Args:
            event: Event name
            handler: Event handler function
        """
        if event in self._event_handlers and handler in self._event_handlers[event]:
            self._event_handlers[event].remove(handler)

    def _emit_event(self, event: str, data: dict[str, Any] | None = None) -> None:
        """
        Emit event to handlers.

        Args:
            event: Event name
            data: Event data
        """
        if event in self._event_handlers:
            event_data = data or {}
            event_data["agent_id"] = self.agent_id
            event_data["agent_name"] = self.name
            event_data["timestamp"] = datetime.utcnow()

            for handler in self._event_handlers[event]:
                try:
                    handler(event, event_data)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}", exc_info=True)

    def _create_context(
        self, correlation_id: str | None = None, **kwargs: Any
    ) -> AgentContext:
        """
        Create execution context.

        Args:
            correlation_id: Correlation ID for request tracking
            **kwargs: Additional context data

        Returns:
            AgentContext instance
        """
        correlation_id = correlation_id or str(uuid.uuid4())

        return AgentContext(
            agent_id=self.agent_id, correlation_id=correlation_id, **kwargs
        )

    def _update_metrics(
        self, success: bool, execution_time_ms: float, error: str | None = None
    ) -> None:
        """
        Update agent metrics.

        Args:
            success: Whether execution was successful
            execution_time_ms: Execution time in milliseconds
            error: Error message if execution failed
        """
        self._metrics.total_executions += 1
        self._metrics.total_execution_time_ms += execution_time_ms

        if success:
            self._metrics.successful_executions += 1
        else:
            self._metrics.failed_executions += 1
            self._metrics.error_count += 1
            self._metrics.last_error = error

        self._metrics.average_execution_time_ms = (
            self._metrics.total_execution_time_ms / self._metrics.total_executions
        )
        self._metrics.last_execution_time = datetime.utcnow()

    async def start(self, **kwargs: Any) -> AgentResult:
        """
        Start the agent.

        Args:
            **kwargs: Additional start parameters

        Returns:
            AgentResult indicating success/failure
        """
        if self.is_running:
            return AgentResult(success=False, error="Agent is already running")

        self.status = AgentStatus.RUNNING
        self._start_time = datetime.utcnow()

        self.logger.info("Agent started", agent_id=self.agent_id)
        self._emit_event("agent_started", {"start_time": self._start_time})

        return AgentResult(success=True)

    async def stop(self, **kwargs: Any) -> AgentResult:
        """
        Stop the agent.

        Args:
            **kwargs: Additional stop parameters

        Returns:
            AgentResult indicating success/failure
        """
        if not self.is_running:
            return AgentResult(success=False, error="Agent is not running")

        self.status = AgentStatus.STOPPED
        end_time = datetime.utcnow()

        self.logger.info("Agent stopped", agent_id=self.agent_id)
        self._emit_event(
            "agent_stopped",
            {
                "end_time": end_time,
                "duration": (
                    (end_time - self._start_time).total_seconds()
                    if self._start_time
                    else 0
                ),
            },
        )

        return AgentResult(success=True)

    async def pause(self, **kwargs: Any) -> AgentResult:
        """
        Pause the agent.

        Args:
            **kwargs: Additional pause parameters

        Returns:
            AgentResult indicating success/failure
        """
        if not self.is_running:
            return AgentResult(success=False, error="Agent is not running")

        self.status = AgentStatus.PAUSED
        self.logger.info("Agent paused", agent_id=self.agent_id)
        self._emit_event("agent_paused")

        return AgentResult(success=True)

    async def resume(self, **kwargs: Any) -> AgentResult:
        """
        Resume the agent.

        Args:
            **kwargs: Additional resume parameters

        Returns:
            AgentResult indicating success/failure
        """
        if self.status != AgentStatus.PAUSED:
            return AgentResult(success=False, error="Agent is not paused")

        self.status = AgentStatus.RUNNING
        self.logger.info("Agent resumed", agent_id=self.agent_id)
        self._emit_event("agent_resumed")

        return AgentResult(success=True)

    @abstractmethod
    async def execute(self, **kwargs: Any) -> AgentResult:
        """
        Execute the agent's main functionality.

        This method must be implemented by concrete agent classes.

        Args:
            **kwargs: Execution parameters

        Returns:
            AgentResult with execution results
        """
        pass

    async def execute_with_context(
        self, correlation_id: str | None = None, **kwargs: Any
    ) -> AgentResult:
        """
        Execute agent with context management.

        Args:
            correlation_id: Correlation ID for request tracking
            **kwargs: Execution parameters

        Returns:
            AgentResult with execution results
        """
        start_time = time.time()
        correlation_id = correlation_id or str(uuid.uuid4())

        # Create context
        self._current_context = self._create_context(correlation_id, **kwargs)

        # Set correlation ID in logger
        self.logger.set_correlation_id(correlation_id)

        self.logger.info(
            "Agent execution started",
            agent_id=self.agent_id,
            correlation_id=correlation_id,
            **kwargs,
        )

        try:
            # Execute agent
            result = await self.execute(**kwargs)

            # Update context
            self._current_context.end_time = datetime.utcnow()
            self._current_context.duration_ms = (time.time() - start_time) * 1000

            # Update metrics
            self._update_metrics(
                success=result.success,
                execution_time_ms=self._current_context.duration_ms,
                error=result.error,
            )

            # Log completion
            if result.success:
                self.logger.info(
                    "Agent execution completed successfully",
                    agent_id=self.agent_id,
                    correlation_id=correlation_id,
                    execution_time_ms=self._current_context.duration_ms,
                )
            else:
                self.logger.error(
                    "Agent execution failed",
                    agent_id=self.agent_id,
                    correlation_id=correlation_id,
                    error=result.error,
                    execution_time_ms=self._current_context.duration_ms,
                )

            # Add correlation ID to result
            result.correlation_id = correlation_id
            result.execution_time_ms = self._current_context.duration_ms

            return result

        except Exception as e:
            # Update context
            self._current_context.end_time = datetime.utcnow()
            self._current_context.duration_ms = (time.time() - start_time) * 1000

            # Update metrics
            self._update_metrics(
                success=False,
                execution_time_ms=self._current_context.duration_ms,
                error=str(e),
            )

            # Log error
            self.logger.exception(
                "Agent execution failed with exception",
                agent_id=self.agent_id,
                correlation_id=correlation_id,
                execution_time_ms=self._current_context.duration_ms,
            )

            return AgentResult(
                success=False,
                error=str(e),
                correlation_id=correlation_id,
                execution_time_ms=self._current_context.duration_ms,
            )

        finally:
            # Clear correlation ID
            self.logger.clear_correlation_id()
            self._current_context = None

    def get_status(self) -> dict[str, Any]:
        """
        Get agent status information.

        Returns:
            Dictionary with agent status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "metrics": {
                "total_executions": self._metrics.total_executions,
                "successful_executions": self._metrics.successful_executions,
                "failed_executions": self._metrics.failed_executions,
                "average_execution_time_ms": self._metrics.average_execution_time_ms,
                "last_execution_time": (
                    self._metrics.last_execution_time.isoformat()
                    if self._metrics.last_execution_time
                    else None
                ),
                "error_count": self._metrics.error_count,
                "last_error": self._metrics.last_error,
            },
            "metadata": self.metadata,
            "start_time": self._start_time.isoformat() if self._start_time else None,
        }

    def validate_configuration(self) -> None:
        """
        Validate agent configuration.

        Raises:
            ISAValidationError: If configuration is invalid
        """
        # Basic validation - can be overridden by subclasses
        if not self.agent_id:
            raise ISAValidationError("Agent ID cannot be empty", field="agent_id")

        if not self.name:
            raise ISAValidationError("Agent name cannot be empty", field="name")

        if not self.config:
            raise ISAValidationError("Configuration cannot be None", field="config")

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name}({self.agent_id})"

    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (
            f"BaseAgent(name='{self.name}', agent_id='{self.agent_id}', "
            f"status={self.status.value}, capabilities={self.capabilities})"
        )


# Agent registry for managing multiple agents
class AgentRegistry:
    """Registry for managing multiple agents."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._agents: dict[str, BaseAgent] = {}
        self.logger = get_logger("agent_registry")

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent.

        Args:
            agent: Agent instance to register
        """
        if agent.agent_id in self._agents:
            raise ISAConfigurationError(
                f"Agent with ID {agent.agent_id} already registered"
            )

        self._agents[agent.agent_id] = agent
        self.logger.info(f"Agent registered: {agent.name} ({agent.agent_id})")

    def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent.

        Args:
            agent_id: Agent ID to unregister
        """
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            del self._agents[agent_id]
            self.logger.info(f"Agent unregistered: {agent.name} ({agent_id})")
        else:
            self.logger.warning(f"Agent not found for unregistration: {agent_id}")

    def get_agent(self, agent_id: str) -> BaseAgent | None:
        """
        Get agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_id)

    def get_agents_by_capability(self, capability: AgentCapability) -> list[BaseAgent]:
        """
        Get agents by capability.

        Args:
            capability: Capability to filter by

        Returns:
            List of agents with the specified capability
        """
        return [
            agent for agent in self._agents.values() if agent.has_capability(capability)
        ]

    def get_all_agents(self) -> list[BaseAgent]:
        """
        Get all registered agents.

        Returns:
            List of all registered agents
        """
        return list(self._agents.values())

    def get_agent_statuses(self) -> dict[str, dict[str, Any]]:
        """
        Get status information for all agents.

        Returns:
            Dictionary mapping agent IDs to status information
        """
        return {
            agent_id: agent.get_status() for agent_id, agent in self._agents.items()
        }

    def __len__(self) -> int:
        """Get number of registered agents."""
        return len(self._agents)

    def __contains__(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self._agents


# Global agent registry
agent_registry = AgentRegistry()
