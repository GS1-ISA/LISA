"""
Retrieval system for ISA SuperApp.

This module provides document retrieval capabilities using vector search
and hybrid retrieval strategies.
"""

import abc
import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from .embedding import BaseEmbeddingProvider, EmbeddingFactory
from .exceptions import ISAConfigurationError, ISANotFoundError, ISAValidationError
from .logger import get_logger
from .models import Document, RetrievalStrategy, SearchResult, Vector
from .vector_store import BaseVectorStore, VectorStoreConfig, VectorStoreFactory


@dataclass
class RetrievalConfig:
    """Retrieval system configuration."""

    strategy: str
    vector_store_provider: str
    embedding_provider: str
    collection_name: str
    vector_dimension: int
    top_k: int = 10
    rerank_top_k: int = 5
    similarity_threshold: float = 0.7
    enable_reranking: bool = True
    enable_hybrid_search: bool = True
    sparse_weight: float = 0.3
    dense_weight: float = 0.7
    timeout: int = 30
    cache_enabled: bool = True
    cache_size: int = 1000

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.strategy:
            raise ISAValidationError("Strategy is required", field="strategy")
        if not self.vector_store_provider:
            raise ISAValidationError(
                "Vector store provider is required", field="vector_store_provider"
            )
        if not self.embedding_provider:
            raise ISAValidationError(
                "Embedding provider is required", field="embedding_provider"
            )
        if not self.collection_name:
            raise ISAValidationError(
                "Collection name is required", field="collection_name"
            )
        if self.vector_dimension <= 0:
            raise ISAValidationError(
                "Vector dimension must be positive", field="vector_dimension"
            )
        if self.top_k <= 0:
            raise ISAValidationError("top_k must be positive", field="top_k")
        if self.rerank_top_k <= 0:
            raise ISAValidationError(
                "rerank_top_k must be positive", field="rerank_top_k"
            )
        if not 0 <= self.similarity_threshold <= 1:
            raise ISAValidationError(
                "similarity_threshold must be between 0 and 1",
                field="similarity_threshold",
            )
        if not 0 <= self.sparse_weight <= 1:
            raise ISAValidationError(
                "sparse_weight must be between 0 and 1", field="sparse_weight"
            )
        if not 0 <= self.dense_weight <= 1:
            raise ISAValidationError(
                "dense_weight must be between 0 and 1", field="dense_weight"
            )
        if abs(self.sparse_weight + self.dense_weight - 1.0) > 1e-6:
            raise ISAValidationError(
                "sparse_weight + dense_weight must equal 1.0", field="sparse_weight"
            )


