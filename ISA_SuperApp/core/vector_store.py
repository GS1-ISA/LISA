"""
Vector store for ISA SuperApp.

This module provides vector storage and similarity search capabilities
using various vector databases and search algorithms.
"""

import abc
import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
from .logger import get_logger
from .models import SearchResult, Vector, VectorStoreProvider


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""

    provider: str
    collection_name: str
    dimension: int
    distance_metric: str = "cosine"  # cosine, euclidean, dot_product
    index_type: str = "hnsw"  # hnsw, ivf, flat
    max_elements: int = 1000000
    ef_construction: int = 200
    ef_search: int = 100
    m: int = 16
    batch_size: int = 100
    timeout: int = 30
    cache_enabled: bool = True
    cache_size: int = 10000

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.provider:
            raise ISAValidationError("Provider is required", field="provider")
        if not self.collection_name:
            raise ISAValidationError(
                "Collection name is required", field="collection_name"
            )
        if self.dimension <= 0:
            raise ISAValidationError("Dimension must be positive", field="dimension")
        if self.distance_metric not in ["cosine", "euclidean", "dot_product"]:
            raise ISAValidationError("Invalid distance metric", field="distance_metric")
        if self.index_type not in ["hnsw", "ivf", "flat"]:
            raise ISAValidationError("Invalid index type", field="index_type")


