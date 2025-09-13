"""
Embedding service for ISA SuperApp.

This module provides text embedding capabilities using various
embedding providers and models.
"""

import abc
import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import numpy as np

from .exceptions import ISAConfigurationError, ISAValidationError
from .logger import get_logger
from .models import Document, Vector


@dataclass
class EmbeddingConfig:
    """Embedding service configuration."""

    provider: str
    model: str
    dimension: int
    batch_size: int = 32
    max_tokens: int = 8192
    timeout: int = 30
    cache_enabled: bool = True
    cache_size: int = 10000
    normalize: bool = True
    pooling_strategy: str = "mean"  # mean, cls, max

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.provider:
            raise ISAValidationError("Provider is required", field="provider")
        if not self.model:
            raise ISAValidationError("Model is required", field="model")
        if self.dimension <= 0:
            raise ISAValidationError("Dimension must be positive", field="dimension")
        if self.batch_size <= 0:
            raise ISAValidationError("Batch size must be positive", field="batch_size")
        if self.pooling_strategy not in ["mean", "cls", "max"]:
            raise ISAValidationError(
                "Invalid pooling strategy", field="pooling_strategy"
            )


class BaseEmbeddingProvider(abc.ABC):
    """Abstract base class for embedding providers."""

    def __init__(self, config: EmbeddingConfig) -> None:
        """
        Initialize embedding provider.

        Args:
            config: Embedding configuration
        """
        self.config = config
        self.logger = get_logger(f"embedding.{config.provider}")
        self._initialized = False
        self._cache: Dict[str, List[float]] = {}
        self._cache_lock = asyncio.Lock()

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the embedding provider."""
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the embedding provider."""
        pass

    @abc.abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        pass

    @abc.abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    def _validate_text(self, text: str) -> None:
        """Validate text input."""
        if not text or not text.strip():
            raise ISAValidationError("Text cannot be empty", field="text")
        if len(text) > self.config.max_tokens * 4:  # Rough token estimation
            raise ISAValidationError(
                f"Text too long: {len(text)} characters (max ~{self.config.max_tokens} tokens)",
                field="text",
            )

    def _validate_texts(self, texts: List[str]) -> None:
        """Validate texts input."""
        if not texts:
            raise ISAValidationError("Texts list cannot be empty", field="texts")
        for text in texts:
            self._validate_text(text)

    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize vector to unit length."""
        if not self.config.normalize:
            return vector

        v = np.array(vector)
        norm = np.linalg.norm(v)
        if norm == 0:
            return vector

        return (v / norm).tolist()

    def _apply_pooling(self, embeddings: List[List[float]]) -> List[float]:
        """Apply pooling strategy to embeddings."""
        if not embeddings:
            return []

        if self.config.pooling_strategy == "mean":
            # Mean pooling
            return np.mean(embeddings, axis=0).tolist()
        elif self.config.pooling_strategy == "max":
            # Max pooling
            return np.max(embeddings, axis=0).tolist()
        elif self.config.pooling_strategy == "cls":
            # CLS token (first token)
            return embeddings[0]
        else:
            raise ISAConfigurationError(
                f"Unsupported pooling strategy: {self.config.pooling_strategy}"
            )

    async def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        if not self.config.cache_enabled:
            return None

        async with self._cache_lock:
            return self._cache.get(text)

    async def _set_cached_embedding(self, text: str, embedding: List[float]) -> None:
        """Set embedding in cache."""
        if not self.config.cache_enabled:
            return

        async with self._cache_lock:
            self._cache[text] = embedding

            # Maintain cache size limit
            if len(self._cache) > self.config.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._initialized:
            try:
                asyncio.run(self.close())
            except Exception as e:
                self.logger.error(f"Error closing embedding provider: {e}")


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """Sentence Transformers embedding provider."""

    def __init__(self, config: EmbeddingConfig) -> None:
        """
        Initialize Sentence Transformers embedding provider.

        Args:
            config: Embedding configuration
        """
        super().__init__(config)
        self._model = None

    async def initialize(self) -> None:
        """Initialize the Sentence Transformers embedding provider."""
        try:
            from sentence_transformers import SentenceTransformer

            # Load model
            self._model = SentenceTransformer(self.config.model)

            # Verify dimension
            test_embedding = self._model.encode(["test"])
            actual_dimension = len(test_embedding[0])
            if actual_dimension != self.config.dimension:
                self.logger.warning(
                    f"Model dimension mismatch: expected {self.config.dimension}, "
                    f"got {actual_dimension}. Updating config."
                )
                self.config.dimension = actual_dimension

            self._initialized = True
            self.logger.info(
                f"Sentence Transformers embedding provider initialized with model '{self.config.model}'"
            )

        except ImportError:
            raise ISAConfigurationError(
                "Sentence Transformers not installed. Install with: pip install sentence-transformers"
            )
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Sentence Transformers embedding provider: {e}"
            )
            raise ISAConfigurationError(
                f"Failed to initialize Sentence Transformers embedding provider: {e}"
            )

    async def close(self) -> None:
        """Close the Sentence Transformers embedding provider."""
        self._model = None
        self._initialized = False
        self.logger.info("Sentence Transformers embedding provider closed")

    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        self._validate_text(text)

        # Check cache
        cached_embedding = await self._get_cached_embedding(text)
        if cached_embedding:
            return cached_embedding

        try:
            # Embed text
            embedding = self._model.encode([text])[0].tolist()
            embedding = self._normalize_vector(embedding)

            # Cache result
            await self._set_cached_embedding(text, embedding)

            return embedding

        except Exception as e:
            self.logger.error(f"Failed to embed text with Sentence Transformers: {e}")
            raise ISAConfigurationError(
                f"Failed to embed text with Sentence Transformers: {e}"
            )

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        self._validate_texts(texts)

        try:
            # Process in batches
            embeddings = []
            for i in range(0, len(texts), self.config.batch_size):
                batch = texts[i : i + self.config.batch_size]

                # Embed batch
                batch_embeddings = self._model.encode(batch).tolist()
                batch_embeddings = [
                    self._normalize_vector(emb) for emb in batch_embeddings
                ]

                embeddings.extend(batch_embeddings)

                # Cache results
                for text, embedding in zip(batch, batch_embeddings):
                    await self._set_cached_embedding(text, embedding)

            return embeddings

        except Exception as e:
            self.logger.error(f"Failed to embed texts with Sentence Transformers: {e}")
            raise ISAConfigurationError(
                f"Failed to embed texts with Sentence Transformers: {e}"
            )


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider."""

    def __init__(self, config: EmbeddingConfig) -> None:
        """
        Initialize OpenAI embedding provider.

        Args:
            config: Embedding configuration
        """
        super().__init__(config)
        self._client = None

    async def initialize(self) -> None:
        """Initialize the OpenAI embedding provider."""
        try:
            import openai

            # Initialize client
            self._client = openai.AsyncOpenAI()

            self._initialized = True
            self.logger.info(
                f"OpenAI embedding provider initialized with model '{self.config.model}'"
            )

        except ImportError:
            raise ISAConfigurationError(
                "OpenAI not installed. Install with: pip install openai"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI embedding provider: {e}")
            raise ISAConfigurationError(
                f"Failed to initialize OpenAI embedding provider: {e}"
            )

    async def close(self) -> None:
        """Close the OpenAI embedding provider."""
        if self._client:
            await self._client.close()
        self._initialized = False
        self.logger.info("OpenAI embedding provider closed")

    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text."""
        self._validate_text(text)

        # Check cache
        cached_embedding = await self._get_cached_embedding(text)
        if cached_embedding:
            return cached_embedding

        try:
            # Embed text
            response = await self._client.embeddings.create(
                model=self.config.model, input=text
            )

            embedding = response.data[0].embedding
            embedding = self._normalize_vector(embedding)

            # Cache result
            await self._set_cached_embedding(text, embedding)

            return embedding

        except Exception as e:
            self.logger.error(f"Failed to embed text with OpenAI: {e}")
            raise ISAConfigurationError(f"Failed to embed text with OpenAI: {e}")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        self._validate_texts(texts)

        try:
            # Process in batches
            embeddings = []
            for i in range(0, len(texts), self.config.batch_size):
                batch = texts[i : i + self.config.batch_size]

                # Embed batch
                response = await self._client.embeddings.create(
                    model=self.config.model, input=batch
                )

                batch_embeddings = [
                    self._normalize_vector(data.embedding) for data in response.data
                ]
                embeddings.extend(batch_embeddings)

                # Cache results
                for text, embedding in zip(batch, batch_embeddings):
                    await self._set_cached_embedding(text, embedding)

            return embeddings

        except Exception as e:
            self.logger.error(f"Failed to embed texts with OpenAI: {e}")
            raise ISAConfigurationError(f"Failed to embed texts with OpenAI: {e}")


class EmbeddingService:
    """Embedding service for managing text embeddings."""

    def __init__(self, provider: BaseEmbeddingProvider) -> None:
        """
        Initialize embedding service.

        Args:
            provider: Embedding provider
        """
        self.provider = provider
        self.logger = get_logger("embedding.service")

    async def initialize(self) -> None:
        """Initialize the embedding service."""
        await self.provider.initialize()
        self.logger.info("Embedding service initialized")

    async def close(self) -> None:
        """Close the embedding service."""
        await self.provider.close()
        self.logger.info("Embedding service closed")

    async def embed_document(self, document: Document) -> Vector:
        """
        Embed a document.

        Args:
            document: Document to embed

        Returns:
            Vector with embedding
        """
        if not document.content:
            raise ISAValidationError(
                "Document content cannot be empty", field="content"
            )

        # Embed text
        embedding = await self.provider.embed_text(document.content)

        return Vector(
            id=document.id,
            vector=embedding,
            document_id=document.id,
            metadata=document.metadata or {},
        )

    async def embed_documents(self, documents: List[Document]) -> List[Vector]:
        """
        Embed multiple documents.

        Args:
            documents: List of documents to embed

        Returns:
            List of vectors with embeddings
        """
        if not documents:
            raise ISAValidationError(
                "Documents list cannot be empty", field="documents"
            )

        # Extract texts
        texts = [doc.content for doc in documents]

        # Embed texts
        embeddings = await self.provider.embed_texts(texts)

        # Create vectors
        vectors = []
        for doc, embedding in zip(documents, embeddings):
            vector = Vector(
                id=doc.id,
                vector=embedding,
                document_id=doc.id,
                metadata=doc.metadata or {},
            )
            vectors.append(vector)

        return vectors

    async def embed_text_chunks(
        self,
        text_chunks: List[str],
        chunk_ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Vector]:
        """
        Embed text chunks.

        Args:
            text_chunks: List of text chunks
            chunk_ids: Optional list of chunk IDs
            metadata: Optional list of metadata for each chunk

        Returns:
            List of vectors with embeddings
        """
        if not text_chunks:
            raise ISAValidationError(
                "Text chunks list cannot be empty", field="text_chunks"
            )

        # Generate IDs if not provided
        if chunk_ids is None:
            chunk_ids = [f"chunk_{i}" for i in range(len(text_chunks))]

        # Generate metadata if not provided
        if metadata is None:
            metadata = [{} for _ in text_chunks]

        # Validate lengths
        if len(chunk_ids) != len(text_chunks):
            raise ISAValidationError("Chunk IDs length must match text chunks length")
        if len(metadata) != len(text_chunks):
            raise ISAValidationError("Metadata length must match text chunks length")

        # Embed texts
        embeddings = await self.provider.embed_texts(text_chunks)

        # Create vectors
        vectors = []
        for chunk_id, text, embedding, meta in zip(
            chunk_ids, text_chunks, embeddings, metadata
        ):
            vector = Vector(
                id=chunk_id,
                vector=embedding,
                document_id=chunk_id,
                metadata={"text": text, **meta},
            )
            vectors.append(vector)

        return vectors


class EmbeddingProviderFactory:
    """Factory for creating embedding provider instances."""

    _providers = {
        "sentence_transformers": SentenceTransformerEmbeddingProvider,
        "openai": OpenAIEmbeddingProvider,
    }

    @classmethod
    def create_provider(cls, config: EmbeddingConfig) -> BaseEmbeddingProvider:
        """
        Create an embedding provider instance.

        Args:
            config: Embedding configuration

        Returns:
            Embedding provider instance

        Raises:
            ISAConfigurationError: If provider is not supported
        """
        if config.provider not in cls._providers:
            raise ISAConfigurationError(
                f"Unsupported embedding provider: {config.provider}. "
                f"Supported providers: {list(cls._providers.keys())}"
            )

        provider_class = cls._providers[config.provider]
        return provider_class(config)

    @classmethod
    def register_provider(
        cls, provider_name: str, provider_class: Type[BaseEmbeddingProvider]
    ) -> None:
        """
        Register a new embedding provider.

        Args:
            provider_name: Provider name
            provider_class: Provider class
        """
        cls._providers[provider_name] = provider_class

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """
        Get list of supported providers.

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())


# Utility functions
async def create_embedding_service(
    provider: str = "sentence_transformers",
    model: str = "all-MiniLM-L6-v2",
    dimension: int = 384,
    **kwargs,
) -> EmbeddingService:
    """
    Create an embedding service with common configuration.

    Args:
        provider: Embedding provider
        model: Model name
        dimension: Embedding dimension
        **kwargs: Additional configuration parameters

    Returns:
        Embedding service instance
    """
    config = EmbeddingConfig(
        provider=provider, model=model, dimension=dimension, **kwargs
    )

    provider_instance = EmbeddingProviderFactory.create_provider(config)
    embedding_service = EmbeddingService(provider_instance)
    await embedding_service.initialize()
    return embedding_service


async def create_embedding_service_from_config(
    config_dict: Dict[str, Any],
) -> EmbeddingService:
    """
    Create an embedding service from configuration dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        Embedding service instance
    """
    config = EmbeddingConfig(**config_dict)
    provider_instance = EmbeddingProviderFactory.create_provider(config)
    embedding_service = EmbeddingService(provider_instance)
    await embedding_service.initialize()
    return embedding_service
