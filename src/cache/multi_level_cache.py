"""
Multi-Level Caching System for ISA_D

Implements a three-tier caching strategy:
- L1: In-memory cache (fastest, limited size)
- L2: Redis cache (distributed, persistent)
- L3: File-based cache (persistent, slowest)

Features:
- Intelligent cache promotion/demotion
- Configurable TTL per layer
- Comprehensive statistics tracking
- ISA-specific optimization rules
- Thread-safe operations
"""

import hashlib
import json
import os
import pickle
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable
import redis


class ISACacheEntry:
    """Represents a cache entry with metadata for ISA optimizations."""

    def __init__(self, value: Any, ttl: int, priority: int = 1, tags: list = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.priority = priority  # 1=low, 2=medium, 3=high
        self.tags = tags or []
        self.access_count = 0
        self.last_accessed = time.time()

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() - self.created_at > self.ttl

    def access(self):
        """Mark entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


class ISAL1Cache:
    """L1 In-memory cache with LRU eviction and ISA optimizations."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, ISACacheEntry] = OrderedDict()
        self.lock = threading.RLock()

        # ISA-specific priority queues
        self.priority_queues = {
            1: OrderedDict(),  # Low priority
            2: OrderedDict(),  # Medium priority
            3: OrderedDict()   # High priority
        }

    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if not entry.is_expired():
                    entry.access()
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    return entry.value
                else:
                    # Remove expired entry
                    del self.cache[key]
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, priority: int = 1, tags: list = None):
        """Set value in L1 cache with ISA optimizations."""
        with self.lock:
            ttl = ttl or self.default_ttl
            entry = ISACacheEntry(value, ttl, priority, tags)

            # Remove if exists
            if key in self.cache:
                del self.cache[key]

            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                self._evict_least_valuable()

            self.cache[key] = entry
            self.cache.move_to_end(key)  # Mark as recently used

    def _evict_least_valuable(self):
        """Evict least valuable entry based on ISA rules."""
        # First try to evict low priority items
        for priority in [1, 2, 3]:
            queue = self.priority_queues[priority]
            if queue:
                # Evict least recently used from this priority
                lru_key = next(iter(queue))
                del self.cache[lru_key]
                del queue[lru_key]
                return

        # Fallback to standard LRU
        if self.cache:
            lru_key = next(iter(self.cache))
            del self.cache[lru_key]

    def clear(self):
        """Clear all entries."""
        with self.lock:
            self.cache.clear()
            for queue in self.priority_queues.values():
                queue.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics."""
        with self.lock:
            total_entries = len(self.cache)
            expired_count = sum(1 for entry in self.cache.values() if entry.is_expired())
            priority_counts = {p: len(q) for p, q in self.priority_queues.items()}
            total_accesses = sum(entry.access_count for entry in self.cache.values())

            return {
                'total_entries': total_entries,
                'expired_entries': expired_count,
                'active_entries': total_entries - expired_count,
                'priority_distribution': priority_counts,
                'total_accesses': total_accesses,
                'hit_rate_estimate': total_accesses / max(1, total_entries)
            }


class ISAL2Cache:
    """L2 Redis cache with ISA optimizations."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0,
                 default_ttl: int = 3600, prefix: str = 'isa_l2:'):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_ttl = default_ttl
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self.prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            data = self.redis.get(self._make_key(key))
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in Redis cache."""
        try:
            ttl = ttl or self.default_ttl
            data = json.dumps(value)
            self.redis.setex(self._make_key(key), ttl, data)
        except Exception:
            pass  # Fail silently

    def delete(self, key: str):
        """Delete key from Redis cache."""
        try:
            self.redis.delete(self._make_key(key))
        except Exception:
            pass

    def clear(self, pattern: str = "*"):
        """Clear cache entries matching pattern."""
        try:
            keys = self.redis.keys(f"{self.prefix}{pattern}")
            if keys:
                self.redis.delete(*keys)
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            info = self.redis.info()
            keys_count = len(self.redis.keys(f"{self.prefix}*"))
            return {
                'redis_connected': True,
                'cached_keys': keys_count,
                'redis_memory_used': info.get('used_memory_human', 'unknown'),
                'redis_uptime': info.get('uptime_in_seconds', 0)
            }
        except Exception:
            return {'redis_connected': False, 'error': 'Redis connection failed'}


class ISAL3Cache:
    """L3 File-based cache with ISA optimizations."""

    def __init__(self, cache_dir: str = ".cache/isa_l3", default_ttl: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def _get_file_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Use hash to create filename
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache."""
        file_path = self._get_file_path(key)

        if not file_path.exists():
            return None

        try:
            with file_path.open('rb') as f:
                data = pickle.load(f)

            # Check TTL
            if time.time() - data['timestamp'] > data['ttl']:
                file_path.unlink()  # Remove expired file
                return None

            return data['value']
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in file cache."""
        file_path = self._get_file_path(key)
        ttl = ttl or self.default_ttl

        try:
            data = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl,
                'key': key
            }

            with file_path.open('wb') as f:
                pickle.dump(data, f)
        except Exception:
            pass  # Fail silently

    def delete(self, key: str):
        """Delete key from file cache."""
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()

    def clear(self):
        """Clear all cache files."""
        for file_path in self.cache_dir.glob("*.cache"):
            file_path.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get file cache statistics."""
        try:
            files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in files)
            expired_count = 0

            for file_path in files:
                try:
                    with file_path.open('rb') as f:
                        data = pickle.load(f)
                    if time.time() - data['timestamp'] > data['ttl']:
                        expired_count += 1
                except Exception:
                    expired_count += 1

            return {
                'total_files': len(files),
                'expired_files': expired_count,
                'active_files': len(files) - expired_count,
                'total_size_bytes': total_size,
                'cache_dir': str(self.cache_dir)
            }
        except Exception:
            return {'error': 'Failed to read cache directory'}


