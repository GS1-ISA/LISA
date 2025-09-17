"""
Base orchestrator module for ISA SuperApp.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskDefinition:
    """Definition of a task to be executed."""

    task_id: str
    task_type: str
    parameters: dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout_seconds: int | None = None
    dependencies: list | None = None

    def __post_init__(self):
        """Post initialization validation."""
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not self.task_type:
            raise ValueError("task_type cannot be empty")
