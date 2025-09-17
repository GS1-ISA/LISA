"""
Memory vector store implementation for ISA SuperApp.
"""

from typing import Any

from .base import SearchResult, VectorStore


class MemoryVectorStore(VectorStore):
    """In-memory vector store implementation."""

    def __init__(self, dimension: int = 384, **kwargs):
        """Initialize memory vector store."""
        super().__init__()
        self.dimension = dimension
        self.vectors = []
        self.metadata = []
        self.ids = []

    def add_vectors(self, vectors: list[list[float]], metadata: list[dict[str, Any]] = None) -> None:
        """Add vectors to the store."""
        self.vectors.extend(vectors)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(vectors))
        self.ids.extend([f"id_{len(self.ids) + i}" for i in range(len(vectors))])

    def search(self, query_vector: list[float], top_k: int = 10) -> list[SearchResult]:
        """Search for similar vectors."""
        # Simple cosine similarity (stub implementation)
        results = []
        for i, _vector in enumerate(self.vectors):
            # Mock similarity score
            score = 0.9 - (i * 0.1) if i < top_k else 0.1
            results.append(SearchResult(
                document={"id": self.ids[i], "content": f"Document {i}"},
                score=score,
                metadata=self.metadata[i]
            ))
        return results[:top_k]

    def delete(self, ids: list[str]) -> None:
        """Delete vectors by IDs."""
        indices_to_remove = []
        for i, doc_id in enumerate(self.ids):
            if doc_id in ids:
                indices_to_remove.append(i)

        for i in reversed(indices_to_remove):
            del self.vectors[i]
            del self.metadata[i]
            del self.ids[i]
