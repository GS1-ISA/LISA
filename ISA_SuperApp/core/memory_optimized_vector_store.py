"""
Memory-Optimized Vector Store for ISA SuperApp.

This module provides memory-efficient vector storage with:
- LRU eviction for memory management
- Compressed vector storage
- Intelligent caching strategies
- Memory usage monitoring
"""

import abc
import asyncio
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from .exceptions import ISAConfigurationError, ISAValidationError
from .logger import get_logger
from .models import SearchResult, Vector


@dataclass
class MemoryOptimizedConfig:
    """Memory-optimized vector store configuration."""

    provider: str
    collection_name: str
    dimension: int
    distance_metric: str = "cosine"
    max_memory_vectors: int = 5000  # Limit in-memory vectors
    cache_size: int = 1000
    compression_enabled: bool = True
    memory_limit_mb: int = 512  # Memory limit in MB

    def __post_init__(self) -> None:
        if not self.provider:
            raise ISAValidationError("Provider is required", field="provider")
        if self.dimension <= 0:
            raise ISAValidationError("Dimension must be positive", field="dimension")


class MemoryEfficientVectorStore(abc.ABC):
    """Abstract base class for memory-efficient vector stores."""

    def __init__(self, config: MemoryOptimizedConfig) -> None:
        self.config = config
        self.logger = get_logger(f"memory_vector_store.{config.provider}")
        self._initialized = False

        # Memory-efficient storage
        self._vectors: OrderedDict[str, Vector] = OrderedDict()  # LRU ordering
        self._vector_data: dict[str, tuple[bytes, int]] = {}  # (compressed_vector, access_time)
        self._access_counter = 0
        self._memory_usage = 0

        # Compression
        self._compression_enabled = config.compression_enabled

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store."""
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the vector store."""
        pass

    def _compress_vector(self, vector: list[float]) -> bytes:
        """Compress vector data to save memory."""
        if not self._compression_enabled:
            return np.array(vector, dtype=np.float32).tobytes()

        # Use quantization to reduce precision and memory
        arr = np.array(vector, dtype=np.float16)  # Reduce to half precision
        return arr.tobytes()

    def _decompress_vector(self, compressed: bytes) -> list[float]:
        """Decompress vector data."""
        if not self._compression_enabled:
            arr = np.frombuffer(compressed, dtype=np.float32)
        else:
            arr = np.frombuffer(compressed, dtype=np.float16)

        return arr.astype(np.float32).tolist()

    def _update_access(self, vector_id: str):
        """Update access time for LRU."""
        self._access_counter += 1
        if vector_id in self._vector_data:
            self._vector_data[vector_id] = (
                self._vector_data[vector_id][0],
                self._access_counter
            )

    def _evict_old_vectors(self):
        """Evict least recently used vectors to stay within memory limits."""
        if len(self._vectors) <= self.config.max_memory_vectors:
            return

        # Remove oldest 20% of vectors
        evict_count = max(1, len(self._vectors) // 5)
        evicted = 0

        for vector_id in list(self._vectors.keys()):
            if evicted >= evict_count:
                break
            if vector_id in self._vectors:
                del self._vectors[vector_id]
                del self._vector_data[vector_id]
                evicted += 1

        if evicted > 0:
            self.logger.info(f"Evicted {evicted} vectors due to memory limits")

    def _calculate_memory_usage(self) -> int:
        """Calculate current memory usage in bytes."""
        vector_memory = sum(
            len(compressed) + len(vector_id.encode())
            for vector_id, (compressed, _) in self._vector_data.items()
        )
        metadata_memory = sum(
            len(str(v.metadata).encode()) + len(v.id.encode())
            for v in self._vectors.values()
        )
        return vector_memory + metadata_memory

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory usage statistics."""
        return {
            "vectors_in_memory": len(self._vectors),
            "total_vectors": len(self._vector_data),
            "memory_usage_mb": self._calculate_memory_usage() / (1024 * 1024),
            "memory_limit_mb": self.config.memory_limit_mb,
            "compression_enabled": self._compression_enabled,
            "cache_hit_ratio": getattr(self, '_cache_hits', 0) / max(1, getattr(self, '_cache_misses', 0) + getattr(self, '_cache_hits', 0))
        }


class OptimizedInMemoryVectorStore(MemoryEfficientVectorStore):
    """Memory-optimized in-memory vector store."""

    def __init__(self, config: MemoryOptimizedConfig) -> None:
        super().__init__(config)
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the optimized vector store."""
        self._initialized = True
        self.logger.info("Memory-optimized in-memory vector store initialized")

    async def close(self) -> None:
        """Close the vector store."""
        async with self._lock:
            self._vectors.clear()
            self._vector_data.clear()
            self._initialized = False
        self.logger.info("Memory-optimized vector store closed")

    async def add_vector(self, vector: Vector) -> None:
        """Add a single vector with memory optimization."""
        async with self._lock:
            # Validate input
            if not vector.id:
                raise ISAValidationError("Vector ID is required", field="id")
            if len(vector.vector) != self.config.dimension:
                raise ISAValidationError(
                    f"Vector dimension mismatch: expected {self.config.dimension}, "
                    f"got {len(vector.vector)}",
                    field="vector",
                )

            # Compress and store
            compressed = self._compress_vector(vector.vector)
            self._vector_data[vector.id] = (compressed, self._access_counter)
            self._vectors[vector.id] = vector
            self._vectors.move_to_end(vector.id)  # Mark as recently used

            # Evict if necessary
            self._evict_old_vectors()

            self.logger.debug(f"Added optimized vector {vector.id}")

    async def add_vectors(self, vectors: list[Vector]) -> None:
        """Add multiple vectors efficiently."""
        async with self._lock:
            for vector in vectors:
                await self.add_vector(vector)

    async def search(
        self,
        query_vector: list[float],
        k: int = 10,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors with memory efficiency."""
        async with self._lock:
            if not self._vectors:
                return []

            # Validate query
            if len(query_vector) != self.config.dimension:
                raise ISAValidationError(
                    f"Query vector dimension mismatch: expected {self.config.dimension}, "
                    f"got {len(query_vector)}",
                    field="query_vector",
                )

            query_arr = np.array(query_vector)

            # Calculate distances for in-memory vectors only
            distances = []
            for vector_id, vector in self._vectors.items():
                # Apply metadata filter
                if filter_metadata:
                    if not self._matches_filter(vector.metadata, filter_metadata):
                        continue

                # Decompress vector for distance calculation
                compressed, _ = self._vector_data[vector_id]
                vec_arr = np.array(self._decompress_vector(compressed))

                # Calculate distance
                if self.config.distance_metric == "cosine":
                    similarity = np.dot(query_arr, vec_arr) / (
                        np.linalg.norm(query_arr) * np.linalg.norm(vec_arr)
                    )
                    distance = 1.0 - similarity
                elif self.config.distance_metric == "euclidean":
                    distance = np.linalg.norm(query_arr - vec_arr)
                else:
                    distance = np.linalg.norm(query_arr - vec_arr)  # Default to euclidean

                distances.append((distance, vector_id))
                self._update_access(vector_id)

            # Sort and return top k
            distances.sort(key=lambda x: x[0])
            top_k = distances[:k]

            results = []
            for distance, vector_id in top_k:
                vector = self._vectors[vector_id]
                result = SearchResult(
                    vector=vector,
                    score=1.0 - distance if self.config.distance_metric == "cosine" else distance,
                    metadata={
                        "distance": distance,
                        "distance_metric": self.config.distance_metric,
                    },
                )
                results.append(result)

            return results

    async def get_vector(self, vector_id: str) -> Vector | None:
        """Get vector by ID."""
        async with self._lock:
            if vector_id in self._vectors:
                self._update_access(vector_id)
                self._vectors.move_to_end(vector_id)
                return self._vectors[vector_id]
            return None

    async def delete_vector(self, vector_id: str) -> bool:
        """Delete vector by ID."""
        async with self._lock:
            if vector_id in self._vectors:
                del self._vectors[vector_id]
                del self._vector_data[vector_id]
                return True
            return False

    async def count_vectors(self) -> int:
        """Count total vectors."""
        async with self._lock:
            return len(self._vector_data)

    def _matches_filter(
        self, metadata: dict[str, Any], filter_metadata: dict[str, Any]
    ) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True


# Factory function for optimized vector stores
async def create_memory_optimized_vector_store(
    provider: str = "optimized_memory",
    collection_name: str = "default_collection",
    dimension: int = 384,
    **kwargs,
) -> MemoryEfficientVectorStore:
    """
    Create a memory-optimized vector store.

    Args:
        provider: Vector store provider
        collection_name: Collection name
        dimension: Vector dimension
        **kwargs: Additional configuration

    Returns:
        Memory-optimized vector store instance
    """
    config = MemoryOptimizedConfig(
        provider=provider,
        collection_name=collection_name,
        dimension=dimension,
        **kwargs,
    )

    if provider == "optimized_memory":
        store = OptimizedInMemoryVectorStore(config)
    else:
        raise ISAConfigurationError(f"Unsupported optimized provider: {provider}")

    await store.initialize()
    return store


# Module logger
logger = get_logger(__name__)