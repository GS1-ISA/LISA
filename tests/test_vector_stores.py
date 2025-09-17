"""
Tests for vector store functionality.
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from isa_superapp.core.exceptions import VectorStoreError
from isa_superapp.vector_stores.base import SearchResult, VectorStore
from isa_superapp.vector_stores.chroma_store import ChromaVectorStore
from isa_superapp.vector_stores.faiss_store import FaissVectorStore
from isa_superapp.vector_stores.memory_store import MemoryVectorStore


class TestVectorStoreBase:
    """Test cases for VectorStore base class."""

    def test_vector_store_interface(self):
        """Test that VectorStore defines the required interface."""
        # VectorStore should be abstract
        with pytest.raises(TypeError):
            VectorStore()

    def test_search_result_model(self):
        """Test SearchResult model."""
        result = SearchResult(
            content="Test content",
            score=0.85,
            metadata={"source": "test", "id": "doc1"},
            embedding=[0.1, 0.2, 0.3],
        )

        assert result.content == "Test content"
        assert result.score == 0.85
        assert result.metadata["source"] == "test"
        assert result.embedding == [0.1, 0.2, 0.3]

        # Test with minimal fields
        minimal_result = SearchResult(content="Minimal content", score=0.5)

        assert minimal_result.content == "Minimal content"
        assert minimal_result.score == 0.5
        assert minimal_result.metadata == {}
        assert minimal_result.embedding is None


class TestMemoryVectorStore:
    """Test cases for MemoryVectorStore."""

    @pytest.fixture
    def memory_store(self):
        """Create a MemoryVectorStore instance."""
        return MemoryVectorStore(
            collection_name="test_collection", embedding_dimension=384
        )

    def test_initialization(self, memory_store):
        """Test memory store initialization."""
        assert memory_store.collection_name == "test_collection"
        assert memory_store.embedding_dimension == 384
        assert memory_store.documents == {}
        assert memory_store.embeddings == []

    @pytest.mark.asyncio
    async def test_add_document(self, memory_store):
        """Test adding a single document."""
        doc_id = "doc1"
        content = "This is a test document"
        embedding = np.random.rand(384).tolist()
        metadata = {"source": "test", "type": "document"}

        await memory_store.add(
            doc_id=doc_id, content=content, embedding=embedding, metadata=metadata
        )

        # Verify document was added
        assert doc_id in memory_store.documents
        assert memory_store.documents[doc_id]["content"] == content
        assert memory_store.documents[doc_id]["metadata"] == metadata

        # Verify embedding was added
        assert len(memory_store.embeddings) == 1
        assert memory_store.embeddings[0] == embedding

    @pytest.mark.asyncio
    async def test_add_multiple_documents(self, memory_store):
        """Test adding multiple documents."""
        documents = []
        for i in range(5):
            documents.append(
                {
                    "doc_id": f"doc{i}",
                    "content": f"Document {i} content",
                    "embedding": np.random.rand(384).tolist(),
                    "metadata": {"index": i},
                }
            )

        await memory_store.add_batch(documents)

        # Verify all documents were added
        assert len(memory_store.documents) == 5
        assert len(memory_store.embeddings) == 5

        # Verify document contents
        for i in range(5):
            doc_id = f"doc{i}"
            assert doc_id in memory_store.documents
            assert memory_store.documents[doc_id]["content"] == f"Document {i} content"

    @pytest.mark.asyncio
    async def test_search_documents(self, memory_store):
        """Test searching documents."""
        # Add test documents
        test_docs = [
            {
                "doc_id": "py_doc",
                "content": "Python is a programming language",
                "embedding": [0.9, 0.8, 0.7]
                + [0.1] * 381,  # High similarity to programming
                "metadata": {"topic": "programming"},
            },
            {
                "doc_id": "cooking_doc",
                "content": "Cooking is about preparing food",
                "embedding": [0.2, 0.3, 0.1]
                + [0.1] * 381,  # Low similarity to programming
                "metadata": {"topic": "cooking"},
            },
        ]

        await memory_store.add_batch(test_docs)

        # Search with programming-related embedding
        query_embedding = [0.8, 0.7, 0.6] + [0.1] * 381
        results = await memory_store.search(
            query="programming languages", query_embedding=query_embedding, limit=2
        )

        assert isinstance(results, list)
        assert len(results) == 2

        # Verify results are sorted by score
        scores = [result.score for result in results]
        assert scores == sorted(scores, reverse=True)

        # Programming document should have higher score
        assert results[0].content == "Python is a programming language"
        assert results[0].metadata["topic"] == "programming"

    @pytest.mark.asyncio
    async def test_search_with_threshold(self, memory_store):
        """Test searching with similarity threshold."""
        # Add documents with different similarity scores
        docs = [
            {
                "doc_id": f"doc{i}",
                "content": f"Document {i}",
                "embedding": [0.9 - (i * 0.1)] * 384,  # Decreasing similarity
                "metadata": {"index": i},
            }
            for i in range(5)
        ]

        await memory_store.add_batch(docs)

        # Search with threshold
        query_embedding = [0.9] * 384
        results = await memory_store.search(
            query="test query", query_embedding=query_embedding, threshold=0.7
        )

        # Only documents with score >= 0.7 should be returned
        assert all(result.score >= 0.7 for result in results)
        assert len(results) <= 5

    @pytest.mark.asyncio
    async def test_search_with_filtering(self, memory_store):
        """Test searching with metadata filtering."""
        # Add documents with different metadata
        docs = [
            {
                "doc_id": f"doc{i}",
                "content": f"Document {i}",
                "embedding": [0.8] * 384,
                "metadata": {"category": "A" if i < 3 else "B", "index": i},
            }
            for i in range(5)
        ]

        await memory_store.add_batch(docs)

        # Search with filter
        query_embedding = [0.8] * 384
        results = await memory_store.search(
            query="test query",
            query_embedding=query_embedding,
            filter_dict={"category": "A"},
        )

        # Only documents with category "A" should be returned
        assert all(result.metadata["category"] == "A" for result in results)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_document(self, memory_store):
        """Test getting a specific document."""
        # Add a document
        doc_id = "test_doc"
        content = "Test document content"
        embedding = np.random.rand(384).tolist()
        metadata = {"test": True}

        await memory_store.add(doc_id, content, embedding, metadata)

        # Retrieve the document
        document = await memory_store.get(doc_id)

        assert document is not None
        assert document["content"] == content
        assert document["metadata"] == metadata
        assert document["embedding"] == embedding

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self, memory_store):
        """Test getting a non-existent document."""
        document = await memory_store.get("nonexistent")
        assert document is None

    @pytest.mark.asyncio
    async def test_delete_document(self, memory_store):
        """Test deleting a document."""
        # Add a document
        doc_id = "doc_to_delete"
        await memory_store.add(
            doc_id=doc_id,
            content="Content to delete",
            embedding=np.random.rand(384).tolist(),
            metadata={"to_delete": True},
        )

        # Verify it exists
        assert doc_id in memory_store.documents

        # Delete the document
        await memory_store.delete(doc_id)

        # Verify it was deleted
        assert doc_id not in memory_store.documents
        assert await memory_store.get(doc_id) is None

    @pytest.mark.asyncio
    async def test_update_document(self, memory_store):
        """Test updating a document."""
        # Add a document
        doc_id = "doc_to_update"
        original_content = "Original content"
        await memory_store.add(
            doc_id=doc_id,
            content=original_content,
            embedding=np.random.rand(384).tolist(),
            metadata={"version": 1},
        )

        # Update the document
        new_content = "Updated content"
        new_embedding = np.random.rand(384).tolist()
        new_metadata = {"version": 2, "updated": True}

        await memory_store.update(
            doc_id=doc_id,
            content=new_content,
            embedding=new_embedding,
            metadata=new_metadata,
        )

        # Verify the update
        updated_doc = await memory_store.get(doc_id)
        assert updated_doc["content"] == new_content
        assert updated_doc["metadata"] == new_metadata
        assert updated_doc["embedding"] == new_embedding

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, memory_store):
        """Test getting collection statistics."""
        # Add some documents
        for i in range(3):
            await memory_store.add(
                doc_id=f"doc{i}",
                content=f"Document {i}",
                embedding=np.random.rand(384).tolist(),
                metadata={"index": i},
            )

        stats = await memory_store.get_collection_stats()

        assert stats["count"] == 3
        assert stats["dimension"] == 384
        assert stats["collection_name"] == "test_collection"

    @pytest.mark.asyncio
    async def test_clear_collection(self, memory_store):
        """Test clearing the collection."""
        # Add some documents
        for i in range(3):
            await memory_store.add(
                doc_id=f"doc{i}",
                content=f"Document {i}",
                embedding=np.random.rand(384).tolist(),
            )

        # Clear the collection
        await memory_store.clear()

        # Verify collection is empty
        assert len(memory_store.documents) == 0
        assert len(memory_store.embeddings) == 0

    @pytest.mark.asyncio
    async def test_search_empty_collection(self, memory_store):
        """Test searching an empty collection."""
        results = await memory_store.search(
            query="test query", query_embedding=np.random.rand(384).tolist()
        )

        assert isinstance(results, list)
        assert len(results) == 0


class TestChromaVectorStore:
    """Test cases for ChromaVectorStore."""

    @pytest.fixture
    def mock_chroma_client(self):
        """Create a mock ChromaDB client."""
        client = Mock()

        # Mock collection
        collection = Mock()
        collection.add = Mock()
        collection.get = Mock(
            return_value={
                "ids": ["doc1"],
                "documents": ["Test document"],
                "metadatas": [{"test": True}],
                "embeddings": [[0.1] * 384],
            }
        )
        collection.query = Mock(
            return_value={
                "ids": [["doc1", "doc2"]],
                "documents": [["Doc 1", "Doc 2"]],
                "metadatas": [[{"id": "1"}, {"id": "2"}]],
                "distances": [[0.1, 0.2]],
                "embeddings": [[[0.1] * 384, [0.2] * 384]],
            }
        )
        collection.delete = Mock()
        collection.update = Mock()
        collection.count = Mock(return_value=5)

        client.get_or_create_collection = Mock(return_value=collection)
        client.delete_collection = Mock()

        return client

    @pytest.fixture
    def chroma_store(self, mock_chroma_client):
        """Create a ChromaVectorStore instance."""
        with patch(
            "isa_superapp.vector_stores.chroma_store.chromadb.Client",
            return_value=mock_chroma_client,
        ):
            return ChromaVectorStore(
                collection_name="test_collection",
                embedding_dimension=384,
                persist_directory="/tmp/chroma_test",
            )

    def test_initialization(self, chroma_store):
        """Test Chroma store initialization."""
        assert chroma_store.collection_name == "test_collection"
        assert chroma_store.embedding_dimension == 384
        assert chroma_store.persist_directory == "/tmp/chroma_test"
        assert chroma_store.collection is not None

    @pytest.mark.asyncio
    async def test_add_document(self, chroma_store):
        """Test adding a document to Chroma."""
        doc_id = "doc1"
        content = "Test document"
        embedding = np.random.rand(384).tolist()
        metadata = {"source": "test"}

        await chroma_store.add(doc_id, content, embedding, metadata)

        # Verify collection.add was called
        chroma_store.collection.add.assert_called_once_with(
            ids=[doc_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    @pytest.mark.asyncio
    async def test_search_documents(self, chroma_store):
        """Test searching documents in Chroma."""
        query_embedding = np.random.rand(384).tolist()

        results = await chroma_store.search(
            query="test query", query_embedding=query_embedding, limit=2
        )

        assert isinstance(results, list)
        assert len(results) == 2

        # Verify collection.query was called
        chroma_store.collection.query.assert_called_once_with(
            query_embeddings=[query_embedding],
            n_results=2,
            where=None,
            where_document=None,
        )

        # Verify results are SearchResult instances
        assert all(isinstance(result, SearchResult) for result in results)
        assert results[0].score > results[1].score  # Higher score first

    @pytest.mark.asyncio
    async def test_search_with_filtering(self, chroma_store):
        """Test searching with metadata filtering."""
        query_embedding = np.random.rand(384).tolist()
        filter_dict = {"source": "test"}

        await chroma_store.search(
            query="test query", query_embedding=query_embedding, filter_dict=filter_dict
        )

        # Verify filter was passed
        chroma_store.collection.query.assert_called_once_with(
            query_embeddings=[query_embedding],
            n_results=10,
            where=filter_dict,
            where_document=None,
        )

    @pytest.mark.asyncio
    async def test_get_document(self, chroma_store):
        """Test getting a document from Chroma."""
        document = await chroma_store.get("doc1")

        assert document is not None
        assert document["content"] == "Test document"
        assert document["metadata"]["test"] is True
        assert document["embedding"] == [0.1] * 384

    @pytest.mark.asyncio
    async def test_delete_document(self, chroma_store):
        """Test deleting a document from Chroma."""
        await chroma_store.delete("doc1")

        # Verify collection.delete was called
        chroma_store.collection.delete.assert_called_once_with(ids=["doc1"])

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, chroma_store):
        """Test getting collection statistics from Chroma."""
        stats = await chroma_store.get_collection_stats()

        assert stats["count"] == 5
        assert stats["collection_name"] == "test_collection"

    @pytest.mark.asyncio
    async def test_clear_collection(self, chroma_store):
        """Test clearing the Chroma collection."""
        await chroma_store.clear()

        # Verify collection was deleted and recreated
        chroma_store.client.delete_collection.assert_called_once_with("test_collection")
        chroma_store.client.get_or_create_collection.assert_called()


class TestFaissVectorStore:
    """Test cases for FaissVectorStore."""

    @pytest.fixture
    def mock_faiss_index(self):
        """Create a mock FAISS index."""
        index = Mock()
        index.ntotal = 5
        index.d = 384
        index.add = Mock()
        index.search = Mock(
            return_value=(
                np.array([[0.1, 0.2]]),  # distances
                np.array([[0, 1]]),  # indices
            )
        )
        index.reset = Mock()

        return index

    @pytest.fixture
    def mock_faiss(self, mock_faiss_index):
        """Create mock FAISS module."""
        faiss = Mock()
        faiss.IndexFlatIP = Mock(return_value=mock_faiss_index)
        faiss.normalize_L2 = Mock()

        return faiss

    @pytest.fixture
    def faiss_store(self, mock_faiss):
        """Create a FaissVectorStore instance."""
        with patch("isa_superapp.vector_stores.faiss_store.faiss", mock_faiss):
            store = FaissVectorStore(
                collection_name="test_collection",
                embedding_dimension=384,
                index_type="IndexFlatIP",
            )
            store.documents = {
                "0": {"content": "Doc 1", "metadata": {"id": "1"}},
                "1": {"content": "Doc 2", "metadata": {"id": "2"}},
            }
            return store

    def test_initialization(self, faiss_store):
        """Test FAISS store initialization."""
        assert faiss_store.collection_name == "test_collection"
        assert faiss_store.embedding_dimension == 384
        assert faiss_store.index_type == "IndexFlatIP"
        assert faiss_store.index is not None

    @pytest.mark.asyncio
    async def test_add_document(self, faiss_store):
        """Test adding a document to FAISS."""
        doc_id = "doc3"
        content = "New document"
        embedding = np.random.rand(384).tolist()
        metadata = {"source": "test"}

        await faiss_store.add(doc_id, content, embedding, metadata)

        # Verify index.add was called
        faiss_store.index.add.assert_called_once()

        # Verify document was added to storage
        assert doc_id in faiss_store.documents
        assert faiss_store.documents[doc_id]["content"] == content

    @pytest.mark.asyncio
    async def test_search_documents(self, faiss_store):
        """Test searching documents in FAISS."""
        query_embedding = np.random.rand(384).tolist()

        results = await faiss_store.search(
            query="test query", query_embedding=query_embedding, limit=2
        )

        assert isinstance(results, list)
        assert len(results) == 2

        # Verify index.search was called
        faiss_store.index.search.assert_called_once()

        # Verify results are SearchResult instances
        assert all(isinstance(result, SearchResult) for result in results)

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, faiss_store):
        """Test getting collection statistics from FAISS."""
        stats = await faiss_store.get_collection_stats()

        assert stats["count"] == 5
        assert stats["dimension"] == 384
        assert stats["collection_name"] == "test_collection"

    @pytest.mark.asyncio
    async def test_clear_collection(self, faiss_store):
        """Test clearing the FAISS collection."""
        await faiss_store.clear()

        # Verify index was reset
        faiss_store.index.reset.assert_called_once()

        # Verify documents were cleared
        assert len(faiss_store.documents) == 0


class TestVectorStoreIntegration:
    """Integration tests for vector stores."""

    @pytest.fixture
    def memory_store(self):
        """Create a MemoryVectorStore for integration tests."""
        return MemoryVectorStore(
            collection_name="integration_test", embedding_dimension=384
        )

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing."""
        return [
            {
                "doc_id": f"doc_{i}",
                "content": f"This is document {i} about topic {i % 3}",
                "embedding": (
                    [0.9 - (i % 3) * 0.3] * 128 + [0.1] * 256
                ),  # Different embeddings
                "metadata": {"topic": f"topic_{i % 3}", "index": i, "category": "test"},
            }
            for i in range(9)
        ]

    @pytest.mark.asyncio
    async def test_full_document_lifecycle(self, memory_store, sample_documents):
        """Test complete document lifecycle: add, search, update, delete."""
        # Add documents
        await memory_store.add_batch(sample_documents)

        # Verify documents were added
        stats = await memory_store.get_collection_stats()
        assert stats["count"] == 9

        # Search for documents
        query_embedding = [0.8] * 128 + [0.1] * 256  # Similar to topic 0
        results = await memory_store.search(
            query="topic 0 documents", query_embedding=query_embedding, limit=3
        )

        assert len(results) == 3
        assert all("topic 0" in result.content for result in results)

        # Update a document
        doc_to_update = "doc_0"
        new_content = "Updated content for document 0"
        new_embedding = [0.95] * 384
        new_metadata = {"topic": "topic_0", "updated": True}

        await memory_store.update(
            doc_id=doc_to_update,
            content=new_content,
            embedding=new_embedding,
            metadata=new_metadata,
        )

        # Verify update
        updated_doc = await memory_store.get(doc_to_update)
        assert updated_doc["content"] == new_content
        assert updated_doc["metadata"]["updated"] is True

        # Delete a document
        doc_to_delete = "doc_8"
        await memory_store.delete(doc_to_delete)

        # Verify deletion
        deleted_doc = await memory_store.get(doc_to_delete)
        assert deleted_doc is None

        # Verify final count
        final_stats = await memory_store.get_collection_stats()
        assert final_stats["count"] == 8

    @pytest.mark.asyncio
    async def test_search_with_different_parameters(
        self, memory_store, sample_documents
    ):
        """Test searching with various parameters."""
        await memory_store.add_batch(sample_documents)

        # Test with different limits
        query_embedding = [0.7] * 128 + [0.1] * 256
        results_limit_2 = await memory_store.search(
            query="test query", query_embedding=query_embedding, limit=2
        )
        results_limit_5 = await memory_store.search(
            query="test query", query_embedding=query_embedding, limit=5
        )

        assert len(results_limit_2) == 2
        assert len(results_limit_5) == 5

        # Test with threshold
        results_with_threshold = await memory_store.search(
            query="test query", query_embedding=query_embedding, threshold=0.5
        )

        assert all(result.score >= 0.5 for result in results_with_threshold)

        # Test with filtering
        results_filtered = await memory_store.search(
            query="test query",
            query_embedding=query_embedding,
            filter_dict={"topic": "topic_1"},
        )

        assert all(result.metadata["topic"] == "topic_1" for result in results_filtered)
        assert len(results_filtered) == 3  # Should return 3 documents with topic_1

    @pytest.mark.asyncio
    async def test_batch_operations(self, memory_store):
        """Test batch add and search operations."""
        # Create batch of documents
        batch_size = 20
        documents = []
        for i in range(batch_size):
            documents.append(
                {
                    "doc_id": f"batch_doc_{i}",
                    "content": f"Batch document {i}",
                    "embedding": np.random.rand(384).tolist(),
                    "metadata": {"batch": True, "index": i},
                }
            )

        # Add batch
        await memory_store.add_batch(documents)

        # Verify batch was added
        stats = await memory_store.get_collection_stats()
        assert stats["count"] == batch_size

        # Test search after batch add
        query_embedding = np.random.rand(384).tolist()
        results = await memory_store.search(
            query="batch document", query_embedding=query_embedding, limit=5
        )

        assert len(results) == 5
        assert all("batch" in result.content for result in results)


