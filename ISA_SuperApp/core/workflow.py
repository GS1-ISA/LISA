"""
Workflow system for ISA SuperApp.

This module provides workflow management functionality including
workflow definition, execution, and monitoring.
"""

import abc
import asyncio
import enum
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .agent_system import AgentOrchestrator, BaseAgent, ResearchAgent
from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
from .logger import get_logger
from .models import (
    AgentCapability,
    AgentType,
    Document,
    SearchResult,
    Task,
    TaskPriority,
    TaskStatus,
)


class WorkflowStatus(enum.Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowStepStatus(enum.Enum):
    """Workflow step execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStepType(enum.Enum):
    """Workflow step types."""

    AGENT_TASK = "agent_task"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    WAIT = "wait"
    DATA_PROCESSING = "data_processing"
    EXTERNAL_API = "external_api"


@dataclass
class WorkflowStep:
    """Workflow step definition."""

    step_id: str
    step_type: WorkflowStepType
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    retry_config: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 300  # 5 minutes default
    required_capabilities: List[AgentCapability] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.step_id:
            raise ISAValidationError("step_id is required", field="step_id")
        if not self.name:
            raise ISAValidationError("name is required", field="name")


@dataclass
class WorkflowStepResult:
    """Workflow step execution result."""

    step_id: str
    status: WorkflowStepStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
        }


@dataclass
class WorkflowExecution:
    """Workflow execution instance."""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str] = None
    step_results: Dict[str, WorkflowStepResult] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "current_step": self.current_step,
            "step_results": {
                step_id: result.to_dict()
                for step_id, result in self.step_results.items()
            },
            "context": self.context,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class WorkflowDefinition:
    """Workflow definition."""

    workflow_id: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.workflow_id:
            raise ISAValidationError("workflow_id is required", field="workflow_id")
        if not self.name:
            raise ISAValidationError("name is required", field="name")
        if not self.steps:
            raise ISAValidationError("At least one step is required", field="steps")

        # Validate step dependencies
        step_ids = {step.step_id for step in self.steps}
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ISAValidationError(
                        f"Dependency {dep} not found in workflow steps",
                        field="dependencies",
                    )

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get workflow step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_dependencies(self, step_id: str) -> List[str]:
        """Get dependencies for a step."""
        step = self.get_step(step_id)
        return step.dependencies if step else []

    def get_dependents(self, step_id: str) -> List[str]:
        """Get steps that depend on this step."""
        dependents = []
        for step in self.steps:
            if step_id in step.dependencies:
                dependents.append(step.step_id)
        return dependents


class BaseWorkflowExecutor(abc.ABC):
    """Abstract base class for workflow executors."""

    def __init__(self, orchestrator: AgentOrchestrator) -> None:
        """
        Initialize workflow executor.

        Args:
            orchestrator: Agent orchestrator
        """
        self.orchestrator = orchestrator
        self.logger = get_logger("workflow.executor")

    @abc.abstractmethod
    async def execute_step(
        self, step: WorkflowStep, context: Dict[str, Any], execution: WorkflowExecution
    ) -> WorkflowStepResult:
        """
        Execute a workflow step.

        Args:
            step: Workflow step to execute
            context: Execution context
            execution: Workflow execution instance

        Returns:
            Step execution result
        """
        pass

    async def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.

        Args:
            condition: Condition expression
            context: Execution context

        Returns:
            Condition result
        """
        # Simple condition evaluation - in a real system, use a proper expression evaluator
        try:
            # Replace context variables in condition
            for key, value in context.items():
                if isinstance(value, (str, int, float, bool)):
                    condition = condition.replace(f"${{{key}}}", str(value))

            # Evaluate the condition
            return eval(condition, {"__builtins__": {}})
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False


class AgentTaskExecutor(BaseWorkflowExecutor):
    """Executor for agent task steps."""

    async def execute_step(
        self, step: WorkflowStep, context: Dict[str, Any], execution: WorkflowExecution
    ) -> WorkflowStepResult:
        """
        Execute an agent task step.

        Args:
            step: Workflow step to execute
            context: Execution context
            execution: Workflow execution instance

        Returns:
            Step execution result
        """
        start_time = datetime.utcnow()

        try:
            # Get task configuration
            task_config = step.config.get("task", {})
            task_type = task_config.get("type")
            task_data = task_config.get("data", {})

            if not task_type:
                raise ValueError("Task type is required for agent task step")

            # Merge context data with task data
            merged_data = {**context, **task_data}

            # Find suitable agent
            agent_id = await self._find_suitable_agent(step, merged_data)
            if not agent_id:
                raise ValueError("No suitable agent found for task")

            # Create task
            task_id = await self.orchestrator.create_task(
                task_type=task_type,
                data=merged_data,
                priority=TaskPriority.MEDIUM,
                assigned_agent_id=agent_id,
            )

            # Wait for task completion
            result = await self._wait_for_task_completion(task_id)

            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            return WorkflowStepResult(
                step_id=step.step_id,
                status=WorkflowStepStatus.COMPLETED,
                result=result,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
            )

        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            return WorkflowStepResult(
                step_id=step.step_id,
                status=WorkflowStepStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
            )

    async def _find_suitable_agent(
        self, step: WorkflowStep, data: Dict[str, Any]
    ) -> Optional[str]:
        """Find a suitable agent for the task."""
        # Get available agents
        available_agents = []
        for agent_id in self.orchestrator.agents:
            agent_status = await self.orchestrator.get_agent_status(agent_id)
            if (
                agent_status
                and agent_status["status"] == "active"
                and len(agent_status["current_tasks"]) < 10
            ):  # Max tasks per agent
                # Check capabilities
                agent_capabilities = set(agent_status["capabilities"])
                required_capabilities = set(
                    cap.value for cap in step.required_capabilities
                )

                if required_capabilities.issubset(agent_capabilities):
                    available_agents.append(agent_id)

        # Return first available agent (could be more sophisticated)
        return available_agents[0] if available_agents else None

    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300) -> Any:
        """Wait for task completion."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check task status
            if task_id in self.orchestrator.tasks:
                task = self.orchestrator.tasks[task_id]
                if task.status == TaskStatus.COMPLETED:
                    return task.result
                elif task.status == TaskStatus.FAILED:
                    raise ValueError(f"Task {task_id} failed")

            await asyncio.sleep(1)

        raise TimeoutError(f"Task {task_id} timed out")


class ConditionalExecutor(BaseWorkflowExecutor):
    """Executor for conditional steps."""

    async def execute_step(
        self, step: WorkflowStep, context: Dict[str, Any], execution: WorkflowExecution
    ) -> WorkflowStepResult:
        """
        Execute a conditional step.

        Args:
            step: Workflow step to execute
            context: Execution context
            execution: Workflow execution instance

        Returns:
            Step execution result
        """
        start_time = datetime.utcnow()

        try:
            condition = step.config.get("condition", step.condition)
            if not condition:
                raise ValueError("Condition is required for conditional step")

            # Evaluate condition
            condition_result = await self.evaluate_condition(condition, context)

            # Determine next steps based on condition
            next_steps = step.config.get("next_steps", {})
            if condition_result:
                next_step_id = next_steps.get("true")
            else:
                next_step_id = next_steps.get("false")

            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            return WorkflowStepResult(
                step_id=step.step_id,
                status=WorkflowStepStatus.COMPLETED,
                result={
                    "condition": condition,
                    "result": condition_result,
                    "next_step_id": next_step_id,
                },
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
            )

        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            return WorkflowStepResult(
                step_id=step.step_id,
                status=WorkflowStepStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
            )


class ParallelExecutor(BaseWorkflowExecutor):
    """Executor for parallel steps."""

    async def execute_step(
        self, step: WorkflowStep, context: Dict[str, Any], execution: WorkflowExecution
    ) -> WorkflowStepResult:
        """
        Execute a parallel step.

        Args:
            step: Workflow step to execute
            context: Execution context
            execution: Workflow execution instance

        Returns:
            Step execution result
        """
        start_time = datetime.utcnow()

        try:
            # Get sub-steps to execute in parallel
            sub_steps = step.config.get("steps", [])
            if not sub_steps:
                raise ValueError("Sub-steps are required for parallel step")

            # Execute sub-steps in parallel
            tasks = []
            for sub_step_config in sub_steps:
                sub_step = WorkflowStep(**sub_step_config)
                # Create appropriate executor for sub-step
                executor = self._create_executor(sub_step.step_type)
                task = executor.execute_step(sub_step, context, execution)
                tasks.append(task)

            # Wait for all sub-steps to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            successful_results = []
            failed_results = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_results.append({"step_index": i, "error": str(result)})
                else:
                    successful_results.append(result)

            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            return WorkflowStepResult(
                step_id=step.step_id,
                status=WorkflowStepStatus.COMPLETED,
                result={
                    "successful_count": len(successful_results),
                    "failed_count": len(failed_results),
                    "successful_results": [r.to_dict() for r in successful_results],
                    "failed_results": failed_results,
                },
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
            )

        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            return WorkflowStepResult(
                step_id=step.step_id,
                status=WorkflowStepStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
            )

    def _create_executor(self, step_type: WorkflowStepType) -> BaseWorkflowExecutor:
        """Create executor for step type."""
        if step_type == WorkflowStepType.AGENT_TASK:
            return AgentTaskExecutor(self.orchestrator)
        elif step_type == WorkflowStepType.CONDITIONAL:
            return ConditionalExecutor(self.orchestrator)
        elif step_type == WorkflowStepType.PARALLEL:
            return ParallelExecutor(self.orchestrator)
        else:
            raise ValueError(
                f"Unsupported step type for parallel execution: {step_type}"
            )


class WorkflowEngine:
    """Workflow engine for managing workflow execution."""

    def __init__(self, orchestrator: AgentOrchestrator) -> None:
        """
        Initialize workflow engine.

        Args:
            orchestrator: Agent orchestrator
        """
        self.orchestrator = orchestrator
        self.logger = get_logger("workflow.engine")
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.executors: Dict[WorkflowStepType, BaseWorkflowExecutor] = {}

        # Register default executors
        self._register_executors()

    def _register_executors(self) -> None:
        """Register workflow step executors."""
        self.executors[WorkflowStepType.AGENT_TASK] = AgentTaskExecutor(
            self.orchestrator
        )
        self.executors[WorkflowStepType.CONDITIONAL] = ConditionalExecutor(
            self.orchestrator
        )
        self.executors[WorkflowStepType.PARALLEL] = ParallelExecutor(self.orchestrator)
        self.executors[WorkflowStepType.SEQUENTIAL] = AgentTaskExecutor(
            self.orchestrator
        )  # Reuse

    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """
        Register a workflow definition.

        Args:
            workflow: Workflow definition
        """
        self.workflows[workflow.workflow_id] = workflow
        self.logger.info(f"Workflow {workflow.workflow_id} registered")

    def unregister_workflow(self, workflow_id: str) -> bool:
        """
        Unregister a workflow definition.

        Args:
            workflow_id: Workflow ID

        Returns:
            True if workflow was unregistered
        """
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            self.logger.info(f"Workflow {workflow_id} unregistered")
            return True
        return False

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        execution_id: Optional[str] = None,
    ) -> str:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow ID
            input_data: Input data for the workflow
            execution_id: Optional execution ID

        Returns:
            Execution ID

        Raises:
            ISANotFoundError: If workflow not found
            ISAValidationError: If input data is invalid
        """
        if workflow_id not in self.workflows:
            raise ISANotFoundError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]

        # Validate input data
        if not self._validate_input(input_data, workflow.input_schema):
            raise ISAValidationError("Invalid input data", field="input_data")

        # Create execution
        if not execution_id:
            execution_id = str(uuid.uuid4())

        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            context=input_data,
        )

        self.executions[execution_id] = execution

        # Start execution
        asyncio.create_task(self._execute_workflow_async(workflow, execution))

        self.logger.info(f"Workflow {workflow_id} execution {execution_id} started")
        return execution_id

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow execution status.

        Args:
            execution_id: Execution ID

        Returns:
            Execution status or None if not found
        """
        if execution_id not in self.executions:
            return None

        execution = self.executions[execution_id]
        return execution.to_dict()

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a workflow execution.

        Args:
            execution_id: Execution ID

        Returns:
            True if execution was cancelled
        """
        if execution_id not in self.executions:
            return False

        execution = self.executions[execution_id]
        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            self.logger.info(f"Execution {execution_id} cancelled")
            return True

        return False

    async def _execute_workflow_async(
        self, workflow: WorkflowDefinition, execution: WorkflowExecution
    ) -> None:
        """Execute workflow asynchronously."""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.utcnow()

            self.logger.info(
                f"Starting workflow {workflow.workflow_id} execution {execution.execution_id}"
            )

            # Execute steps in dependency order
            executed_steps = set()
            pending_steps = {step.step_id for step in workflow.steps}

            while pending_steps:
                # Find steps that can be executed (dependencies satisfied)
                executable_steps = []
                for step_id in pending_steps:
                    step = workflow.get_step(step_id)
                    if step:
                        dependencies_satisfied = all(
                            dep in executed_steps for dep in step.dependencies
                        )
                        if dependencies_satisfied:
                            executable_steps.append(step)

                if not executable_steps:
                    # No progress can be made - circular dependency?
                    raise ValueError(
                        "Cannot execute workflow - circular dependency detected"
                    )

                # Execute steps
                for step in executable_steps:
                    execution.current_step = step.step_id

                    # Check if step should be skipped due to condition
                    if step.condition:
                        executor = self.executors[WorkflowStepType.CONDITIONAL]
                        condition_result = await executor.evaluate_condition(
                            step.condition, execution.context
                        )
                        if not condition_result:
                            # Skip this step
                            execution.step_results[step.step_id] = WorkflowStepResult(
                                step_id=step.step_id,
                                status=WorkflowStepStatus.SKIPPED,
                                result={"reason": "Condition not met"},
                            )
                            executed_steps.add(step.step_id)
                            pending_steps.remove(step.step_id)
                            continue

                    # Execute step
                    executor = self.executors.get(step.step_type)
                    if not executor:
                        raise ValueError(
                            f"No executor found for step type {step.step_type}"
                        )

                    step_result = await executor.execute_step(
                        step, execution.context, execution
                    )
                    execution.step_results[step.step_id] = step_result

                    # Update context with step result
                    if step_result.result:
                        execution.context[f"step_{step.step_id}_result"] = (
                            step_result.result
                        )

                    executed_steps.add(step.step_id)
                    pending_steps.remove(step.step_id)

                    # Check if workflow should stop due to failure
                    if step_result.status == WorkflowStepStatus.FAILED:
                        execution.status = WorkflowStatus.FAILED
                        execution.end_time = datetime.utcnow()
                        self.logger.error(
                            f"Workflow execution {execution.execution_id} failed at step {step.step_id}"
                        )
                        return

                # Small delay between batches
                await asyncio.sleep(0.1)

            # All steps completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.utcnow()

            self.logger.info(
                f"Workflow execution {execution.execution_id} completed successfully"
            )

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.utcnow()
            self.logger.error(
                f"Workflow execution {execution.execution_id} failed: {e}"
            )

    def _validate_input(
        self, input_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> bool:
        """Validate input data against schema."""
        # Simple validation - in a real system, use a proper schema validator
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in input_data:
                return False
        return True


# Predefined workflow templates
def create_research_workflow() -> WorkflowDefinition:
    """Create a research workflow definition."""
    return WorkflowDefinition(
        workflow_id="research_workflow_v1",
        name="Research Workflow",
        description="A workflow for conducting research and analysis",
        version="1.0.0",
        steps=[
            WorkflowStep(
                step_id="search_documents",
                step_type=WorkflowStepType.AGENT_TASK,
                name="Search Documents",
                description="Search for relevant documents",
                config={
                    "task": {
                        "type": "search",
                        "data": {"query": "${query}", "top_k": 10},
                    }
                },
                required_capabilities=[AgentCapability.SEARCH],
            ),
            WorkflowStep(
                step_id="analyze_documents",
                step_type=WorkflowStepType.AGENT_TASK,
                name="Analyze Documents",
                description="Analyze found documents",
                config={
                    "task": {
                        "type": "analyze",
                        "data": {
                            "document_ids": "${step_search_documents_result.results}"
                        },
                    }
                },
                dependencies=["search_documents"],
                required_capabilities=[AgentCapability.DOCUMENT_ANALYSIS],
            ),
            WorkflowStep(
                step_id="generate_summary",
                step_type=WorkflowStepType.AGENT_TASK,
                name="Generate Summary",
                description="Generate summary of analysis",
                config={
                    "task": {
                        "type": "summarize",
                        "data": {
                            "analysis_results": "${step_analyze_documents_result}"
                        },
                    }
                },
                dependencies=["analyze_documents"],
                required_capabilities=[AgentCapability.INFORMATION_RETRIEVAL],
            ),
        ],
        input_schema={
            "required": ["query"],
            "properties": {"query": {"type": "string", "description": "Search query"}},
        },
        output_schema={
            "properties": {
                "summary": {"type": "string", "description": "Research summary"}
            }
        },
    )


def create_document_processing_workflow() -> WorkflowDefinition:
    """Create a document processing workflow definition."""
    return WorkflowDefinition(
        workflow_id="document_processing_workflow_v1",
        name="Document Processing Workflow",
        description="A workflow for processing and analyzing documents",
        version="1.0.0",
        steps=[
            WorkflowStep(
                step_id="ingest_documents",
                step_type=WorkflowStepType.AGENT_TASK,
                name="Ingest Documents",
                description="Ingest documents into the system",
                config={
                    "task": {
                        "type": "ingest",
                        "data": {"document_paths": "${document_paths}"},
                    }
                },
                required_capabilities=[AgentCapability.DOCUMENT_PROCESSING],
            ),
            WorkflowStep(
                step_id="extract_metadata",
                step_type=WorkflowStepType.AGENT_TASK,
                name="Extract Metadata",
                description="Extract metadata from documents",
                config={
                    "task": {
                        "type": "extract_metadata",
                        "data": {
                            "document_ids": "${step_ingest_documents_result.document_ids}"
                        },
                    }
                },
                dependencies=["ingest_documents"],
                required_capabilities=[AgentCapability.DOCUMENT_ANALYSIS],
            ),
            WorkflowStep(
                step_id="classify_documents",
                step_type=WorkflowStepType.AGENT_TASK,
                name="Classify Documents",
                description="Classify documents by type",
                config={
                    "task": {
                        "type": "classify",
                        "data": {
                            "document_ids": "${step_extract_metadata_result.document_ids}"
                        },
                    }
                },
                dependencies=["extract_metadata"],
                required_capabilities=[AgentCapability.DOCUMENT_ANALYSIS],
            ),
            WorkflowStep(
                step_id="index_documents",
                step_type=WorkflowStepType.AGENT_TASK,
                name="Index Documents",
                description="Index documents for search",
                config={
                    "task": {
                        "type": "index",
                        "data": {
                            "document_ids": "${step_classify_documents_result.document_ids}"
                        },
                    }
                },
                dependencies=["classify_documents"],
                required_capabilities=[AgentCapability.INFORMATION_RETRIEVAL],
            ),
        ],
        input_schema={
            "required": ["document_paths"],
            "properties": {
                "document_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Paths to documents to process",
                }
            },
        },
        output_schema={
            "properties": {
                "indexed_documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "IDs of indexed documents",
                }
            }
        },
    )


