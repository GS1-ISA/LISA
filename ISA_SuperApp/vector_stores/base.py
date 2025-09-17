"""
Base vector stores module for ISA SuperApp.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseVectorStores(ABC):
    """Base class for managing multiple vector stores."""

    @abstractmethod
    def get_store(self, store_name: str) -> Any:
        """Get a specific vector store by name."""
        pass

    @abstractmethod
    def create_store(self, store_name: str, **kwargs) -> Any:
        """Create a new vector store."""
        pass

    @abstractmethod
    def delete_store(self, store_name: str) -> None:
        """Delete a vector store."""
        pass
class SearchResult:
    """Result from a vector store search."""

    def __init__(self, document, score, metadata=None):
        """Initialize search result."""
        self.document = document
        self.score = score
        self.metadata = metadata or {}


class VectorStore(BaseVectorStores):
    """Concrete vector store implementation."""

    def __init__(self):
        """Initialize vector store."""
        pass

    def get_store(self, store_name: str):
        """Get a specific vector store by name."""
        # Stub implementation
        return None

    def create_store(self, store_name: str, **kwargs):
        """Create a new vector store."""
        # Stub implementation
        return None

    def delete_store(self, store_name: str) -> None:
        """Delete a vector store."""
        pass

    def list_stores(self) -> list[str]:
        """List all available vector stores."""
        return []

    @abstractmethod
    def list_stores(self) -> list[str]:
        """List all available vector stores."""
        pass