class TestVectorStorePerformance:
    """Performance tests for vector stores."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_large_scale_operations(self):
        """Test performance with large number of documents."""
        import time

        store = MemoryVectorStore(
            collection_name="performance_test", embedding_dimension=384
        )

        # Create large dataset
        num_docs = 1000
        documents = []
        for i in range(num_docs):
            documents.append(
                {
                    "doc_id": f"perf_doc_{i}",
                    "content": f"Performance test document {i} with some content",
                    "embedding": np.random.rand(384).tolist(),
                    "metadata": {"index": i, "category": f"cat_{i % 10}"},
                }
            )

        # Test batch add performance
        start_time = time.time()
        await store.add_batch(documents)
        add_time = time.time() - start_time

        # Test search performance
        query_embedding = np.random.rand(384).tolist()
        start_time = time.time()
        await store.search(
            query="performance test", query_embedding=query_embedding, limit=10
        )
        search_time = time.time() - start_time

        # Test get stats performance
        start_time = time.time()
        stats = await store.get_collection_stats()
        stats_time = time.time() - start_time

        # Performance assertions
        assert add_time < 5.0  # Should add 1000 docs in less than 5 seconds
        assert search_time < 1.0  # Should search in less than 1 second
        assert stats_time < 0.1  # Should get stats in less than 0.1 seconds
        assert stats["count"] == num_docs

        print(f"Added {num_docs} documents in {add_time:.3f} seconds")
        print(f"Searched {num_docs} documents in {search_time:.3f} seconds")
        print(f"Got stats in {stats_time:.3f} seconds")

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_search_accuracy(self):
        """Test search accuracy with known similar documents."""
        store = MemoryVectorStore(
            collection_name="accuracy_test", embedding_dimension=384
        )

        # Create documents with known similarity relationships
        base_embedding = np.random.rand(384)

        documents = []
        for i in range(10):
            # Create documents with decreasing similarity to base
            similarity = 1.0 - (i * 0.1)
            noise = np.random.rand(384) * 0.1
            embedding = (base_embedding * similarity + noise).tolist()

            documents.append(
                {
                    "doc_id": f"sim_doc_{i}",
                    "content": f"Document with similarity {similarity:.1f}",
                    "embedding": embedding,
                    "metadata": {"similarity": similarity, "index": i},
                }
            )

        await store.add_batch(documents)

        # Search using base embedding
        results = await store.search(
            query="base document", query_embedding=base_embedding.tolist(), limit=10
        )

        # Verify results are ordered by similarity
        similarities = [result.metadata["similarity"] for result in results]
        assert similarities == sorted(similarities, reverse=True)

        # Verify highest similarity documents are returned first
        assert results[0].metadata["similarity"] > 0.9
        assert results[-1].metadata["similarity"] < 0.2


class TestVectorStoreErrorHandling:
    """Error handling tests for vector stores."""

    @pytest.mark.asyncio
    async def test_add_document_with_wrong_dimension(self):
        """Test adding document with wrong embedding dimension."""
        store = MemoryVectorStore(collection_name="error_test", embedding_dimension=384)

        # Try to add document with wrong dimension
        with pytest.raises(VectorStoreError):
            await store.add(
                doc_id="wrong_dim_doc",
                content="Test content",
                embedding=[0.1] * 100,  # Wrong dimension
                metadata={},
            )

    @pytest.mark.asyncio
    async def test_search_with_wrong_dimension(self):
        """Test searching with wrong embedding dimension."""
        store = MemoryVectorStore(collection_name="error_test", embedding_dimension=384)

        # Add a document first
        await store.add(
            doc_id="test_doc",
            content="Test content",
            embedding=np.random.rand(384).tolist(),
            metadata={},
        )

        # Try to search with wrong dimension
        with pytest.raises(VectorStoreError):
            await store.search(
                query="test query",
                query_embedding=[0.1] * 100,  # Wrong dimension
            )