class MultiLevelCache:
    """
    Multi-level caching system with intelligent promotion/demotion.

    Architecture:
    - L1: Fast in-memory cache (LRU with ISA priorities)
    - L2: Distributed Redis cache
    - L3: Persistent file-based cache

    Features:
    - Automatic cache promotion on access
    - Configurable TTL per layer
    - ISA-specific optimization rules
    - Comprehensive statistics
    """

    def __init__(self,
                 l1_max_size: int = 1000,
                 l1_ttl: int = 300,
                 l2_host: str = 'localhost',
                 l2_port: int = 6379,
                 l2_ttl: int = 3600,
                 l3_dir: str = ".cache/isa_multilevel",
                 l3_ttl: int = 86400,
                 isa_optimization_rules: Dict[str, Any] = None):

        # Initialize cache layers
        self.l1 = ISAL1Cache(max_size=l1_max_size, default_ttl=l1_ttl)
        self.l2 = ISAL2Cache(host=l2_host, port=l2_port, default_ttl=l2_ttl)
        self.l3 = ISAL3Cache(cache_dir=l3_dir, default_ttl=l3_ttl)

        # ISA-specific optimization rules
        self.isa_rules = isa_optimization_rules or {
            'high_priority_patterns': ['llm_', 'agent_', 'research_'],
            'medium_priority_patterns': ['doc_', 'data_', 'query_'],
            'long_ttl_patterns': ['static_', 'config_', 'metadata_'],
            'short_ttl_patterns': ['temp_', 'session_', 'volatile_']
        }

        # Statistics
        self.stats = {
            'l1_hits': 0, 'l1_misses': 0,
            'l2_hits': 0, 'l2_misses': 0,
            'l3_hits': 0, 'l3_misses': 0,
            'promotions': 0, 'demotions': 0,
            'total_requests': 0
        }
        self.stats_lock = threading.Lock()

    def _determine_priority(self, key: str) -> int:
        """Determine cache priority based on ISA rules."""
        for pattern in self.isa_rules['high_priority_patterns']:
            if pattern in key:
                return 3
        for pattern in self.isa_rules['medium_priority_patterns']:
            if pattern in key:
                return 2
        return 1

    def _determine_ttl(self, key: str, layer: str) -> int:
        """Determine TTL based on ISA rules and layer."""
        base_ttl = {
            'l1': self.l1.default_ttl,
            'l2': self.l2.default_ttl,
            'l3': self.l3.default_ttl
        }[layer]

        # Adjust based on patterns
        for pattern in self.isa_rules['long_ttl_patterns']:
            if pattern in key:
                return base_ttl * 4  # 4x longer
        for pattern in self.isa_rules['short_ttl_patterns']:
            if pattern in key:
                return base_ttl // 4  # 4x shorter

        return base_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache with promotion."""
        with self.stats_lock:
            self.stats['total_requests'] += 1

        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            with self.stats_lock:
                self.stats['l1_hits'] += 1
            return value

        with self.stats_lock:
            self.stats['l1_misses'] += 1

        # Try L2
        value = self.l2.get(key)
        if value is not None:
            with self.stats_lock:
                self.stats['l2_hits'] += 1
            # Promote to L1
            priority = self._determine_priority(key)
            l1_ttl = self._determine_ttl(key, 'l1')
            self.l1.set(key, value, ttl=l1_ttl, priority=priority)
            with self.stats_lock:
                self.stats['promotions'] += 1
            return value

        with self.stats_lock:
            self.stats['l2_misses'] += 1

        # Try L3
        value = self.l3.get(key)
        if value is not None:
            with self.stats_lock:
                self.stats['l3_hits'] += 1
            # Promote to L2 and L1
            l2_ttl = self._determine_ttl(key, 'l2')
            self.l2.set(key, value, ttl=l2_ttl)

            priority = self._determine_priority(key)
            l1_ttl = self._determine_ttl(key, 'l1')
            self.l1.set(key, value, ttl=l1_ttl, priority=priority)

            with self.stats_lock:
                self.stats['promotions'] += 2  # L3->L2 and L2->L1
            return value

        with self.stats_lock:
            self.stats['l3_misses'] += 1

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, priority: Optional[int] = None):
        """Set value in all cache layers."""
        # Determine priority and TTLs
        priority = priority or self._determine_priority(key)

        l1_ttl = ttl or self._determine_ttl(key, 'l1')
        l2_ttl = ttl or self._determine_ttl(key, 'l2')
        l3_ttl = ttl or self._determine_ttl(key, 'l3')

        # Set in all layers
        self.l1.set(key, value, ttl=l1_ttl, priority=priority)
        self.l2.set(key, value, ttl=l2_ttl)
        self.l3.set(key, value, ttl=l3_ttl)

    def delete(self, key: str):
        """Delete key from all cache layers."""
        self.l1.cache.pop(key, None)
        self.l2.delete(key)
        self.l3.delete(key)

    def clear(self):
        """Clear all cache layers."""
        self.l1.clear()
        self.l2.clear()
        self.l3.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self.stats_lock:
            stats = self.stats.copy()

        # Calculate rates
        total = stats['total_requests']
        if total > 0:
            stats['overall_hit_rate'] = (stats['l1_hits'] + stats['l2_hits'] + stats['l3_hits']) / total * 100
            stats['l1_hit_rate'] = stats['l1_hits'] / total * 100
            stats['l2_hit_rate'] = stats['l2_hits'] / total * 100
            stats['l3_hit_rate'] = stats['l3_hits'] / total * 100

        # Layer-specific stats
        stats['l1_stats'] = self.l1.get_stats()
        stats['l2_stats'] = self.l2.get_stats()
        stats['l3_stats'] = self.l3.get_stats()

        # ISA optimizations summary
        stats['isa_optimizations'] = {
            'high_priority_patterns': self.isa_rules['high_priority_patterns'],
            'medium_priority_patterns': self.isa_rules['medium_priority_patterns'],
            'long_ttl_patterns': self.isa_rules['long_ttl_patterns'],
            'short_ttl_patterns': self.isa_rules['short_ttl_patterns']
        }

        return stats

    def optimize_for_isa_workload(self):
        """Apply ISA-specific optimizations based on current workload."""
        # This could be enhanced with ML-based optimization
        # For now, it's a placeholder for future enhancements
        pass


# Global instance
_multilevel_cache: Optional[MultiLevelCache] = None

def get_multilevel_cache() -> MultiLevelCache:
    """Get or create global MultiLevelCache instance."""
    global _multilevel_cache
    if _multilevel_cache is None:
        _multilevel_cache = MultiLevelCache()
    return _multilevel_cache