class BaseVectorStore(abc.ABC):
    """Abstract base class for vector stores."""

    def __init__(self, config: VectorStoreConfig) -> None:
        """
        Initialize vector store.

        Args:
            config: Vector store configuration
        """
        self.config = config
        self.logger = get_logger(f"vector_store.{config.provider}")
        self._initialized = False
        self._cache: Dict[str, Vector] = {}
        self._cache_lock = asyncio.Lock()

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store."""
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the vector store."""
        pass

    @abc.abstractmethod
    async def add_vector(self, vector: Vector) -> None:
        """
        Add a single vector to the store.

        Args:
            vector: Vector to add
        """
        pass

    @abc.abstractmethod
    async def add_vectors(self, vectors: List[Vector]) -> None:
        """
        Add multiple vectors to the store.

        Args:
            vectors: List of vectors to add
        """
        pass

    @abc.abstractmethod
    async def search(
        self,
        query_vector: List[float],
        k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector
            k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of search results
        """
        pass

    @abc.abstractmethod
    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector by ID.

        Args:
            vector_id: Vector ID

        Returns:
            True if vector was deleted, False if not found
        """
        pass

    @abc.abstractmethod
    async def get_vector(self, vector_id: str) -> Optional[Vector]:
        """
        Get a vector by ID.

        Args:
            vector_id: Vector ID

        Returns:
            Vector if found, None otherwise
        """
        pass

    @abc.abstractmethod
    async def update_vector(self, vector: Vector) -> bool:
        """
        Update a vector.

        Args:
            vector: Vector to update

        Returns:
            True if vector was updated, False if not found
        """
        pass

    @abc.abstractmethod
    async def count_vectors(self) -> int:
        """
        Count total number of vectors in the store.

        Returns:
            Vector count
        """
        pass

    def _validate_vector(self, vector: Vector) -> None:
        """Validate vector input."""
        if not vector.id:
            raise ISAValidationError("Vector ID is required", field="id")
        if not vector.vector:
            raise ISAValidationError("Vector data is required", field="vector")
        if len(vector.vector) != self.config.dimension:
            raise ISAValidationError(
                f"Vector dimension mismatch: expected {self.config.dimension}, "
                f"got {len(vector.vector)}",
                field="vector",
            )

    def _validate_vectors(self, vectors: List[Vector]) -> None:
        """Validate vectors input."""
        if not vectors:
            raise ISAValidationError("Vectors list cannot be empty", field="vectors")
        for vector in vectors:
            self._validate_vector(vector)

    def _validate_query_vector(self, query_vector: List[float]) -> None:
        """Validate query vector input."""
        if not query_vector:
            raise ISAValidationError(
                "Query vector cannot be empty", field="query_vector"
            )
        if len(query_vector) != self.config.dimension:
            raise ISAValidationError(
                f"Query vector dimension mismatch: expected {self.config.dimension}, "
                f"got {len(query_vector)}",
                field="query_vector",
            )

    def _validate_k(self, k: int) -> None:
        """Validate k parameter."""
        if k <= 0:
            raise ISAValidationError("k must be positive", field="k")
        if k > 1000:
            raise ISAValidationError("k cannot be greater than 1000", field="k")

    def _calculate_distance(self, v1: List[float], v2: List[float]) -> float:
        """Calculate distance between two vectors."""
        vec1 = np.array(v1)
        vec2 = np.array(v2)

        if self.config.distance_metric == "cosine":
            # Cosine similarity (converted to distance)
            similarity = np.dot(vec1, vec2) / (
                np.linalg.norm(vec1) * np.linalg.norm(vec2)
            )
            return 1.0 - similarity
        elif self.config.distance_metric == "euclidean":
            # Euclidean distance
            return np.linalg.norm(vec1 - vec2)
        elif self.config.distance_metric == "dot_product":
            # Negative dot product (converted to distance)
            return -np.dot(vec1, vec2)
        else:
            raise ISAConfigurationError(
                f"Unsupported distance metric: {self.config.distance_metric}"
            )

    async def _get_cached_vector(self, vector_id: str) -> Optional[Vector]:
        """Get vector from cache."""
        if not self.config.cache_enabled:
            return None

        async with self._cache_lock:
            return self._cache.get(vector_id)

    async def _set_cached_vector(self, vector: Vector) -> None:
        """Set vector in cache."""
        if not self.config.cache_enabled:
            return

        async with self._cache_lock:
            self._cache[vector.id] = vector

            # Maintain cache size limit
            if len(self._cache) > self.config.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

    async def _remove_cached_vector(self, vector_id: str) -> None:
        """Remove vector from cache."""
        if not self.config.cache_enabled:
            return

        async with self._cache_lock:
            self._cache.pop(vector_id, None)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._initialized:
            try:
                asyncio.run(self.close())
            except Exception as e:
                self.logger.error(f"Error closing vector store: {e}")


class InMemoryVectorStore(BaseVectorStore):
    """In-memory vector store implementation."""

    def __init__(self, config: VectorStoreConfig) -> None:
        """
        Initialize in-memory vector store.

        Args:
            config: Vector store configuration
        """
        super().__init__(config)
        self._vectors: Dict[str, Vector] = {}
        self._vector_data: Dict[str, List[float]] = {}

    async def initialize(self) -> None:
        """Initialize the in-memory vector store."""
        self._initialized = True
        self.logger.info("In-memory vector store initialized")

    async def close(self) -> None:
        """Close the in-memory vector store."""
        self._vectors.clear()
        self._vector_data.clear()
        self._initialized = False
        self.logger.info("In-memory vector store closed")

    async def add_vector(self, vector: Vector) -> None:
        """Add a single vector to the store."""
        self._validate_vector(vector)

        self._vectors[vector.id] = vector
        self._vector_data[vector.id] = vector.vector

        # Cache result
        await self._set_cached_vector(vector)

        self.logger.debug(f"Added vector {vector.id}")

    async def add_vectors(self, vectors: List[Vector]) -> None:
        """Add multiple vectors to the store."""
        self._validate_vectors(vectors)

        for vector in vectors:
            self._vectors[vector.id] = vector
            self._vector_data[vector.id] = vector.vector

            # Cache result
            await self._set_cached_vector(vector)

        self.logger.debug(f"Added {len(vectors)} vectors")

    async def search(
        self,
        query_vector: List[float],
        k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        self._validate_query_vector(query_vector)
        self._validate_k(k)

        if not self._vectors:
            return []

        # Calculate distances for all vectors
        distances = []
        for vector_id, vector_data in self._vector_data.items():
            distance = self._calculate_distance(query_vector, vector_data)

            # Apply metadata filter if provided
            if filter_metadata:
                vector = self._vectors[vector_id]
                if not self._matches_filter(vector.metadata, filter_metadata):
                    continue

            distances.append((distance, vector_id))

        # Sort by distance and take top k
        distances.sort(key=lambda x: x[0])
        top_k = distances[:k]

        # Create search results
        results = []
        for distance, vector_id in top_k:
            vector = self._vectors[vector_id]
            result = SearchResult(
                vector=vector,
                score=(
                    1.0 - distance
                    if self.config.distance_metric == "cosine"
                    else distance
                ),
                metadata={
                    "distance": distance,
                    "distance_metric": self.config.distance_metric,
                },
            )
            results.append(result)

        return results

    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        if vector_id not in self._vectors:
            return False

        del self._vectors[vector_id]
        del self._vector_data[vector_id]

        # Remove from cache
        await self._remove_cached_vector(vector_id)

        self.logger.debug(f"Deleted vector {vector_id}")
        return True

    async def get_vector(self, vector_id: str) -> Optional[Vector]:
        """Get a vector by ID."""
        # Check cache first
        cached_vector = await self._get_cached_vector(vector_id)
        if cached_vector:
            return cached_vector

        return self._vectors.get(vector_id)

    async def update_vector(self, vector: Vector) -> bool:
        """Update a vector."""
        self._validate_vector(vector)

        if vector.id not in self._vectors:
            return False

        self._vectors[vector.id] = vector
        self._vector_data[vector.id] = vector.vector

        # Update cache
        await self._set_cached_vector(vector)

        self.logger.debug(f"Updated vector {vector.id}")
        return True

    async def count_vectors(self) -> int:
        """Count total number of vectors in the store."""
        return len(self._vectors)

    def _matches_filter(
        self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]
    ) -> bool:
        """Check if metadata matches filter criteria."""
        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation."""

    def __init__(self, config: VectorStoreConfig) -> None:
        """
        Initialize ChromaDB vector store.

        Args:
            config: Vector store configuration
        """
        super().__init__(config)
        self._client = None
        self._collection = None

    async def initialize(self) -> None:
        """Initialize the ChromaDB vector store."""
        try:
            import chromadb
            from chromadb.config import Settings

            # Initialize client
            self._client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )

            # Get or create collection
            try:
                self._collection = self._client.get_collection(
                    name=self.config.collection_name
                )
                self.logger.info(
                    f"Using existing collection '{self.config.collection_name}'"
                )
            except Exception:
                self._collection = self._client.create_collection(
                    name=self.config.collection_name,
                    metadata={
                        "hnsw:space": self.config.distance_metric,
                        "hnsw:ef_construction": self.config.ef_construction,
                        "hnsw:ef_search": self.config.ef_search,
                        "hnsw:M": self.config.m,
                    },
                )
                self.logger.info(f"Created collection '{self.config.collection_name}'")

            self._initialized = True
            self.logger.info("ChromaDB vector store initialized")

        except ImportError:
            raise ISAConfigurationError(
                "ChromaDB not installed. Install with: pip install chromadb"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB vector store: {e}")
            raise ISAConfigurationError(
                f"Failed to initialize ChromaDB vector store: {e}"
            )

    async def close(self) -> None:
        """Close the ChromaDB vector store."""
        self._collection = None
        self._client = None
        self._initialized = False
        self.logger.info("ChromaDB vector store closed")

    async def add_vector(self, vector: Vector) -> None:
        """Add a single vector to the store."""
        self._validate_vector(vector)

        # Convert metadata to JSON strings for ChromaDB
        metadata_str = {k: str(v) for k, v in vector.metadata.items()}

        self._collection.add(
            embeddings=[vector.vector], metadatas=[metadata_str], ids=[vector.id]
        )

        # Cache result
        await self._set_cached_vector(vector)

        self.logger.debug(f"Added vector {vector.id}")

    async def add_vectors(self, vectors: List[Vector]) -> None:
        """Add multiple vectors to the store."""
        self._validate_vectors(vectors)

        # Process in batches
        for i in range(0, len(vectors), self.config.batch_size):
            batch = vectors[i : i + self.config.batch_size]

            embeddings = [v.vector for v in batch]
            metadatas = [{k: str(v) for k, v in vec.metadata.items()} for vec in batch]
            ids = [v.id for v in batch]

            self._collection.add(embeddings=embeddings, metadatas=metadatas, ids=ids)

            # Cache results
            for vector in batch:
                await self._set_cached_vector(vector)

        self.logger.debug(f"Added {len(vectors)} vectors")

    async def search(
        self,
        query_vector: List[float],
        k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        self._validate_query_vector(query_vector)
        self._validate_k(k)

        # Convert filter metadata to strings
        where_clause = None
        if filter_metadata:
            where_clause = {k: str(v) for k, v in filter_metadata.items()}

        # Search
        results = self._collection.query(
            query_embeddings=[query_vector], n_results=k, where=where_clause
        )

        # Create search results
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, vector_id in enumerate(results["ids"][0]):
                vector = Vector(
                    id=vector_id,
                    vector=results["embeddings"][0][i],
                    document_id=vector_id,
                    metadata={k: v for k, v in results["metadatas"][0][i].items()},
                )

                result = SearchResult(
                    vector=vector,
                    score=results["distances"][0][i],
                    metadata={
                        "distance": results["distances"][0][i],
                        "distance_metric": self.config.distance_metric,
                    },
                )
                search_results.append(result)

        return search_results

    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        try:
            self._collection.delete(ids=[vector_id])

            # Remove from cache
            await self._remove_cached_vector(vector_id)

            self.logger.debug(f"Deleted vector {vector_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete vector {vector_id}: {e}")
            return False

    async def get_vector(self, vector_id: str) -> Optional[Vector]:
        """Get a vector by ID."""
        # Check cache first
        cached_vector = await self._get_cached_vector(vector_id)
        if cached_vector:
            return cached_vector

        try:
            result = self._collection.get(ids=[vector_id])

            if not result["ids"]:
                return None

            vector = Vector(
                id=result["ids"][0],
                vector=result["embeddings"][0],
                document_id=result["ids"][0],
                metadata={k: v for k, v in result["metadatas"][0].items()},
            )

            # Cache result
            await self._set_cached_vector(vector)

            return vector

        except Exception as e:
            self.logger.error(f"Failed to get vector {vector_id}: {e}")
            return None

    async def update_vector(self, vector: Vector) -> bool:
        """Update a vector."""
        self._validate_vector(vector)

        try:
            # Delete existing vector
            self._collection.delete(ids=[vector.id])

            # Add updated vector
            metadata_str = {k: str(v) for k, v in vector.metadata.items()}
            self._collection.add(
                embeddings=[vector.vector], metadatas=[metadata_str], ids=[vector.id]
            )

            # Update cache
            await self._set_cached_vector(vector)

            self.logger.debug(f"Updated vector {vector.id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update vector {vector.id}: {e}")
            return False

    async def count_vectors(self) -> int:
        """Count total number of vectors in the store."""
        try:
            return self._collection.count()
        except Exception as e:
            self.logger.error(f"Failed to count vectors: {e}")
            return 0


class VectorStoreFactory:
    """Factory for creating vector store instances."""

    _stores = {
        "in_memory": InMemoryVectorStore,
        "chroma": ChromaVectorStore,
    }

    @classmethod
    def create_store(cls, config: VectorStoreConfig) -> BaseVectorStore:
        """
        Create a vector store instance.

        Args:
            config: Vector store configuration

        Returns:
            Vector store instance

        Raises:
            ISAConfigurationError: If provider is not supported
        """
        if config.provider not in cls._stores:
            raise ISAConfigurationError(
                f"Unsupported vector store provider: {config.provider}. "
                f"Supported providers: {list(cls._stores.keys())}"
            )

        store_class = cls._stores[config.provider]
        return store_class(config)

    @classmethod
    def register_store(
        cls, provider_name: str, store_class: Type[BaseVectorStore]
    ) -> None:
        """
        Register a new vector store provider.

        Args:
            provider_name: Provider name
            store_class: Store class
        """
        cls._stores[provider_name] = store_class

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """
        Get list of supported providers.

        Returns:
            List of provider names
        """
        return list(cls._stores.keys())


# Utility functions
async def create_vector_store(
    provider: str = "in_memory",
    collection_name: str = "default_collection",
    dimension: int = 384,
    **kwargs,
) -> BaseVectorStore:
    """
    Create a vector store with common configuration.

    Args:
        provider: Vector store provider
        collection_name: Collection name
        dimension: Vector dimension
        **kwargs: Additional configuration parameters

    Returns:
        Vector store instance
    """
    config = VectorStoreConfig(
        provider=provider,
        collection_name=collection_name,
        dimension=dimension,
        **kwargs,
    )

    vector_store = VectorStoreFactory.create_store(config)
    await vector_store.initialize()
    return vector_store


async def create_vector_store_from_config(
    config_dict: Dict[str, Any],
) -> BaseVectorStore:
    """
    Create a vector store from configuration dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        Vector store instance
    """
    config = VectorStoreConfig(**config_dict)
    vector_store = VectorStoreFactory.create_store(config)
    await vector_store.initialize()
    return vector_store
