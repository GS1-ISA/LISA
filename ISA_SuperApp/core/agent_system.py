"""
Agent system for ISA SuperApp.

This module provides the core agent system functionality including
agent orchestration, task management, and coordination.
"""

import abc
import asyncio
import contextlib
import enum
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .exceptions import ISAConfigurationError, ISAValidationError
from .logger import get_logger
from .models import (
    AgentCapability,
    AgentStatus,
    AgentType,
    Message,
    MessageType,
    Task,
    TaskPriority,
    TaskStatus,
)
from .retrieval import RetrievalConfig, RetrievalSystem


class AgentEventType(enum.Enum):
    """Agent event types."""

    AGENT_CREATED = "agent_created"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_FAILED = "agent_failed"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"


@dataclass
class AgentEvent:
    """Agent system event."""

    event_type: AgentEventType
    agent_id: str | None = None
    task_id: str | None = None
    message_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentSystemConfig:
    """Agent system configuration."""

    max_agents: int = 100
    max_tasks_per_agent: int = 10
    task_timeout: int = 3600  # 1 hour
    message_queue_size: int = 1000
    enable_retrieval: bool = True
    retrieval_config: dict[str, Any] | None = None
    enable_caching: bool = True
    cache_size: int = 1000
    enable_monitoring: bool = True
    monitoring_interval: int = 60  # seconds

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if self.max_agents <= 0:
            raise ISAValidationError("max_agents must be positive", field="max_agents")
        if self.max_tasks_per_agent <= 0:
            raise ISAValidationError(
                "max_tasks_per_agent must be positive", field="max_tasks_per_agent"
            )
        if self.task_timeout <= 0:
            raise ISAValidationError(
                "task_timeout must be positive", field="task_timeout"
            )
        if self.message_queue_size <= 0:
            raise ISAValidationError(
                "message_queue_size must be positive", field="message_queue_size"
            )
        if self.cache_size <= 0:
            raise ISAValidationError("cache_size must be positive", field="cache_size")
        if self.monitoring_interval <= 0:
            raise ISAValidationError(
                "monitoring_interval must be positive", field="monitoring_interval"
            )