class BaseRetrievalStrategy(abc.ABC):
    """Abstract base class for retrieval strategies."""

    def __init__(self, config: RetrievalConfig) -> None:
        """
        Initialize retrieval strategy.

        Args:
            config: Retrieval configuration
        """
        self.config = config
        self.logger = get_logger(f"retrieval.{config.strategy}")
        self._initialized = False

    @abc.abstractmethod
    async def initialize(
        self, vector_store: BaseVectorStore, embedding_provider: BaseEmbeddingProvider
    ) -> None:
        """
        Initialize the retrieval strategy.

        Args:
            vector_store: Vector store instance
            embedding_provider: Embedding provider instance
        """
        pass

    @abc.abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Retrieve documents for a query.

        Args:
            query: Search query
            top_k: Number of results to return (overrides config)
            filter_metadata: Optional metadata filter

        Returns:
            List of search results
        """
        pass

    @abc.abstractmethod
    async def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[List[SearchResult]]:
        """
        Retrieve documents for multiple queries.

        Args:
            queries: List of search queries
            top_k: Number of results to return per query (overrides config)
            filter_metadata: Optional metadata filter

        Returns:
            List of search result lists
        """
        pass

    def _validate_query(self, query: str) -> None:
        """Validate query input."""
        if not query or not query.strip():
            raise ISAValidationError("Query cannot be empty", field="query")
        if len(query) > 10000:
            raise ISAValidationError(
                "Query too long (max 10000 characters)", field="query"
            )

    def _validate_queries(self, queries: List[str]) -> None:
        """Validate queries input."""
        if not queries:
            raise ISAValidationError("Queries list cannot be empty", field="queries")
        for query in queries:
            self._validate_query(query)

    def _validate_top_k(self, top_k: int) -> None:
        """Validate top_k parameter."""
        if top_k <= 0:
            raise ISAValidationError("top_k must be positive", field="top_k")
        if top_k > 1000:
            raise ISAValidationError("top_k cannot be greater than 1000", field="top_k")

    def _filter_by_similarity(
        self, results: List[SearchResult], threshold: float
    ) -> List[SearchResult]:
        """Filter results by similarity threshold."""
        filtered = []
        for result in results:
            if result.score >= threshold:
                filtered.append(result)
        return filtered

    def _rerank_results(
        self, query: str, results: List[SearchResult], top_k: int
    ) -> List[SearchResult]:
        """Rerank results using query relevance."""
        if not self.config.enable_reranking or len(results) <= 1:
            return results[:top_k]

        # Simple reranking based on query similarity
        # In a real implementation, this could use a cross-encoder model
        reranked = []
        for result in results:
            # Calculate simple text similarity
            query_lower = query.lower()
            text_lower = str(result.vector.metadata.get("text", "")).lower()

            # Count matching words
            query_words = set(query_lower.split())
            text_words = set(text_lower.split())
            overlap = len(query_words.intersection(text_words))

            # Adjust score based on overlap
            adjusted_score = result.score * (
                1.0 + 0.1 * overlap / max(len(query_words), 1)
            )

            reranked_result = SearchResult(
                vector=result.vector,
                score=min(adjusted_score, 1.0),  # Cap at 1.0
                metadata={**result.metadata, "reranked": True},
            )
            reranked.append(reranked_result)

        # Sort by adjusted score
        reranked.sort(key=lambda x: x.score, reverse=True)
        return reranked[:top_k]


class DenseRetrievalStrategy(BaseRetrievalStrategy):
    """Dense retrieval strategy using vector embeddings."""

    def __init__(self, config: RetrievalConfig) -> None:
        """
        Initialize dense retrieval strategy.

        Args:
            config: Retrieval configuration
        """
        super().__init__(config)
        self.vector_store: Optional[BaseVectorStore] = None
        self.embedding_provider: Optional[BaseEmbeddingProvider] = None

    async def initialize(
        self, vector_store: BaseVectorStore, embedding_provider: BaseEmbeddingProvider
    ) -> None:
        """Initialize the dense retrieval strategy."""
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self._initialized = True
        self.logger.info("Dense retrieval strategy initialized")

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Retrieve documents using dense embeddings."""
        self._validate_query(query)

        if top_k is None:
            top_k = self.config.top_k

        self._validate_top_k(top_k)

        if not self._initialized:
            raise ISAConfigurationError("Retrieval strategy not initialized")

        # Generate query embedding
        query_embedding = await self.embedding_provider.embed_query(query)

        # Search in vector store
        results = await self.vector_store.search(
            query_vector=query_embedding,
            k=(
                top_k * 2 if self.config.enable_reranking else top_k
            ),  # Get more for reranking
            filter_metadata=filter_metadata,
        )

        # Filter by similarity threshold
        results = self._filter_by_similarity(results, self.config.similarity_threshold)

        # Rerank if enabled
        if self.config.enable_reranking:
            results = self._rerank_results(query, results, top_k)
        else:
            results = results[:top_k]

        return results

    async def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[List[SearchResult]]:
        """Retrieve documents for multiple queries."""
        self._validate_queries(queries)

        if top_k is None:
            top_k = self.config.top_k

        self._validate_top_k(top_k)

        if not self._initialized:
            raise ISAConfigurationError("Retrieval strategy not initialized")

        # Process queries in parallel
        tasks = [self.retrieve(query, top_k, filter_metadata) for query in queries]

        results = await asyncio.gather(*tasks)
        return results


