"""
Advanced Monitoring and Metrics System for ISA SuperApp
Provides comprehensive observability with performance metrics, error rates,
business KPIs, system health, and ISA-specific metrics.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import psutil
from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    WARNING = "warning"

class ResearchWorkflowStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SystemHealth:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_connections: int
    timestamp: datetime

@dataclass
class ISAMetrics:
    compliance_checks: int
    compliance_violations: int
    research_workflows_started: int
    research_workflows_completed: int
    active_users: int
    user_sessions: int
    engagement_score: float

class MonitoringSystem:
    """
    Comprehensive monitoring system for ISA SuperApp with advanced observability.
    Tracks performance, errors, business KPIs, system health, and ISA-specific metrics.
    """

    def __init__(self, registry: CollectorRegistry | None = None):
        from prometheus_client import REGISTRY
        self.registry = registry or REGISTRY
        self._initialized = False
        self._init_metrics()

    def _init_metrics(self):
        """Initialize all Prometheus metrics."""
        if self._initialized:
            return

        # Performance Metrics
        self.http_request_duration = Histogram(
            "isa_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint", "status_code"],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry
        )

        self.http_requests_total = Counter(
            "isa_http_requests_total",
            "Total number of HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry
        )

        self.database_query_duration = Histogram(
            "isa_database_query_duration_seconds",
            "Database query duration in seconds",
            ["operation", "table"],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
            registry=self.registry
        )

        # Error Rate Metrics
        self.errors_total = Counter(
            "isa_errors_total",
            "Total number of errors",
            ["error_type", "component", "severity"],
            registry=self.registry
        )

        self.error_rate = Gauge(
            "isa_error_rate_percent",
            "Current error rate as percentage",
            ["component", "time_window"],
            registry=self.registry
        )

        # Business KPIs
        self.business_kpis = Gauge(
            "isa_business_kpi",
            "Business Key Performance Indicators",
            ["kpi_name", "category"],
            registry=self.registry
        )

        self.user_registrations = Counter(
            "isa_user_registrations_total",
            "Total user registrations",
            ["source", "user_type"],
            registry=self.registry
        )

        self.revenue_total = Counter(
            "isa_revenue_total_usd",
            "Total revenue in USD",
            ["revenue_type", "currency"],
            registry=self.registry
        )

        # System Health Metrics
        self.system_cpu_percent = Gauge(
            "isa_system_cpu_percent",
            "System CPU usage percentage",
            registry=self.registry
        )

        self.system_memory_percent = Gauge(
            "isa_system_memory_percent",
            "System memory usage percentage",
            registry=self.registry
        )

        self.system_disk_percent = Gauge(
            "isa_system_disk_percent",
            "System disk usage percentage",
            ["mount_point"],
            registry=self.registry
        )

        self.system_network_connections = Gauge(
            "isa_system_network_connections",
            "Number of active network connections",
            registry=self.registry
        )

        # ISA-Specific Metrics
        # Compliance Analysis
        self.compliance_checks_total = Counter(
            "isa_compliance_checks_total",
            "Total compliance checks performed",
            ["check_type", "status"],
            registry=self.registry
        )

        self.compliance_violations = Gauge(
            "isa_compliance_violations_current",
            "Current number of active compliance violations",
            ["violation_type", "severity"],
            registry=self.registry
        )

        # Research Workflows
        self.research_workflows_total = Counter(
            "isa_research_workflows_total",
            "Total research workflows",
            ["status", "workflow_type"],
            registry=self.registry
        )

        self.research_workflow_duration = Histogram(
            "isa_research_workflow_duration_seconds",
            "Research workflow duration in seconds",
            ["workflow_type", "status"],
            buckets=(60, 300, 600, 1800, 3600, 7200, 14400),  # 1min to 4hrs
            registry=self.registry
        )

        # User Engagement
        self.active_users = Gauge(
            "isa_active_users_current",
            "Current number of active users",
            ["user_type", "activity_type"],
            registry=self.registry
        )

        self.user_sessions_total = Counter(
            "isa_user_sessions_total",
            "Total user sessions",
            ["session_type", "user_type"],
            registry=self.registry
        )

        self.user_engagement_score = Gauge(
            "isa_user_engagement_score",
            "User engagement score (0-100)",
            ["metric_type"],
            registry=self.registry
        )

        self.session_duration = Histogram(
            "isa_user_session_duration_seconds",
            "User session duration in seconds",
            ["user_type", "session_type"],
            buckets=(60, 300, 600, 1800, 3600, 7200),  # 1min to 2hrs
            registry=self.registry
        )

        # Cache Performance
        self.cache_hit_rate = Gauge(
            "isa_cache_hit_rate_percent",
            "Cache hit rate percentage",
            ["cache_type"],
            registry=self.registry
        )

        # Agent Performance
        self.agent_operations_total = Counter(
            "isa_agent_operations_total",
            "Total agent operations",
            ["agent_type", "operation_type", "status"],
            registry=self.registry
        )

        self.agent_response_time = Histogram(
            "isa_agent_response_time_seconds",
            "Agent response time in seconds",
            ["agent_type", "operation_type"],
            buckets=(1, 5, 10, 30, 60, 120, 300),
            registry=self.registry
        )

        self._initialized = True
        logger.info("MonitoringSystem metrics initialized")

    # Performance Metrics Methods
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_request_duration.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).observe(duration)

        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

    def record_database_query(self, operation: str, table: str, duration: float):
        """Record database query metrics."""
        self.database_query_duration.labels(
            operation=operation, table=table
        ).observe(duration)

    # Error Tracking Methods
    def record_error(self, error_type: str, component: str, severity: str = "error"):
        """Record an error occurrence."""
        self.errors_total.labels(
            error_type=error_type, component=component, severity=severity
        ).inc()

    def update_error_rate(self, component: str, error_rate: float, time_window: str = "5m"):
        """Update error rate for a component."""
        self.error_rate.labels(
            component=component, time_window=time_window
        ).set(error_rate)

    # Business KPIs Methods
    def update_business_kpi(self, kpi_name: str, value: float, category: str = "general"):
        """Update business KPI value."""
        self.business_kpis.labels(
            kpi_name=kpi_name, category=category
        ).set(value)

    def record_user_registration(self, source: str = "web", user_type: str = "standard"):
        """Record a user registration."""
        self.user_registrations.labels(
            source=source, user_type=user_type
        ).inc()

    def record_revenue(self, amount: float, revenue_type: str = "subscription", currency: str = "USD"):
        """Record revenue."""
        self.revenue_total.labels(
            revenue_type=revenue_type, currency=currency
        ).inc(amount)

    # System Health Methods
    def collect_system_health(self) -> SystemHealth:
        """Collect current system health metrics."""
        health = SystemHealth(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage("/").percent,
            network_connections=len(psutil.net_connections()),
            timestamp=datetime.now()
        )

        # Update Prometheus metrics
        self.system_cpu_percent.set(health.cpu_percent)
        self.system_memory_percent.set(health.memory_percent)
        self.system_disk_percent.labels(mount_point="/").set(health.disk_percent)
        self.system_network_connections.set(health.network_connections)

        return health

    # ISA-Specific Methods
    def record_compliance_check(self, check_type: str, status: ComplianceStatus):
        """Record a compliance check."""
        self.compliance_checks_total.labels(
            check_type=check_type, status=status.value
        ).inc()

        if status == ComplianceStatus.VIOLATION:
            self.compliance_violations.labels(
                violation_type=check_type, severity="high"
            ).inc()

    def update_compliance_violations(self, violation_type: str, count: int, severity: str = "medium"):
        """Update current compliance violations count."""
        self.compliance_violations.labels(
            violation_type=violation_type, severity=severity
        ).set(count)

    def record_research_workflow(self, workflow_type: str, status: ResearchWorkflowStatus, duration: float | None = None):
        """Record research workflow metrics."""
        self.research_workflows_total.labels(
            status=status.value, workflow_type=workflow_type
        ).inc()

        if duration is not None:
            self.research_workflow_duration.labels(
                workflow_type=workflow_type, status=status.value
            ).observe(duration)

    def update_active_users(self, count: int, user_type: str = "all", activity_type: str = "active"):
        """Update active users count."""
        self.active_users.labels(
            user_type=user_type, activity_type=activity_type
        ).set(count)

    def record_user_session(self, session_type: str = "web", user_type: str = "standard"):
        """Record a user session."""
        self.user_sessions_total.labels(
            session_type=session_type, user_type=user_type
        ).inc()

    def record_session_duration(self, duration: float, user_type: str = "standard", session_type: str = "web"):
        """Record user session duration."""
        self.session_duration.labels(
            user_type=user_type, session_type=session_type
        ).observe(duration)

    def update_engagement_score(self, score: float, metric_type: str = "overall"):
        """Update user engagement score."""
        self.user_engagement_score.labels(metric_type=metric_type).set(score)

    def update_cache_hit_rate(self, hit_rate: float, cache_type: str = "redis"):
        """Update cache hit rate."""
        self.cache_hit_rate.labels(cache_type=cache_type).set(hit_rate)

    def record_agent_operation(self, agent_type: str, operation_type: str, status: str = "success"):
        """Record agent operation."""
        self.agent_operations_total.labels(
            agent_type=agent_type, operation_type=operation_type, status=status
        ).inc()

    def record_agent_response_time(self, agent_type: str, operation_type: str, duration: float):
        """Record agent response time."""
        self.agent_response_time.labels(
            agent_type=agent_type, operation_type=operation_type
        ).observe(duration)

    def get_metrics_response(self) -> Response:
        """Get Prometheus metrics as HTTP response."""
        data = generate_latest(self.registry)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    async def start_health_monitoring(self, interval_seconds: int = 30):
        """Start periodic system health monitoring."""
        while True:
            try:
                self.collect_system_health()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error collecting system health metrics: {e}")
                await asyncio.sleep(interval_seconds)

    def get_isa_metrics_summary(self) -> ISAMetrics:
        """Get current ISA-specific metrics summary."""
        # This would typically query the registry for current values
        # For now, return a placeholder structure
        return ISAMetrics(
            compliance_checks=0,  # Would query actual metrics
            compliance_violations=0,
            research_workflows_started=0,
            research_workflows_completed=0,
            active_users=0,
            user_sessions=0,
            engagement_score=0.0
        )

# Global monitoring system instance
monitoring_system = MonitoringSystem()