class BaseAgent(abc.ABC):
    """Abstract base class for agents."""

    def __init__(
        self, agent_id: str, agent_type: AgentType, config: dict[str, Any]
    ) -> None:
        """
        Initialize base agent.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent
            config: Agent configuration
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        self.status = AgentStatus.IDLE
        self.capabilities: set[AgentCapability] = set()
        self.current_tasks: list[str] = []
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self.logger = get_logger(f"agent.{agent_id}")
        self._running = False
        self._task: asyncio.Task | None = None

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent."""
        pass

    @abc.abstractmethod
    async def process_task(self, task: Task) -> Any:
        """
        Process a task.

        Args:
            task: Task to process

        Returns:
            Task result
        """
        pass

    @abc.abstractmethod
    async def handle_message(self, message: Message) -> Any:
        """
        Handle a message.

        Args:
            message: Message to handle

        Returns:
            Message response
        """
        pass

    async def start(self) -> None:
        """Start the agent."""
        if self._running:
            return

        self._running = True
        self.status = AgentStatus.ACTIVE
        self._task = asyncio.create_task(self._run())
        self.logger.info(f"Agent {self.agent_id} started")

    async def stop(self) -> None:
        """Stop the agent."""
        if not self._running:
            return

        self._running = False
        self.status = AgentStatus.STOPPED

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

        self.logger.info(f"Agent {self.agent_id} stopped")

    async def assign_task(self, task: Task) -> bool:
        """
        Assign a task to the agent.

        Args:
            task: Task to assign

        Returns:
            True if task assigned successfully
        """
        if len(self.current_tasks) >= 10:  # Max tasks per agent
            return False

        if self.status != AgentStatus.ACTIVE:
            return False

        self.current_tasks.append(task.task_id)
        await self.message_queue.put(
            Message(
                message_id=str(uuid.uuid4()),
                sender_id="system",
                receiver_id=self.agent_id,
                message_type=MessageType.TASK,
                content={"task": task.to_dict()},
                timestamp=datetime.utcnow(),
            )
        )

        self.logger.info(f"Task {task.task_id} assigned to agent {self.agent_id}")
        return True

    async def send_message(self, message: Message) -> None:
        """
        Send a message to the agent.

        Args:
            message: Message to send
        """
        await self.message_queue.put(message)
        self.logger.debug(f"Message {message.message_id} sent to agent {self.agent_id}")

    def has_capability(self, capability: AgentCapability) -> bool:
        """
        Check if agent has a capability.

        Args:
            capability: Capability to check

        Returns:
            True if agent has capability
        """
        return capability in self.capabilities

    async def _run(self) -> None:
        """Main agent loop."""
        try:
            while self._running:
                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(
                        self.message_queue.get(), timeout=1.0
                    )

                    await self._process_message(message)

                except asyncio.TimeoutError:
                    # No messages, continue loop
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    self.status = AgentStatus.ERROR

        except asyncio.CancelledError:
            self.logger.info(f"Agent {self.agent_id} loop cancelled")
        except Exception as e:
            self.logger.error(f"Agent {self.agent_id} error: {e}")
            self.status = AgentStatus.ERROR
        finally:
            self.status = AgentStatus.STOPPED

    async def _process_message(self, message: Message) -> None:
        """Process a message."""
        try:
            if message.message_type == MessageType.TASK:
                await self._process_task_message(message)
            else:
                await self.handle_message(message)

        except Exception as e:
            self.logger.error(f"Error processing message {message.message_id}: {e}")

    async def _process_task_message(self, message: Message) -> None:
        """Process a task message."""
        task_data = message.content["task"]
        task = Task.from_dict(task_data)

        self.status = AgentStatus.WORKING
        self.logger.info(f"Agent {self.agent_id} processing task {task.task_id}")

        try:
            result = await self.process_task(task)

            # Send completion message
            Message(
                message_id=str(uuid.uuid4()),
                sender_id=self.agent_id,
                receiver_id="system",
                message_type=MessageType.TASK_RESULT,
                content={
                    "task_id": task.task_id,
                    "result": result,
                    "status": "completed",
                },
                timestamp=datetime.utcnow(),
            )

            # In a real system, this would be sent to the orchestrator
            self.logger.info(f"Task {task.task_id} completed by agent {self.agent_id}")

        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed: {e}")

            # Send failure message
            Message(
                message_id=str(uuid.uuid4()),
                sender_id=self.agent_id,
                receiver_id="system",
                message_type=MessageType.TASK_RESULT,
                content={"task_id": task.task_id, "error": str(e), "status": "failed"},
                timestamp=datetime.utcnow(),
            )

        finally:
            # Remove task from current tasks
            if task.task_id in self.current_tasks:
                self.current_tasks.remove(task.task_id)

            self.status = AgentStatus.IDLE