class HybridRetrievalStrategy(BaseRetrievalStrategy):
    """Hybrid retrieval strategy combining dense and sparse retrieval."""

    def __init__(self, config: RetrievalConfig) -> None:
        """
        Initialize hybrid retrieval strategy.

        Args:
            config: Retrieval configuration
        """
        super().__init__(config)
        self.vector_store: Optional[BaseVectorStore] = None
        self.embedding_provider: Optional[BaseEmbeddingProvider] = None

    async def initialize(
        self, vector_store: BaseVectorStore, embedding_provider: BaseEmbeddingProvider
    ) -> None:
        """Initialize the hybrid retrieval strategy."""
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self._initialized = True
        self.logger.info("Hybrid retrieval strategy initialized")

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Retrieve documents using hybrid approach."""
        self._validate_query(query)

        if top_k is None:
            top_k = self.config.top_k

        self._validate_top_k(top_k)

        if not self._initialized:
            raise ISAConfigurationError("Retrieval strategy not initialized")

        # Dense retrieval
        dense_results = await self._dense_retrieve(query, top_k * 2, filter_metadata)

        # Sparse retrieval (simplified BM25-like approach)
        sparse_results = await self._sparse_retrieve(query, top_k * 2, filter_metadata)

        # Combine results
        combined_results = self._combine_results(dense_results, sparse_results, top_k)

        return combined_results

    async def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[List[SearchResult]]:
        """Retrieve documents for multiple queries."""
        self._validate_queries(queries)

        if top_k is None:
            top_k = self.config.top_k

        self._validate_top_k(top_k)

        if not self._initialized:
            raise ISAConfigurationError("Retrieval strategy not initialized")

        # Process queries in parallel
        tasks = [self.retrieve(query, top_k, filter_metadata) for query in queries]

        results = await asyncio.gather(*tasks)
        return results

    async def _dense_retrieve(
        self, query: str, top_k: int, filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Dense retrieval component."""
        # Generate query embedding
        query_embedding = await self.embedding_provider.embed_query(query)

        # Search in vector store
        results = await self.vector_store.search(
            query_vector=query_embedding, k=top_k, filter_metadata=filter_metadata
        )

        return results

    async def _sparse_retrieve(
        self, query: str, top_k: int, filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Sparse retrieval component (simplified BM25-like approach)."""
        # This is a simplified implementation
        # In a real system, this would use a proper sparse retrieval system like BM25

        query_words = set(query.lower().split())
        all_vectors = []

        # Get all vectors (in a real system, this would be more efficient)
        # For now, we'll simulate by getting some results and filtering
        dummy_embedding = [0.0] * self.config.vector_dimension
        results = await self.vector_store.search(
            query_vector=dummy_embedding,
            k=top_k * 10,  # Get more to filter
            filter_metadata=filter_metadata,
        )

        # Score based on word overlap
        scored_results = []
        for result in results:
            text = str(result.vector.metadata.get("text", "")).lower()
            text_words = set(text.split())

            # Calculate overlap score
            overlap = len(query_words.intersection(text_words))
            total_words = len(query_words.union(text_words))
            score = overlap / max(total_words, 1) if total_words > 0 else 0

            if score > 0:
                scored_result = SearchResult(
                    vector=result.vector,
                    score=score,
                    metadata={**result.metadata, "sparse_score": score},
                )
                scored_results.append(scored_result)

        # Sort by score and take top k
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]

    def _combine_results(
        self,
        dense_results: List[SearchResult],
        sparse_results: List[SearchResult],
        top_k: int,
    ) -> List[SearchResult]:
        """Combine dense and sparse results."""
        # Normalize scores
        dense_results = self._normalize_scores(dense_results)
        sparse_results = self._normalize_scores(sparse_results)

        # Create result map
        result_map = {}

        # Add dense results
        for result in dense_results:
            result_map[result.vector.id] = {
                "dense_score": result.score,
                "sparse_score": 0.0,
                "vector": result.vector,
                "metadata": result.metadata,
            }

        # Add sparse results
        for result in sparse_results:
            if result.vector.id in result_map:
                result_map[result.vector.id]["sparse_score"] = result.score
            else:
                result_map[result.vector.id] = {
                    "dense_score": 0.0,
                    "sparse_score": result.score,
                    "vector": result.vector,
                    "metadata": result.metadata,
                }

        # Calculate combined scores
        combined_results = []
        for vector_id, scores in result_map.items():
            combined_score = (
                self.config.dense_weight * scores["dense_score"]
                + self.config.sparse_weight * scores["sparse_score"]
            )

            combined_result = SearchResult(
                vector=scores["vector"],
                score=combined_score,
                metadata={
                    **scores["metadata"],
                    "dense_score": scores["dense_score"],
                    "sparse_score": scores["sparse_score"],
                    "combined_score": combined_score,
                },
            )
            combined_results.append(combined_result)

        # Sort by combined score and take top k
        combined_results.sort(key=lambda x: x.score, reverse=True)

        # Filter by similarity threshold
        filtered_results = self._filter_by_similarity(
            combined_results, self.config.similarity_threshold
        )

        return filtered_results[:top_k]

    def _normalize_scores(self, results: List[SearchResult]) -> List[SearchResult]:
        """Normalize scores to 0-1 range."""
        if not results:
            return results

        max_score = max(result.score for result in results)
        min_score = min(result.score for result in results)

        if max_score == min_score:
            # All scores are the same
            for result in results:
                result.score = 1.0
        else:
            # Normalize to 0-1 range
            for result in results:
                result.score = (result.score - min_score) / (max_score - min_score)

        return results


class RetrievalSystem:
    """Main retrieval system."""

    def __init__(self, config: RetrievalConfig) -> None:
        """
        Initialize retrieval system.

        Args:
            config: Retrieval configuration
        """
        self.config = config
        self.logger = get_logger("retrieval.system")
        self.vector_store: Optional[BaseVectorStore] = None
        self.embedding_provider: Optional[BaseEmbeddingProvider] = None
        self.strategy: Optional[BaseRetrievalStrategy] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the retrieval system."""
        try:
            # Create vector store
            vector_store_config = VectorStoreConfig(
                provider=self.config.vector_store_provider,
                collection_name=self.config.collection_name,
                dimension=self.config.vector_dimension,
                cache_enabled=self.config.cache_enabled,
                cache_size=self.config.cache_size,
            )

            self.vector_store = VectorStoreFactory.create_store(vector_store_config)
            await self.vector_store.initialize()

            # Create embedding provider
            self.embedding_provider = EmbeddingFactory.create_provider(
                self.config.embedding_provider,
                model_name="sentence-transformers/all-MiniLM-L6-v2",  # Default model
            )

            # Create retrieval strategy
            if self.config.strategy == "dense":
                self.strategy = DenseRetrievalStrategy(self.config)
            elif self.config.strategy == "hybrid":
                self.strategy = HybridRetrievalStrategy(self.config)
            else:
                raise ISAConfigurationError(
                    f"Unsupported retrieval strategy: {self.config.strategy}"
                )

            await self.strategy.initialize(self.vector_store, self.embedding_provider)

            self._initialized = True
            self.logger.info("Retrieval system initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize retrieval system: {e}")
            raise ISAConfigurationError(f"Failed to initialize retrieval system: {e}")

    async def close(self) -> None:
        """Close the retrieval system."""
        if self.vector_store:
            await self.vector_store.close()

        self.vector_store = None
        self.embedding_provider = None
        self.strategy = None
        self._initialized = False
        self.logger.info("Retrieval system closed")

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Retrieve documents for a query.

        Args:
            query: Search query
            top_k: Number of results to return (overrides config)
            filter_metadata: Optional metadata filter

        Returns:
            List of search results

        Raises:
            ISAConfigurationError: If system not initialized
        """
        if not self._initialized:
            raise ISAConfigurationError("Retrieval system not initialized")

        return await self.strategy.retrieve(query, top_k, filter_metadata)

    async def retrieve_batch(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[List[SearchResult]]:
        """
        Retrieve documents for multiple queries.

        Args:
            queries: List of search queries
            top_k: Number of results to return per query (overrides config)
            filter_metadata: Optional metadata filter

        Returns:
            List of search result lists

        Raises:
            ISAConfigurationError: If system not initialized
        """
        if not self._initialized:
            raise ISAConfigurationError("Retrieval system not initialized")

        return await self.strategy.retrieve_batch(queries, top_k, filter_metadata)

    async def add_document(self, document: Document, vector: Vector) -> None:
        """
        Add a document to the retrieval system.

        Args:
            document: Document to add
            vector: Document vector
        """
        if not self._initialized:
            raise ISAConfigurationError("Retrieval system not initialized")

        await self.vector_store.add_vector(vector)
        self.logger.debug(f"Added document {document.id} to retrieval system")

    async def add_documents(
        self, documents: List[Document], vectors: List[Vector]
    ) -> None:
        """
        Add multiple documents to the retrieval system.

        Args:
            documents: List of documents to add
            vectors: List of document vectors
        """
        if not self._initialized:
            raise ISAConfigurationError("Retrieval system not initialized")

        if len(documents) != len(vectors):
            raise ISAValidationError(
                "Documents and vectors lists must have the same length"
            )

        await self.vector_store.add_vectors(vectors)
        self.logger.debug(f"Added {len(documents)} documents to retrieval system")

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the retrieval system.

        Args:
            document_id: Document ID

        Returns:
            True if document was deleted, False if not found
        """
        if not self._initialized:
            raise ISAConfigurationError("Retrieval system not initialized")

        return await self.vector_store.delete_vector(document_id)

    async def get_document_count(self) -> int:
        """
        Get the number of documents in the retrieval system.

        Returns:
            Document count
        """
        if not self._initialized:
            raise ISAConfigurationError("Retrieval system not initialized")

        return await self.vector_store.count_vectors()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._initialized:
            try:
                asyncio.run(self.close())
            except Exception as e:
                self.logger.error(f"Error closing retrieval system: {e}")


# Utility functions
async def create_retrieval_system(
    strategy: str = "dense",
    vector_store_provider: str = "in_memory",
    embedding_provider: str = "sentence_transformers",
    collection_name: str = "default_collection",
    vector_dimension: int = 384,
    **kwargs,
) -> RetrievalSystem:
    """
    Create a retrieval system with common configuration.

    Args:
        strategy: Retrieval strategy
        vector_store_provider: Vector store provider
        embedding_provider: Embedding provider
        collection_name: Collection name
        vector_dimension: Vector dimension
        **kwargs: Additional configuration parameters

    Returns:
        Retrieval system instance
    """
    config = RetrievalConfig(
        strategy=strategy,
        vector_store_provider=vector_store_provider,
        embedding_provider=embedding_provider,
        collection_name=collection_name,
        vector_dimension=vector_dimension,
        **kwargs,
    )

    retrieval_system = RetrievalSystem(config)
    await retrieval_system.initialize()
    return retrieval_system


async def create_retrieval_system_from_config(
    config_dict: Dict[str, Any],
) -> RetrievalSystem:
    """
    Create a retrieval system from configuration dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        Retrieval system instance
    """
    config = RetrievalConfig(**config_dict)
    retrieval_system = RetrievalSystem(config)
    await retrieval_system.initialize()
    return retrieval_system