# Utility functions
async def create_workflow_engine(orchestrator: AgentOrchestrator) -> WorkflowEngine:
    """
    Create a workflow engine with default workflows.

    Args:
        orchestrator: Agent orchestrator

    Returns:
        Workflow engine instance
    """
    engine = WorkflowEngine(orchestrator)

    # Register default workflows
    engine.register_workflow(create_research_workflow())
    engine.register_workflow(create_document_processing_workflow())

    return engine


async def execute_research_workflow(
    engine: WorkflowEngine, query: str, execution_id: Optional[str] = None
) -> str:
    """
    Execute a research workflow.

    Args:
        engine: Workflow engine
        query: Research query
        execution_id: Optional execution ID

    Returns:
        Execution ID
    """
    input_data = {"query": query}
    return await engine.execute_workflow(
        "research_workflow_v1", input_data, execution_id
    )


async def execute_document_processing_workflow(
    engine: WorkflowEngine,
    document_paths: List[str],
    execution_id: Optional[str] = None,
) -> str:
    """
    Execute a document processing workflow.

    Args:
        engine: Workflow engine
        document_paths: List of document paths
        execution_id: Optional execution ID

    Returns:
        Execution ID
    """
    input_data = {"document_paths": document_paths}
    return await engine.execute_workflow(
        "document_processing_workflow_v1", input_data, execution_id
    )
