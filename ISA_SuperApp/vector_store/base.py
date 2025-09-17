"""
Base vector store module for ISA SuperApp.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseVectorStore(ABC):
    """Base class for vector stores."""

    @abstractmethod
    def add_vectors(self, vectors: list[list[float]], metadata: list[dict[str, Any]] = None) -> None:
        """Add vectors to the store."""
        pass

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int = 10) -> list[dict[str, Any]]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """Delete vectors by IDs."""
        pass


class DocumentMetadata:
    """Metadata for documents in vector store."""

    def __init__(self, **kwargs):
        """Initialize metadata."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class SearchFilters:
    """Filters for vector store search operations."""

    def __init__(self, **kwargs):
        """Initialize search filters."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class SearchResult:
    """Result from a vector store search."""

    def __init__(self, document, score, metadata=None):
        """Initialize search result."""
        self.document = document
        self.score = score
        self.metadata = metadata or {}


class VectorDocument:
    """Document with vector representation."""

    def __init__(self, id: str, content: str, vector: list[float] = None, metadata: dict[str, Any] = None, embedding: list[float] = None, **kwargs):
        """Initialize vector document."""
        self.id = id
        self.content = content
        self.vector = vector or embedding or []
        self.embedding = self.vector  # Alias for backward compatibility
        self.metadata = metadata or {}
        # Store any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)


class VectorStoreConfig:
    """Configuration for vector stores."""

    def __init__(self, **kwargs):
        """Initialize vector store config."""
        for key, value in kwargs.items():
            setattr(self, key, value)
