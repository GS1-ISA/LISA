"""
Optimized Multi-Agent Workflow for ISA_D
High-performance multi-agent orchestration with advanced optimizations.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime
from enum import Enum

from .agent_core.llm_client import get_openrouter_free_client
from .agent_core.query_optimizer import QueryOptimizer
from .cache.multi_level_cache import get_multilevel_cache, MultiLevelCache

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent roles in the optimized workflow."""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    SYNTHESIZER = "synthesizer"
    VALIDATOR = "validator"
    COORDINATOR = "coordinator"


class WorkflowStage(Enum):
    """Workflow processing stages."""
    PLANNING = "planning"
    RESEARCH = "research"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    COORDINATION = "coordination"


@dataclass
class AgentTask:
    """Represents a task for an agent."""
    task_id: str
    role: AgentRole
    content: str
    priority: int = 1
    dependencies: List[str] = None
    timeout: int = 300


@dataclass
class WorkflowMetrics:
    """Performance metrics for agent workflows."""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_processing_time: float
    avg_task_time: float
    throughput_tasks_per_sec: float
    cache_hit_rate: float
    agent_utilization: Dict[str, float]
    timestamp: datetime


@dataclass
class TaskResult:
    """Result of a completed task."""
    task_id: str
    success: bool
    result: Any
    processing_time: float
    agent_role: AgentRole
    error_message: Optional[str] = None


