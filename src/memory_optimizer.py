"""
Memory Optimization Module for ISA_D

Provides comprehensive memory management including:
- Garbage collection tuning
- Memory limits and monitoring
- Memory leak detection
- Automatic cleanup routines
"""

import gc
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemoryOptimizer:
    """
    Memory optimization and monitoring system.

    Provides automatic memory management, leak detection, and optimization
    recommendations for the ISA_D application.
    """

    def __init__(
        self,
        memory_limit_mb: int = 1024,
        gc_threshold: tuple[int, int, int] = (700, 10, 10),
        cleanup_interval: int = 300,
        enable_leak_detection: bool = True
    ):
        """
        Initialize memory optimizer.

        Args:
            memory_limit_mb: Memory limit in MB
            gc_threshold: Garbage collection thresholds (gen0, gen1, gen2)
            cleanup_interval: Cleanup interval in seconds
            enable_leak_detection: Enable memory leak detection
        """
        self.memory_limit_mb = memory_limit_mb
        self.gc_threshold = gc_threshold
        self.cleanup_interval = cleanup_interval
        self.enable_leak_detection = enable_leak_detection

        # Monitoring state
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._memory_stats_history: List[Dict[str, Any]] = []
        self._leak_detection_objects: Dict[int, Any] = {}
        self._cleanup_callbacks: List[Callable[[], None]] = []

        # Set GC thresholds
        gc.set_threshold(*gc_threshold)
        logger.info(f"Set GC thresholds: {gc_threshold}")

    def start_monitoring(self):
        """Start memory monitoring and optimization."""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="MemoryOptimizer"
        )
        self._monitor_thread.start()
        logger.info("Memory monitoring started")

    def stop_monitoring(self):
        """Stop memory monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Memory monitoring stopped")

    def add_cleanup_callback(self, callback: Callable[[], None]):
        """Add a cleanup callback to be called during memory cleanup."""
        self._cleanup_callbacks.append(callback)

    def remove_cleanup_callback(self, callback: Callable[[], None]):
        """Remove a cleanup callback."""
        if callback in self._cleanup_callbacks:
            self._cleanup_callbacks.remove(callback)

    def force_garbage_collection(self):
        """Force garbage collection across all generations."""
        collected = 0
        for generation in range(3):
            collected += gc.collect(generation)

        logger.info(f"Garbage collection completed: {collected} objects collected")
        return collected

    def optimize_memory_usage(self):
        """Perform comprehensive memory optimization."""
        logger.info("Starting memory optimization...")

        # Force garbage collection
        collected = self.force_garbage_collection()

        # Run cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")

        # Clear internal caches if available
        self._clear_internal_caches()

        logger.info("Memory optimization completed")
        return {"objects_collected": collected}

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        try:
            import psutil
            process = psutil.Process()

            stats = {
                "memory_usage_mb": process.memory_info().rss / (1024 * 1024),
                "memory_limit_mb": self.memory_limit_mb,
                "gc_stats": {
                    "collections": [gc.get_count()[i] for i in range(3)],
                    "objects": gc.get_count(),
                    "thresholds": gc.get_threshold()
                },
                "thread_count": threading.active_count(),
                "timestamp": time.time()
            }

            # Memory usage percentage
            stats["memory_usage_percent"] = (stats["memory_usage_mb"] / self.memory_limit_mb) * 100

            return stats
        except ImportError:
            return {
                "error": "psutil not available",
                "gc_stats": {
                    "collections": [gc.get_count()[i] for i in range(3)],
                    "objects": gc.get_count(),
                    "thresholds": gc.get_threshold()
                }
            }

    def detect_memory_leaks(self) -> List[Dict[str, Any]]:
        """Detect potential memory leaks."""
        if not self.enable_leak_detection:
            return []

        leaks = []
        try:
            # Get objects that have been alive for multiple GC cycles
            for obj in gc.get_objects():
                obj_id = id(obj)
                if obj_id in self._leak_detection_objects:
                    # Object has survived multiple collections
                    self._leak_detection_objects[obj_id]["survival_count"] += 1
                    if self._leak_detection_objects[obj_id]["survival_count"] > 3:
                        leaks.append({
                            "object_type": type(obj).__name__,
                            "object_id": obj_id,
                            "size_bytes": len(str(obj).encode()) if hasattr(obj, '__str__') else 0,
                            "survival_count": self._leak_detection_objects[obj_id]["survival_count"]
                        })
                else:
                    self._leak_detection_objects[obj_id] = {
                        "object": obj,
                        "survival_count": 1,
                        "first_seen": time.time()
                    }

            # Clean up old entries
            current_time = time.time()
            to_remove = []
            for obj_id, data in self._leak_detection_objects.items():
                if current_time - data["first_seen"] > 3600:  # 1 hour
                    to_remove.append(obj_id)

            for obj_id in to_remove:
                del self._leak_detection_objects[obj_id]

        except Exception as e:
            logger.error(f"Error in leak detection: {e}")

        return leaks

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                # Collect memory stats
                stats = self.get_memory_stats()
                self._memory_stats_history.append(stats)

                # Keep only recent history
                if len(self._memory_stats_history) > 100:
                    self._memory_stats_history = self._memory_stats_history[-100:]

                # Check memory limits
                if stats.get("memory_usage_percent", 0) > 85:
                    logger.warning(".1f")
                    self.optimize_memory_usage()

                # Detect memory leaks periodically
                if self.enable_leak_detection and len(self._memory_stats_history) % 10 == 0:
                    leaks = self.detect_memory_leaks()
                    if leaks:
                        logger.warning(f"Potential memory leaks detected: {len(leaks)} objects")

                # Periodic cleanup
                if len(self._memory_stats_history) % (self.cleanup_interval // 30) == 0:
                    self.optimize_memory_usage()

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            time.sleep(30)  # Check every 30 seconds

    def _clear_internal_caches(self):
        """Clear internal caches to free memory."""
        try:
            # Clear Python's internal caches
            import sys
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()

            # Clear import cache (limited)
            modules_to_clear = []
            for module_name, module in sys.modules.items():
                if module_name.startswith(('PIL.', 'numpy.', 'pandas.')):
                    modules_to_clear.append(module_name)

            # Note: Actually clearing modules can be dangerous, so we just log
            if modules_to_clear:
                logger.info(f"Identified {len(modules_to_clear)} modules that could be cleared")

        except Exception as e:
            logger.debug(f"Error clearing internal caches: {e}")

    def get_optimization_recommendations(self) -> List[str]:
        """Get memory optimization recommendations based on current stats."""
        recommendations = []
        stats = self.get_memory_stats()

        memory_percent = stats.get("memory_usage_percent", 0)
        if memory_percent > 90:
            recommendations.append("CRITICAL: Memory usage above 90%. Immediate action required.")
            recommendations.append("- Reduce batch sizes in data processing")
            recommendations.append("- Implement streaming for large datasets")
            recommendations.append("- Clear unused caches and sessions")
        elif memory_percent > 75:
            recommendations.append("WARNING: Memory usage above 75%.")
            recommendations.append("- Monitor memory-intensive operations")
            recommendations.append("- Consider increasing memory limits if needed")
        elif memory_percent < 50:
            recommendations.append("Memory usage is healthy (< 50%)")

        # GC recommendations
        gc_counts = stats.get("gc_stats", {}).get("collections", [0, 0, 0])
        if gc_counts[0] > gc_counts[1] * 10:  # Too many gen0 collections
            recommendations.append("- Consider adjusting GC thresholds to reduce collection frequency")

        # Leak detection
        leaks = self.detect_memory_leaks()
        if leaks:
            recommendations.append(f"- {len(leaks)} potential memory leaks detected")
            recommendations.append("- Review object lifecycle management")

        return recommendations


# Global instance
_memory_optimizer: Optional[MemoryOptimizer] = None


def get_memory_optimizer() -> MemoryOptimizer:
    """Get or create global memory optimizer instance."""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer


def start_memory_optimization():
    """Start global memory optimization."""
    optimizer = get_memory_optimizer()
    optimizer.start_monitoring()


def stop_memory_optimization():
    """Stop global memory optimization."""
    optimizer = get_memory_optimizer()
    optimizer.stop_monitoring()


def optimize_memory_now() -> Dict[str, Any]:
    """Perform immediate memory optimization."""
    optimizer = get_memory_optimizer()
    return optimizer.optimize_memory_usage()


def get_memory_stats() -> Dict[str, Any]:
    """Get current memory statistics."""
    optimizer = get_memory_optimizer()
    return optimizer.get_memory_stats()