class ResearchAgent(BaseAgent):
    """Research agent for document analysis and information retrieval."""

    def __init__(self, agent_id: str, config: dict[str, Any]) -> None:
        """
        Initialize research agent.

        Args:
            agent_id: Unique agent identifier
            config: Agent configuration
        """
        super().__init__(agent_id, AgentType.RESEARCH, config)
        self.retrieval_system: RetrievalSystem | None = None
        self.capabilities.add(AgentCapability.INFORMATION_RETRIEVAL)
        self.capabilities.add(AgentCapability.DOCUMENT_ANALYSIS)
        self.capabilities.add(AgentCapability.SEARCH)

    async def initialize(self) -> None:
        """Initialize the research agent."""
        if self.config.get("enable_retrieval", True):
            retrieval_config = self.config.get("retrieval_config", {})
            self.retrieval_system = await self._create_retrieval_system(
                retrieval_config
            )

        self.logger.info(f"Research agent {self.agent_id} initialized")

    async def process_task(self, task: Task) -> Any:
        """
        Process a research task.

        Args:
            task: Task to process

        Returns:
            Task result
        """
        task_type = task.task_type
        task_data = task.data

        if task_type == "search":
            return await self._handle_search_task(task_data)
        elif task_type == "analyze":
            return await self._handle_analyze_task(task_data)
        elif task_type == "summarize":
            return await self._handle_summarize_task(task_data)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")

    async def handle_message(self, message: Message) -> Any:
        """
        Handle a message.

        Args:
            message: Message to handle

        Returns:
            Message response
        """
        # Handle different message types
        if message.message_type == MessageType.QUERY:
            return await self._handle_query(message.content)
        elif message.message_type == MessageType.COMMAND:
            return await self._handle_command(message.content)
        else:
            self.logger.warning(f"Unhandled message type: {message.message_type}")
            return None

    async def _create_retrieval_system(self, config: dict[str, Any]) -> RetrievalSystem:
        """Create retrieval system for the agent."""
        retrieval_config = RetrievalConfig(
            strategy=config.get("strategy", "dense"),
            vector_store_provider=config.get("vector_store_provider", "in_memory"),
            embedding_provider=config.get(
                "embedding_provider", "sentence_transformers"
            ),
            collection_name=config.get("collection_name", f"research_{self.agent_id}"),
            vector_dimension=config.get("vector_dimension", 384),
            top_k=config.get("top_k", 10),
            similarity_threshold=config.get("similarity_threshold", 0.7),
        )

        return RetrievalSystem(retrieval_config)

    async def _handle_search_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Handle search task."""
        query = task_data.get("query")
        top_k = task_data.get("top_k", 10)
        filter_metadata = task_data.get("filter_metadata")

        if not query:
            raise ValueError("Query is required for search task")

        if not self.retrieval_system:
            raise ValueError("Retrieval system not available")

        results = await self.retrieval_system.retrieve(query, top_k, filter_metadata)

        return {
            "query": query,
            "results": [result.to_dict() for result in results],
            "result_count": len(results),
        }

    async def _handle_analyze_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Handle analyze task."""
        document_id = task_data.get("document_id")
        analysis_type = task_data.get("analysis_type", "general")

        if not document_id:
            raise ValueError("Document ID is required for analyze task")

        # Simulate document analysis
        analysis_result = {
            "document_id": document_id,
            "analysis_type": analysis_type,
            "summary": f"Analysis of document {document_id}",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "sentiment": "neutral",
            "topics": ["topic1", "topic2"],
            "timestamp": datetime.utcnow().isoformat(),
        }

        return analysis_result

    async def _handle_summarize_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Handle summarize task."""
        document_ids = task_data.get("document_ids", [])
        max_length = task_data.get("max_length", 500)

        if not document_ids:
            raise ValueError("Document IDs are required for summarize task")

        # Simulate document summarization
        summary_result = {
            "document_ids": document_ids,
            "summary": f"Summary of {len(document_ids)} documents",
            "key_points": ["Key point 1", "Key point 2", "Key point 3"],
            "length": max_length,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return summary_result

    async def _handle_query(self, content: dict[str, Any]) -> dict[str, Any]:
        """Handle query message."""
        query = content.get("query")

        if not query:
            raise ValueError("Query is required")

        if not self.retrieval_system:
            raise ValueError("Retrieval system not available")

        results = await self.retrieval_system.retrieve(query)

        return {
            "query": query,
            "results": [result.to_dict() for result in results],
            "result_count": len(results),
        }

    async def _handle_command(self, content: dict[str, Any]) -> dict[str, Any]:
        """Handle command message."""
        command = content.get("command")
        content.get("params", {})

        if command == "status":
            return {
                "agent_id": self.agent_id,
                "status": self.status.value,
                "capabilities": [cap.value for cap in self.capabilities],
                "current_tasks": len(self.current_tasks),
            }
        elif command == "capabilities":
            return {"capabilities": [cap.value for cap in self.capabilities]}
        else:
            raise ValueError(f"Unknown command: {command}")


class AgentOrchestrator:
    """Agent orchestrator for managing agents and tasks."""

    def __init__(self, config: AgentSystemConfig) -> None:
        """
        Initialize agent orchestrator.

        Args:
            config: Agent system configuration
        """
        self.config = config
        self.logger = get_logger("agent.orchestrator")
        self.agents: dict[str, BaseAgent] = {}
        self.tasks: dict[str, Task] = {}
        self.event_listeners: list[Callable[[AgentEvent], None]] = []
        self.retrieval_system: RetrievalSystem | None = None
        self._running = False
        self._monitoring_task: asyncio.Task | None = None

    async def initialize(self) -> None:
        """Initialize the orchestrator."""
        try:
            # Initialize retrieval system if enabled
            if self.config.enable_retrieval and self.config.retrieval_config:
                retrieval_config = RetrievalConfig(**self.config.retrieval_config)
                self.retrieval_system = RetrievalSystem(retrieval_config)
                await self.retrieval_system.initialize()

            self._running = True

            # Start monitoring if enabled
            if self.config.enable_monitoring:
                self._monitoring_task = asyncio.create_task(self._monitor_agents())

            self.logger.info("Agent orchestrator initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            raise ISAConfigurationError(f"Failed to initialize orchestrator: {e}")

    async def close(self) -> None:
        """Close the orchestrator."""
        self._running = False

        # Stop monitoring
        if self._monitoring_task:
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task

        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()

        # Close retrieval system
        if self.retrieval_system:
            await self.retrieval_system.close()

        self.logger.info("Agent orchestrator closed")

    def add_event_listener(self, listener: Callable[[AgentEvent], None]) -> None:
        """
        Add an event listener.

        Args:
            listener: Event listener function
        """
        self.event_listeners.append(listener)

    def remove_event_listener(self, listener: Callable[[AgentEvent], None]) -> None:
        """
        Remove an event listener.

        Args:
            listener: Event listener function to remove
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)

    async def create_agent(self, agent_type: AgentType, config: dict[str, Any]) -> str:
        """
        Create a new agent.

        Args:
            agent_type: Type of agent to create
            config: Agent configuration

        Returns:
            Agent ID

        Raises:
            ISAConfigurationError: If max agents reached
        """
        if len(self.agents) >= self.config.max_agents:
            raise ISAConfigurationError(
                f"Maximum agents ({self.config.max_agents}) reached"
            )

        agent_id = str(uuid.uuid4())

        if agent_type == AgentType.RESEARCH:
            agent = ResearchAgent(agent_id, config)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        await agent.initialize()
        await agent.start()

        self.agents[agent_id] = agent

        # Emit event
        self._emit_event(
            AgentEvent(
                event_type=AgentEventType.AGENT_CREATED,
                agent_id=agent_id,
                data={"agent_type": agent_type.value, "config": config},
            )
        )

        self.logger.info(f"Agent {agent_id} created and started")
        return agent_id

    async def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent.

        Args:
            agent_id: Agent ID to remove

        Returns:
            True if agent was removed
        """
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        await agent.stop()

        del self.agents[agent_id]

        # Emit event
        self._emit_event(
            AgentEvent(event_type=AgentEventType.AGENT_STOPPED, agent_id=agent_id)
        )

        self.logger.info(f"Agent {agent_id} removed")
        return True

    async def create_task(
        self,
        task_type: str,
        data: dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_agent_id: str | None = None,
    ) -> str:
        """
        Create a new task.

        Args:
            task_type: Type of task
            data: Task data
            priority: Task priority
            assigned_agent_id: Optional agent ID to assign task to

        Returns:
            Task ID

        Raises:
            ISAValidationError: If task data is invalid
        """
        if not task_type:
            raise ISAValidationError("Task type is required", field="task_type")

        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_type=task_type,
            data=data,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
            assigned_agent_id=assigned_agent_id,
        )

        self.tasks[task_id] = task

        # Assign to agent if specified
        if assigned_agent_id:
            await self.assign_task(task_id, assigned_agent_id)

        # Emit event
        self._emit_event(
            AgentEvent(
                event_type=AgentEventType.TASK_ASSIGNED,
                task_id=task_id,
                agent_id=assigned_agent_id,
                data={"task_type": task_type, "priority": priority.value},
            )
        )

        self.logger.info(f"Task {task_id} created")
        return task_id

    async def assign_task(self, task_id: str, agent_id: str) -> bool:
        """
        Assign a task to an agent.

        Args:
            task_id: Task ID
            agent_id: Agent ID

        Returns:
            True if task assigned successfully
        """
        if task_id not in self.tasks:
            return False

        if agent_id not in self.agents:
            return False

        task = self.tasks[task_id]
        agent = self.agents[agent_id]

        if task.status != TaskStatus.PENDING:
            return False

        if len(agent.current_tasks) >= self.config.max_tasks_per_agent:
            return False

        success = await agent.assign_task(task)
        if success:
            task.status = TaskStatus.ASSIGNED
            task.assigned_agent_id = agent_id
            task.assigned_at = datetime.utcnow()

        return success

    async def get_agent_status(self, agent_id: str) -> dict[str, Any] | None:
        """
        Get agent status.

        Args:
            agent_id: Agent ID

        Returns:
            Agent status information or None if not found
        """
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "agent_type": agent.agent_type.value,
            "status": agent.status.value,
            "capabilities": [cap.value for cap in agent.capabilities],
            "current_tasks": agent.current_tasks,
            "task_count": len(agent.current_tasks),
        }

    async def get_system_status(self) -> dict[str, Any]:
        """
        Get overall system status.

        Returns:
            System status information
        """
        agent_statuses = {}
        for agent_id in self.agents:
            agent_status = await self.get_agent_status(agent_id)
            if agent_status:
                agent_statuses[agent_id] = agent_status

        task_summary = {
            "total": len(self.tasks),
            "pending": sum(
                1 for task in self.tasks.values() if task.status == TaskStatus.PENDING
            ),
            "assigned": sum(
                1 for task in self.tasks.values() if task.status == TaskStatus.ASSIGNED
            ),
            "completed": sum(
                1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED
            ),
            "failed": sum(
                1 for task in self.tasks.values() if task.status == TaskStatus.FAILED
            ),
        }

        return {
            "agents": agent_statuses,
            "tasks": task_summary,
            "retrieval_enabled": self.retrieval_system is not None,
            "monitoring_enabled": self.config.enable_monitoring,
            "uptime": self._get_uptime(),
        }

    def _emit_event(self, event: AgentEvent) -> None:
        """Emit an event to all listeners."""
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error in event listener: {e}")

    async def _monitor_agents(self) -> None:
        """Monitor agent health and performance."""
        while self._running:
            try:
                await asyncio.sleep(self.config.monitoring_interval)

                # Check agent health
                for agent_id, agent in self.agents.items():
                    if agent.status == AgentStatus.ERROR:
                        self.logger.warning(f"Agent {agent_id} is in error state")
                        # Could attempt recovery here

                # Check for stuck tasks
                current_time = datetime.utcnow()
                for task_id, task in self.tasks.items():
                    if (
                        task.status == TaskStatus.ASSIGNED
                        and task.assigned_at
                        and (current_time - task.assigned_at).total_seconds()
                        > self.config.task_timeout
                    ):
                        self.logger.warning(f"Task {task_id} appears to be stuck")
                        # Could reassign or fail the task here

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring: {e}")

    def _get_uptime(self) -> float:
        """Get system uptime in seconds."""
        # This is a simplified implementation
        return 0.0


# Utility functions
async def create_agent_system(
    max_agents: int = 100,
    enable_retrieval: bool = True,
    retrieval_config: dict[str, Any] | None = None,
    **kwargs,
) -> AgentOrchestrator:
    """
    Create an agent system with common configuration.

    Args:
        max_agents: Maximum number of agents
        enable_retrieval: Whether to enable retrieval system
        retrieval_config: Retrieval system configuration
        **kwargs: Additional configuration parameters

    Returns:
        Agent orchestrator instance
    """
    config = AgentSystemConfig(
        max_agents=max_agents,
        enable_retrieval=enable_retrieval,
        retrieval_config=retrieval_config,
        **kwargs,
    )

    orchestrator = AgentOrchestrator(config)
    await orchestrator.initialize()
    return orchestrator


async def create_agent_system_from_config(
    config_dict: dict[str, Any],
) -> AgentOrchestrator:
    """
    Create an agent system from configuration dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        Agent orchestrator instance
    """
    config = AgentSystemConfig(**config_dict)
    orchestrator = AgentOrchestrator(config)
    await orchestrator.initialize()
    return orchestrator