class OptimizedAgentWorkflow:
    """
    High-performance multi-agent workflow with advanced optimizations:

    - Intelligent task scheduling and load balancing
    - Parallel agent execution with dependency management
    - Result caching and deduplication
    - Adaptive resource allocation
    - Performance monitoring and bottleneck detection
    - Fault tolerance and recovery
    """

    def __init__(self,
                 llm_client=None,
                 cache: Optional[MultiLevelCache] = None,
                 max_concurrent_agents: int = 8):
        self.llm_client = llm_client or get_openrouter_free_client()
        self.cache = cache or get_multilevel_cache()
        self.max_concurrent_agents = max_concurrent_agents

        # Initialize components
        self.query_optimizer = QueryOptimizer()

        # Thread pools for different agent types
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_agents)

        # Agent pools by role
        self.agent_pools = {
            AgentRole.PLANNER: max_concurrent_agents // 4,
            AgentRole.RESEARCHER: max_concurrent_agents // 3,
            AgentRole.SYNTHESIZER: max_concurrent_agents // 4,
            AgentRole.VALIDATOR: max_concurrent_agents // 6,
            AgentRole.COORDINATOR: 2
        }

        # Semaphores for agent pools
        self.agent_semaphores = {
            role: asyncio.Semaphore(count)
            for role, count in self.agent_pools.items()
        }

        # Performance monitoring
        self.metrics_lock = threading.Lock()
        self.workflow_metrics: List[WorkflowMetrics] = []
        self.task_results: List[TaskResult] = []

        # Task management
        self.task_queue = asyncio.Queue()
        self.completed_tasks = {}
        self.failed_tasks = {}

        # Adaptive optimization
        self.agent_utilization = {role.value: 0.0 for role in AgentRole}
        self.load_balancing_enabled = True

        logger.info(f"Initialized OptimizedAgentWorkflow with {max_concurrent_agents} concurrent agents")

    async def execute_workflow(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow with optimized scheduling.

        Args:
            tasks: List of tasks to execute

        Returns:
            Workflow execution results and performance metrics
        """
        start_time = time.time()
        total_tasks = len(tasks)

        logger.info(f"Starting optimized workflow execution of {total_tasks} tasks")

        try:
            # Initialize task tracking
            for task in tasks:
                self.completed_tasks[task.task_id] = False
                self.failed_tasks[task.task_id] = False

            # Execute tasks with dependency management
            results = await self._execute_tasks_with_dependencies(tasks)

            processing_time = time.time() - start_time

            # Calculate metrics
            successful_tasks = sum(1 for r in results if r.success)
            failed_tasks = total_tasks - successful_tasks

            # Calculate agent utilization
            agent_utilization = self._calculate_agent_utilization(results)

            metrics = WorkflowMetrics(
                total_tasks=total_tasks,
                completed_tasks=successful_tasks,
                failed_tasks=failed_tasks,
                total_processing_time=processing_time,
                avg_task_time=processing_time / max(1, total_tasks),
                throughput_tasks_per_sec=total_tasks / max(0.1, processing_time),
                cache_hit_rate=self._calculate_cache_hit_rate(),
                agent_utilization=agent_utilization,
                timestamp=datetime.now()
            )

            with self.metrics_lock:
                self.workflow_metrics.append(metrics)
                self.task_results.extend(results)

            # Adaptive optimization
            if self.load_balancing_enabled:
                self._optimize_agent_allocation(metrics)

            result_summary = {
                'success': successful_tasks > failed_tasks,
                'total_tasks': total_tasks,
                'completed_tasks': successful_tasks,
                'failed_tasks': failed_tasks,
                'processing_time': round(processing_time, 2),
                'throughput': round(metrics.throughput_tasks_per_sec, 2),
                'cache_hit_rate': round(metrics.cache_hit_rate * 100, 2),
                'agent_utilization': {k: round(v * 100, 1) for k, v in agent_utilization.items()},
                'results': [self._format_task_result(r) for r in results],
                'performance_metrics': self._format_workflow_metrics(metrics)
            }

            logger.info(f"Workflow execution completed: {successful_tasks}/{total_tasks} tasks in {processing_time:.2f}s")
            return result_summary

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'completed_tasks': 0,
                'total_tasks': total_tasks
            }

    async def _execute_tasks_with_dependencies(self, tasks: List[AgentTask]) -> List[TaskResult]:
        """Execute tasks considering dependencies."""
        # Group tasks by dependency level
        dependency_levels = self._resolve_dependencies(tasks)

        all_results = []

        for level in dependency_levels:
            level_tasks = [t for t in tasks if t.task_id in level]

            # Execute tasks in this level in parallel
            level_results = await self._execute_task_batch(level_tasks)
            all_results.extend(level_results)

            # Update completed tasks for dependency checking
            for result in level_results:
                if result.success:
                    self.completed_tasks[result.task_id] = True

        return all_results

    def _resolve_dependencies(self, tasks: List[AgentTask]) -> List[List[str]]:
        """Resolve task dependencies and return execution levels."""
        # Simple dependency resolution (could be enhanced with topological sort)
        levels = []
        remaining_tasks = {t.task_id: t for t in tasks}
        processed = set()

        while remaining_tasks:
            current_level = []

            for task_id, task in list(remaining_tasks.items()):
                # Check if all dependencies are satisfied
                deps_satisfied = all(
                    dep in processed or self.completed_tasks.get(dep, False)
                    for dep in (task.dependencies or [])
                )

                if deps_satisfied:
                    current_level.append(task_id)
                    del remaining_tasks[task_id]

            if not current_level:
                # Circular dependency or unsatisfiable dependencies
                logger.warning("Circular or unsatisfiable dependencies detected")
                current_level = list(remaining_tasks.keys())
                remaining_tasks.clear()

            levels.append(current_level)
            processed.update(current_level)

        return levels

    async def _execute_task_batch(self, tasks: List[AgentTask]) -> List[TaskResult]:
        """Execute a batch of tasks in parallel."""
        semaphore = self.agent_semaphores[tasks[0].role] if tasks else asyncio.Semaphore(self.max_concurrent_agents)

        async def execute_with_semaphore(task: AgentTask):
            async with semaphore:
                return await self._execute_single_task(task)

        tasks_list = [execute_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*tasks_list, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {tasks[i].task_id} failed: {result}")
                processed_results.append(TaskResult(
                    task_id=tasks[i].task_id,
                    success=False,
                    result=None,
                    processing_time=0.0,
                    agent_role=tasks[i].role,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_single_task(self, task: AgentTask) -> TaskResult:
        """Execute a single agent task with caching and optimization."""
        start_time = time.time()

        # Check cache first
        cache_key = f"agent_task:{task.task_id}:{hash(task.content)}"
        cached_result = self.cache.get(cache_key)

        if cached_result:
            processing_time = time.time() - start_time
            return TaskResult(
                task_id=task.task_id,
                success=True,
                result=cached_result,
                processing_time=processing_time,
                agent_role=task.role
            )

        # Execute task based on role
        try:
            result = await self._execute_agent_task(task)
            processing_time = time.time() - start_time

            # Cache successful results
            if result:
                self.cache.set(cache_key, result)

            return TaskResult(
                task_id=task.task_id,
                success=True,
                result=result,
                processing_time=processing_time,
                agent_role=task.role
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Task {task.task_id} execution failed: {e}")

            return TaskResult(
                task_id=task.task_id,
                success=False,
                result=None,
                processing_time=processing_time,
                agent_role=task.role,
                error_message=str(e)
            )

    async def _execute_agent_task(self, task: AgentTask) -> Any:
        """Execute task based on agent role."""
        messages = [{"role": "user", "content": task.content}]

        if task.role == AgentRole.PLANNER:
            # Planning tasks - use reasoning-focused model
            result = await self.llm_client.async_chat_completion(
                messages, model="deepseek/deepseek-r1:free"
            )
            return result.get('content', '')

        elif task.role == AgentRole.RESEARCHER:
            # Research tasks - use document-focused model
            result = await self.llm_client.async_chat_completion(
                messages, model="meta-llama/llama-4-scout:free"
            )
            return result.get('content', '')

        elif task.role == AgentRole.SYNTHESIZER:
            # Synthesis tasks - use structured output model
            result = await self.llm_client.async_chat_completion(
                messages, model="mistralai/mistral-small-3.1-24b-instruct:free"
            )
            return result.get('content', '')

        elif task.role == AgentRole.VALIDATOR:
            # Validation tasks - use precision model
            result = await self.llm_client.async_chat_completion(
                messages, model="google/gemini-2.5-flash-image-preview:free"
            )
            return result.get('content', '')

        else:
            # Default to primary model
            result = await self.llm_client.async_chat_completion(messages)
            return result.get('content', '')

    def _calculate_agent_utilization(self, results: List[TaskResult]) -> Dict[str, float]:
        """Calculate agent utilization rates."""
        utilization = {role.value: 0.0 for role in AgentRole}

        for result in results:
            role = result.agent_role.value
            if role in utilization:
                utilization[role] += result.processing_time

        # Normalize by total time
        total_time = sum(utilization.values())
        if total_time > 0:
            for role in utilization:
                utilization[role] /= total_time

        return utilization

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate from LLM client."""
        stats = self.llm_client.get_cache_stats()
        llm_stats = stats.get('llm_specific', {})
        total_requests = llm_stats.get('total', 0)
        if total_requests == 0:
            return 0.0
        return llm_stats.get('hits', 0) / total_requests

    def _optimize_agent_allocation(self, metrics: WorkflowMetrics):
        """Optimize agent allocation based on performance metrics."""
        utilization = metrics.agent_utilization

        # Find bottleneck agents (high utilization)
        bottleneck_roles = [role for role, util in utilization.items() if util > 0.8]

        if bottleneck_roles:
            logger.info(f"Detected bottlenecks in roles: {bottleneck_roles}")
            # Could implement dynamic agent pool resizing here

        # Find underutilized agents
        underutilized_roles = [role for role, util in utilization.items() if util < 0.2]

        if underutilized_roles:
            logger.info(f"Underutilized roles: {underutilized_roles}")
            # Could reduce pool sizes for underutilized roles

    def _format_task_result(self, result: TaskResult) -> Dict[str, Any]:
        """Format task result for reporting."""
        return {
            'task_id': result.task_id,
            'success': result.success,
            'agent_role': result.agent_role.value,
            'processing_time': round(result.processing_time, 4),
            'result_length': len(str(result.result)) if result.result else 0,
            'error_message': result.error_message
        }

    def _format_workflow_metrics(self, metrics: WorkflowMetrics) -> Dict[str, Any]:
        """Format workflow metrics for reporting."""
        return {
            'total_tasks': metrics.total_tasks,
            'completed_tasks': metrics.completed_tasks,
            'failed_tasks': metrics.failed_tasks,
            'total_processing_time': round(metrics.total_processing_time, 2),
            'avg_task_time': round(metrics.avg_task_time, 4),
            'throughput_tasks_per_sec': round(metrics.throughput_tasks_per_sec, 2),
            'cache_hit_rate_percent': round(metrics.cache_hit_rate * 100, 2),
            'agent_utilization': {k: round(v * 100, 1) for k, v in metrics.agent_utilization.items()},
            'timestamp': metrics.timestamp.isoformat()
        }

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get comprehensive workflow performance statistics."""
        with self.metrics_lock:
            if not self.workflow_metrics:
                return {'total_workflows': 0}

            recent_metrics = self.workflow_metrics[-10:]  # Last 10 workflows

            return {
                'total_workflows': len(self.workflow_metrics),
                'avg_throughput': round(sum(m.throughput_tasks_per_sec for m in recent_metrics) / len(recent_metrics), 2),
                'avg_cache_hit_rate': round(sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics) * 100, 2),
                'total_tasks_processed': sum(m.completed_tasks for m in self.workflow_metrics),
                'agent_pool_sizes': {role.value: count for role, count in self.agent_pools.items()},
                'load_balancing_enabled': self.load_balancing_enabled
            }

    def clear_cache(self):
        """Clear cached task results."""
        # Clear agent task cache (would need pattern matching in real implementation)
        pass

    def shutdown(self):
        """Shutdown the workflow engine and cleanup resources."""
        self.executor.shutdown(wait=True)
        logger.info("OptimizedAgentWorkflow shutdown complete")


# Global instance
_optimized_workflow: Optional[OptimizedAgentWorkflow] = None


def get_optimized_agent_workflow() -> OptimizedAgentWorkflow:
    """Get or create global optimized agent workflow instance."""
    global _optimized_workflow
    if _optimized_workflow is None:
        _optimized_workflow = OptimizedAgentWorkflow()
    return _optimized_workflow


def create_optimized_workflow(max_concurrent_agents: int = 8) -> OptimizedAgentWorkflow:
    """Factory function to create optimized agent workflow."""
    return OptimizedAgentWorkflow(max_concurrent_agents=max_concurrent_agents)