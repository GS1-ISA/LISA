"""
Vector store integration for ETL system.

This module provides integration with ISA_D's vector store for
storing processed ETL data.
"""

from typing import Any

from isa_superapp.etl.core.logger import get_logger

# Import from parent ISA_SuperApp
try:
    from isa_superapp.core.vector_store import VectorStoreConfig
    from isa_superapp.core.vector_store import (
        create_vector_store as isa_create_vector_store,
    )
except ImportError:
    # Fallback if import fails
    isa_create_vector_store = None
    VectorStoreConfig = None


logger = get_logger("etl.vector_store")


async def create_vector_store(
    provider: str = "chroma",
    collection_name: str = "isa_etl_data",
    dimension: int = 384,
    **kwargs
) -> Any:
    """Create a vector store instance for ETL data."""
    if isa_create_vector_store:
        # Use ISA_D's vector store factory
        return await isa_create_vector_store(
            provider=provider,
            collection_name=collection_name,
            dimension=dimension,
            **kwargs
        )
    else:
        # Fallback implementation
        logger.warning("ISA_D vector store not available, using mock implementation")
        return MockVectorStore()


class MockVectorStore:
    """Mock vector store for development/testing."""

    def __init__(self):
        self.vectors = []
        logger.info("Mock vector store initialized")

    async def add_vectors(self, vectors: list[dict[str, Any]]) -> None:
        """Add vectors to mock store."""
        self.vectors.extend(vectors)
        logger.info(f"Added {len(vectors)} vectors to mock store")

    async def search(
        self,
        query_vector: list[float],
        k: int = 10,
        **kwargs
    ) -> list[dict[str, Any]]:
        """Mock search implementation."""
        # Return mock results
        return [{
            "id": f"mock_{i}",
            "score": 0.9 - i * 0.1,
            "metadata": {"mock": True}
        } for i in range(min(k, 5))]
