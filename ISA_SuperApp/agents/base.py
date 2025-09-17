"""
Base agent classes and data models for the ISA SuperApp agents module.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class AgentResponse:
    """Response model for agent operations."""

    content: str
    agent_id: str
    confidence: float = 1.0
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate the response data."""
        if not self.content:
            raise ValueError("AgentResponse content cannot be empty")
        if not self.agent_id:
            raise ValueError("AgentResponse agent_id cannot be empty")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("AgentResponse confidence must be between 0.0 and 1.0")
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentState:
    """State model for agent operations."""

    agent_id: str
    status: str
    current_task: str
    context: dict[str, Any]
    memory: dict[str, Any]
    timestamp: datetime

    def __post_init__(self):
        """Validate the state data."""
        if not self.agent_id:
            raise ValueError("AgentState agent_id cannot be empty")
        valid_statuses = ["active", "inactive", "idle", "processing", "error"]
        if self.status not in valid_statuses:
            raise ValueError(f"AgentState status must be one of: {valid_statuses}")


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, query: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """Process a query and return a response.

        Args:
            query: The query to process
            context: Optional context information

        Returns:
            AgentResponse: The agent's response
        """
        pass
