"""
Metrics collection for ISA SuperApp.
"""

import time
from collections import defaultdict
from typing import Any


class MetricType:
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MetricsCollector:
    """Collects and manages application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self._counters = defaultdict(int)
        self._gauges = {}
        self._histograms = defaultdict(list)
        self._timers = defaultdict(list)

    def increment(self, name: str, value: int = 1, labels: dict[str, Any] | None = None) -> None:
        """Increment a counter metric."""
        key = self._make_key(name, labels)
        self._counters[key] += value

    def set_gauge(self, name: str, value: float, labels: dict[str, Any] | None = None) -> None:
        """Set a gauge metric."""
        key = self._make_key(name, labels)
        self._gauges[key] = value

    def record_histogram(self, name: str, value: float, labels: dict[str, Any] | None = None) -> None:
        """Record a histogram value."""
        key = self._make_key(name, labels)
        self._histograms[key].append(value)

    def get_metric(self, name: str, labels: dict[str, Any] | None = None) -> Any:
        """Get a metric value."""
        key = self._make_key(name, labels)
        if key in self._counters:
            return self._counters[key]
        elif key in self._gauges:
            return self._gauges[key]
        return None

    def get_histogram_stats(self, name: str, labels: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get histogram statistics."""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}

        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
        # Return flattened metrics for backward compatibility
        all_metrics = {}

        # Add counters
        for key, value in self._counters.items():
            all_metrics[key] = value

        # Add gauges
        for key, value in self._gauges.items():
            all_metrics[key] = value

        # Add histogram stats
        for key, values in self._histograms.items():
            if values:
                all_metrics[key] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                }
            else:
                all_metrics[key] = []

        return all_metrics

    def timer(self, name: str, labels: dict[str, Any] | None = None):
        """Context manager for timing operations."""
        return TimerContext(self, name, labels)

    def _make_key(self, name: str, labels: dict[str, Any] | None = None) -> str:
        """Make a unique key for a metric."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}@{label_str}"


class TimerContext:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector, name: str, labels: dict[str, Any] | None = None):
        """Initialize timer context."""
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        """Enter the context."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.collector.record_histogram(self.name, duration, self.labels)
