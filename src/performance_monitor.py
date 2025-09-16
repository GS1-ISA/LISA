"""
Performance Monitoring and Alerting System for ISA_D
Comprehensive performance monitoring with intelligent alerting and optimization recommendations.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics

from .cache.multi_level_cache import get_multilevel_cache
from .docs_provider.optimized_processor import get_optimized_document_processor
from .optimized_pipeline import get_optimized_regulatory_pipeline
from .optimized_graph_analytics import get_optimized_graph_analytics
from .optimized_agent_workflow import get_optimized_agent_workflow

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of performance metrics."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_USAGE = "memory_usage"
    ERROR_RATE = "error_rate"
    RESOURCE_UTILIZATION = "resource_utilization"


@dataclass
class PerformanceAlert:
    """Performance alert with context and recommendations."""
    alert_id: str
    severity: AlertSeverity
    metric_type: MetricType
    component: str
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    recommendations: List[str]
    context: Dict[str, Any]


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics snapshot."""
    timestamp: datetime
    document_processing: Dict[str, Any]
    pipeline_performance: Dict[str, Any]
    graph_analytics: Dict[str, Any]
    agent_workflow: Dict[str, Any]
    cache_performance: Dict[str, Any]
    system_resources: Dict[str, Any]


class PerformanceMonitor:
    """
    Advanced performance monitoring system with:

    - Real-time metrics collection
    - Intelligent alerting with thresholds
    - Performance trend analysis
    - Automated optimization recommendations
    - Historical performance tracking
    - Anomaly detection
    """

    def __init__(self,
                 monitoring_interval: int = 60,
                 alert_cooldown: int = 300,
                 enable_anomaly_detection: bool = True):
        self.monitoring_interval = monitoring_interval
        self.alert_cooldown = alert_cooldown
        self.enable_anomaly_detection = enable_anomaly_detection

        # Component references
        self.cache = get_multilevel_cache()
        self.doc_processor = get_optimized_document_processor()
        self.pipeline = get_optimized_regulatory_pipeline()
        self.analytics = get_optimized_graph_analytics()
        self.workflow = get_optimized_agent_workflow()

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_history: List[PerformanceMetrics] = []
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []

        # Alert thresholds
        self.thresholds = {
            'latency_p95': {'warning': 2.0, 'error': 5.0, 'critical': 10.0},
            'throughput_min': {'warning': 5.0, 'error': 2.0, 'critical': 1.0},
            'cache_hit_rate_min': {'warning': 0.7, 'error': 0.5, 'critical': 0.3},
            'memory_usage_max': {'warning': 0.8, 'error': 0.9, 'critical': 0.95},
            'error_rate_max': {'warning': 0.05, 'error': 0.1, 'critical': 0.2}
        }

        # Anomaly detection
        self.anomaly_detector = AnomalyDetector() if enable_anomaly_detection else None

        # Locks
        self.metrics_lock = threading.Lock()
        self.alerts_lock = threading.Lock()

        logger.info("Initialized PerformanceMonitor")

    def start_monitoring(self):
        """Start the performance monitoring system."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop the performance monitoring system."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)

        logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = self._collect_metrics()

                with self.metrics_lock:
                    self.metrics_history.append(metrics)

                    # Keep only recent history (last 1000 entries)
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]

                # Check for alerts
                self._check_alerts(metrics)

                # Anomaly detection
                if self.anomaly_detector:
                    anomalies = self.anomaly_detector.detect_anomalies(metrics)
                    for anomaly in anomalies:
                        self._create_anomaly_alert(anomaly)

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")

            time.sleep(self.monitoring_interval)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive performance metrics."""
        timestamp = datetime.now()

        return PerformanceMetrics(
            timestamp=timestamp,
            document_processing=self._get_document_processing_metrics(),
            pipeline_performance=self._get_pipeline_metrics(),
            graph_analytics=self._get_graph_analytics_metrics(),
            agent_workflow=self._get_agent_workflow_metrics(),
            cache_performance=self._get_cache_metrics(),
            system_resources=self._get_system_resources()
        )

    def _get_document_processing_metrics(self) -> Dict[str, Any]:
        """Get document processing performance metrics."""
        try:
            stats = self.doc_processor.get_performance_stats()
            return {
                'total_processed': stats.get('total_processed', 0),
                'cache_hit_rate': stats.get('cache_hit_rate', 0.0),
                'avg_processing_time': stats.get('avg_processing_time', 0.0),
                'p95_processing_time': stats.get('p95_processing_time', 0.0),
                'avg_chunk_count': stats.get('avg_chunk_count', 0),
                'thread_pool_workers': stats.get('thread_pool_workers', 0)
            }
        except Exception as e:
            logger.warning(f"Failed to get document processing metrics: {e}")
            return {'error': str(e)}

    def _get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get regulatory pipeline performance metrics."""
        try:
            stats = self.pipeline.get_pipeline_stats()
            return {
                'total_runs': stats.get('total_runs', 0),
                'avg_throughput': stats.get('avg_throughput', 0.0),
                'avg_cache_hit_rate': stats.get('avg_cache_hit_rate', 0.0),
                'total_documents_processed': stats.get('total_documents_processed', 0),
                'circuit_breaker_status': stats.get('circuit_breaker_status', 'unknown'),
                'current_batch_size': stats.get('current_batch_size', 0),
                'failure_count': stats.get('failure_count', 0)
            }
        except Exception as e:
            logger.warning(f"Failed to get pipeline metrics: {e}")
            return {'error': str(e)}

    def _get_graph_analytics_metrics(self) -> Dict[str, Any]:
        """Get graph analytics performance metrics."""
        try:
            stats = self.analytics.get_performance_stats()
            return {
                'total_queries': stats.get('total_queries', 0),
                'cache_hit_rate': stats.get('cache_hit_rate', 0.0),
                'avg_query_time': stats.get('avg_query_time', 0.0),
                'p95_query_time': stats.get('p95_query_time', 0.0),
                'avg_nodes_processed': stats.get('avg_nodes_processed', 0),
                'avg_edges_processed': stats.get('avg_edges_processed', 0),
                'concurrent_queries_max': stats.get('concurrent_queries_max', 0)
            }
        except Exception as e:
            logger.warning(f"Failed to get graph analytics metrics: {e}")
            return {'error': str(e)}

    def _get_agent_workflow_metrics(self) -> Dict[str, Any]:
        """Get agent workflow performance metrics."""
        try:
            stats = self.workflow.get_workflow_stats()
            return {
                'total_workflows': stats.get('total_workflows', 0),
                'avg_throughput': stats.get('avg_throughput', 0.0),
                'avg_cache_hit_rate': stats.get('avg_cache_hit_rate', 0.0),
                'total_tasks_processed': stats.get('total_tasks_processed', 0),
                'agent_pool_sizes': stats.get('agent_pool_sizes', {}),
                'load_balancing_enabled': stats.get('load_balancing_enabled', False)
            }
        except Exception as e:
            logger.warning(f"Failed to get agent workflow metrics: {e}")
            return {'error': str(e)}

    def _get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        try:
            stats = self.cache.get_stats()
            return {
                'overall_hit_rate': stats.get('overall_hit_rate', 0.0),
                'l1_hit_rate': stats.get('l1_hit_rate', 0.0),
                'l2_hit_rate': stats.get('l2_hit_rate', 0.0),
                'l3_hit_rate': stats.get('l3_hit_rate', 0.0),
                'total_requests': stats.get('total_requests', 0),
                'l1_stats': stats.get('l1_stats', {}),
                'l2_stats': stats.get('l2_stats', {}),
                'l3_stats': stats.get('l3_stats', {})
            }
        except Exception as e:
            logger.warning(f"Failed to get cache metrics: {e}")
            return {'error': str(e)}

    def _get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage metrics."""
        try:
            import psutil
            process = psutil.Process()

            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'process_memory_mb': process.memory_info().rss / 1024 / 1024,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections())
            }
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            logger.warning(f"Failed to get system resources: {e}")
            return {'error': str(e)}

    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check metrics against thresholds and create alerts."""
        # Document processing alerts
        self._check_latency_alert(metrics.document_processing, 'document_processing')
        self._check_cache_hit_rate_alert(metrics.document_processing, 'document_processing')

        # Pipeline alerts
        self._check_throughput_alert(metrics.pipeline_performance, 'pipeline')
        self._check_error_rate_alert(metrics.pipeline_performance, 'pipeline')

        # Graph analytics alerts
        self._check_latency_alert(metrics.graph_analytics, 'graph_analytics')

        # Agent workflow alerts
        self._check_throughput_alert(metrics.agent_workflow, 'agent_workflow')

        # System resource alerts
        self._check_memory_alert(metrics.system_resources, 'system')

    def _check_latency_alert(self, component_metrics: Dict[str, Any], component: str):
        """Check latency thresholds and create alerts."""
        p95_time = component_metrics.get('p95_processing_time') or component_metrics.get('p95_query_time')
        if p95_time is None:
            return

        thresholds = self.thresholds['latency_p95']
        severity = None

        if p95_time >= thresholds['critical']:
            severity = AlertSeverity.CRITICAL
        elif p95_time >= thresholds['error']:
            severity = AlertSeverity.ERROR
        elif p95_time >= thresholds['warning']:
            severity = AlertSeverity.WARNING

        if severity:
            self._create_alert(
                severity=severity,
                metric_type=MetricType.LATENCY,
                component=component,
                message=f"High P95 latency: {p95_time:.2f}s (threshold: {thresholds[severity.value]}s)",
                current_value=p95_time,
                threshold_value=thresholds[severity.value],
                recommendations=self._get_latency_recommendations(component)
            )

    def _check_throughput_alert(self, component_metrics: Dict[str, Any], component: str):
        """Check throughput thresholds and create alerts."""
        throughput = component_metrics.get('avg_throughput')
        if throughput is None:
            return

        thresholds = self.thresholds['throughput_min']
        severity = None

        if throughput <= thresholds['critical']:
            severity = AlertSeverity.CRITICAL
        elif throughput <= thresholds['error']:
            severity = AlertSeverity.ERROR
        elif throughput <= thresholds['warning']:
            severity = AlertSeverity.WARNING

        if severity:
            self._create_alert(
                severity=severity,
                metric_type=MetricType.THROUGHPUT,
                component=component,
                message=f"Low throughput: {throughput:.2f} tasks/sec (threshold: {thresholds[severity.value]})",
                current_value=throughput,
                threshold_value=thresholds[severity.value],
                recommendations=self._get_throughput_recommendations(component)
            )

    def _check_cache_hit_rate_alert(self, component_metrics: Dict[str, Any], component: str):
        """Check cache hit rate thresholds and create alerts."""
        hit_rate = component_metrics.get('cache_hit_rate')
        if hit_rate is None:
            return

        thresholds = self.thresholds['cache_hit_rate_min']
        severity = None

        if hit_rate <= thresholds['critical']:
            severity = AlertSeverity.CRITICAL
        elif hit_rate <= thresholds['error']:
            severity = AlertSeverity.ERROR
        elif hit_rate <= thresholds['warning']:
            severity = AlertSeverity.WARNING

        if severity:
            self._create_alert(
                severity=severity,
                metric_type=MetricType.CACHE_HIT_RATE,
                component=component,
                message=f"Low cache hit rate: {hit_rate:.1%} (threshold: {thresholds[severity.value]:.1%})",
                current_value=hit_rate,
                threshold_value=thresholds[severity.value],
                recommendations=self._get_cache_recommendations(component)
            )

    def _check_memory_alert(self, system_metrics: Dict[str, Any], component: str):
        """Check memory usage thresholds and create alerts."""
        memory_percent = system_metrics.get('memory_percent')
        if memory_percent is None:
            return

        thresholds = self.thresholds['memory_usage_max']
        severity = None

        if memory_percent >= thresholds['critical']:
            severity = AlertSeverity.CRITICAL
        elif memory_percent >= thresholds['error']:
            severity = AlertSeverity.ERROR
        elif memory_percent >= thresholds['warning']:
            severity = AlertSeverity.WARNING

        if severity:
            self._create_alert(
                severity=severity,
                metric_type=MetricType.MEMORY_USAGE,
                component=component,
                message=f"High memory usage: {memory_percent:.1f}% (threshold: {thresholds[severity.value]*100:.1f}%)",
                current_value=memory_percent,
                threshold_value=thresholds[severity.value] * 100,
                recommendations=self._get_memory_recommendations()
            )

    def _check_error_rate_alert(self, component_metrics: Dict[str, Any], component: str):
        """Check error rate thresholds and create alerts."""
        failure_count = component_metrics.get('failure_count', 0)
        total_runs = component_metrics.get('total_runs', 1)
        error_rate = failure_count / total_runs if total_runs > 0 else 0

        thresholds = self.thresholds['error_rate_max']
        severity = None

        if error_rate >= thresholds['critical']:
            severity = AlertSeverity.CRITICAL
        elif error_rate >= thresholds['error']:
            severity = AlertSeverity.ERROR
        elif error_rate >= thresholds['warning']:
            severity = AlertSeverity.WARNING

        if severity:
            self._create_alert(
                severity=severity,
                metric_type=MetricType.ERROR_RATE,
                component=component,
                message=f"High error rate: {error_rate:.1%} (threshold: {thresholds[severity.value]:.1%})",
                current_value=error_rate,
                threshold_value=thresholds[severity.value],
                recommendations=self._get_error_rate_recommendations(component)
            )

    def _create_alert(self, severity: AlertSeverity, metric_type: MetricType,
                     component: str, message: str, current_value: float,
                     threshold_value: float, recommendations: List[str]):
        """Create and store a performance alert."""
        alert_id = f"{component}_{metric_type.value}_{int(time.time())}"

        # Check cooldown
        if self._is_alert_cooldown_active(alert_id):
            return

        alert = PerformanceAlert(
            alert_id=alert_id,
            severity=severity,
            metric_type=metric_type,
            component=component,
            message=message,
            current_value=current_value,
            threshold_value=threshold_value,
            timestamp=datetime.now(),
            recommendations=recommendations,
            context={'component': component, 'metric_type': metric_type.value}
        )

        with self.alerts_lock:
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)

            # Keep only recent alerts (last 1000)
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]

        logger.warning(f"Performance Alert [{severity.value.upper()}]: {message}")

    def _create_anomaly_alert(self, anomaly: Dict[str, Any]):
        """Create alert for detected anomaly."""
        self._create_alert(
            severity=AlertSeverity.WARNING,
            metric_type=MetricType.RESOURCE_UTILIZATION,
            component=anomaly.get('component', 'unknown'),
            message=f"Anomaly detected: {anomaly.get('description', 'Unknown anomaly')}",
            current_value=anomaly.get('value', 0),
            threshold_value=anomaly.get('expected_value', 0),
            recommendations=["Investigate anomaly cause", "Check system logs", "Review recent changes"]
        )

    def _is_alert_cooldown_active(self, alert_id: str) -> bool:
        """Check if alert is in cooldown period."""
        with self.alerts_lock:
            for alert in self.alert_history[-10:]:  # Check recent alerts
                if alert.alert_id.startswith(alert_id.split('_')[0]) and \
                   (datetime.now() - alert.timestamp).seconds < self.alert_cooldown:
                    return True
        return False

    def _get_latency_recommendations(self, component: str) -> List[str]:
        """Get latency optimization recommendations."""
        recommendations = [
            "Increase cache size for frequently accessed data",
            "Optimize database queries and indexes",
            "Consider horizontal scaling for high load",
            "Review and optimize algorithm complexity"
        ]

        if component == 'document_processing':
            recommendations.extend([
                "Use parallel processing for batch operations",
                "Implement document pre-processing caching",
                "Optimize chunking strategy for document type"
            ])
        elif component == 'graph_analytics':
            recommendations.extend([
                "Add database indexes for frequently queried relationships",
                "Implement query result caching",
                "Consider graph partitioning for large datasets"
            ])

        return recommendations

    def _get_throughput_recommendations(self, component: str) -> List[str]:
        """Get throughput optimization recommendations."""
        return [
            "Increase concurrent worker threads",
            "Optimize batch processing sizes",
            "Implement request queuing for peak loads",
            "Add load balancing across multiple instances",
            "Review and optimize I/O operations"
        ]

    def _get_cache_recommendations(self, component: str) -> List[str]:
        """Get cache optimization recommendations."""
        return [
            "Increase cache TTL for stable data",
            "Implement cache warming for frequently accessed data",
            "Review cache eviction policies",
            "Add cache compression for large objects",
            "Implement cache prefetching strategies"
        ]

    def _get_memory_recommendations(self) -> List[str]:
        """Get memory optimization recommendations."""
        return [
            "Implement memory-efficient data structures",
            "Add memory limits and garbage collection tuning",
            "Use streaming processing for large datasets",
            "Implement memory pooling for frequent allocations",
            "Add memory monitoring and leak detection"
        ]

    def _get_error_rate_recommendations(self, component: str) -> List[str]:
        """Get error rate reduction recommendations."""
        return [
            "Add comprehensive error handling and retries",
            "Implement circuit breaker pattern",
            "Add input validation and sanitization",
            "Review and fix error-prone code paths",
            "Add monitoring for error patterns"
        ]

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active performance alerts."""
        with self.alerts_lock:
            return [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity.value,
                    'component': alert.component,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'recommendations': alert.recommendations
                }
                for alert in self.active_alerts.values()
            ]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        with self.metrics_lock:
            if not self.metrics_history:
                return {'status': 'no_data'}

            recent_metrics = self.metrics_history[-10:]  # Last 10 measurements

            return {
                'monitoring_active': self.monitoring_active,
                'total_measurements': len(self.metrics_history),
                'active_alerts_count': len(self.active_alerts),
                'avg_cache_hit_rate': round(
                    statistics.mean(m.cache_performance.get('overall_hit_rate', 0) for m in recent_metrics), 2
                ),
                'avg_memory_usage': round(
                    statistics.mean(m.system_resources.get('memory_percent', 0) for m in recent_metrics), 2
                ),
                'total_documents_processed': sum(
                    m.document_processing.get('total_processed', 0) for m in recent_metrics
                ),
                'total_queries_executed': sum(
                    m.graph_analytics.get('total_queries', 0) for m in recent_metrics
                ),
                'total_workflows_executed': sum(
                    m.agent_workflow.get('total_workflows', 0) for m in recent_metrics
                )
            }

    def export_metrics_report(self, filepath: str):
        """Export detailed metrics report to file."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'monitoring_config': {
                'interval': self.monitoring_interval,
                'alert_cooldown': self.alert_cooldown,
                'anomaly_detection_enabled': self.enable_anomaly_detection
            },
            'current_metrics': self.get_performance_summary(),
            'active_alerts': self.get_active_alerts(),
            'recent_history': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'cache_hit_rate': m.cache_performance.get('overall_hit_rate', 0),
                    'memory_usage': m.system_resources.get('memory_percent', 0),
                    'documents_processed': m.document_processing.get('total_processed', 0)
                }
                for m in self.metrics_history[-50:]  # Last 50 measurements
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Metrics report exported to {filepath}")


class AnomalyDetector:
    """Simple anomaly detection for performance metrics."""

    def __init__(self, sensitivity: float = 2.0):
        self.sensitivity = sensitivity
        self.baseline_history = {}
        self.anomaly_history = []

    def detect_anomalies(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """Detect anomalies in performance metrics."""
        anomalies = []

        # Check cache hit rate
        cache_hit_rate = metrics.cache_performance.get('overall_hit_rate', 0)
        if self._is_anomaly('cache_hit_rate', cache_hit_rate):
            anomalies.append({
                'component': 'cache',
                'metric': 'cache_hit_rate',
                'value': cache_hit_rate,
                'expected_value': self.baseline_history.get('cache_hit_rate', cache_hit_rate),
                'description': f"Cache hit rate anomaly: {cache_hit_rate:.1%}"
            })

        # Check memory usage
        memory_usage = metrics.system_resources.get('memory_percent', 0)
        if self._is_anomaly('memory_usage', memory_usage):
            anomalies.append({
                'component': 'system',
                'metric': 'memory_usage',
                'value': memory_usage,
                'expected_value': self.baseline_history.get('memory_usage', memory_usage),
                'description': f"Memory usage anomaly: {memory_usage:.1f}%"
            })

        return anomalies

    def _is_anomaly(self, metric_name: str, current_value: float) -> bool:
        """Check if a value is anomalous."""
        if metric_name not in self.baseline_history:
            self.baseline_history[metric_name] = current_value
            return False

        expected_value = self.baseline_history[metric_name]
        deviation = abs(current_value - expected_value)

        # Update baseline with moving average
        self.baseline_history[metric_name] = (expected_value * 0.9) + (current_value * 0.1)

        # Check if deviation exceeds sensitivity threshold
        return deviation > (expected_value * self.sensitivity * 0.1)


# Global instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def start_performance_monitoring():
    """Start the global performance monitoring system."""
    monitor = get_performance_monitor()
    monitor.start_monitoring()


def stop_performance_monitoring():
    """Stop the global performance monitoring system."""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()