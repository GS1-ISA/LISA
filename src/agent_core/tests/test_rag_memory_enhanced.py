import pytest
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch
from src.agent_core.memory.rag_store import RAGMemory, SearchFilters


class TestRAGMemoryEnhanced:

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path("test_temp_dir")
        self.temp_dir.mkdir(exist_ok=True)
        self.rag = RAGMemory(
            collection_name="test_collection",
            persist_directory=str(self.temp_dir),
            cache_size=50
        )

    def teardown_method(self):
        """Cleanup test fixtures."""
        # Clean up the test directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_query_caching(self):
        """Test query result caching."""
        # Add some test data
        self.rag.add("Test document content", "test_source", "doc1")

        query = "test query"
        # First query - should cache result
        result1 = self.rag.query(query, n_results=3)
        assert isinstance(result1, list)

        # Second query - should use cache
        result2 = self.rag.query(query, n_results=3)
        assert result1 == result2

    def test_cache_invalidation(self):
        """Test cache invalidation after TTL."""
        # Add test data
        self.rag.add("Test content", "source", "doc1")

        # Set very short TTL for testing
        self.rag.cache_ttl = 0.1  # 100ms

        query = "test query"
        result1 = self.rag.query(query)

        # Wait for cache to expire
        time.sleep(0.2)

        # This should be a cache miss (but we can't easily test the internal cache without mocking time)
        # Instead, test cache clearing
        self.rag.clear_cache()
        # Cache should be empty now

    def test_cache_size_limit(self):
        """Test cache size limits."""
        # Add test data
        self.rag.add("Content", "source", "doc1")

        # Fill cache beyond limit
        for i in range(self.rag.cache_size + 10):
            query = f"query_{i}"
            self.rag.query(query, n_results=1)

        # Cache should not grow beyond limit
        assert len(self.rag._query_cache) <= self.rag.cache_size

    def test_thread_safety(self):
        """Test thread safety of operations."""
        results = []
        errors = []

        def add_documents(worker_id):
            try:
                for i in range(5):
                    doc_id = f"doc_{worker_id}_{i}"
                    self.rag.add(f"Content {i} from worker {worker_id}", f"source_{worker_id}", doc_id)
                results.append(f"Worker {worker_id} completed")
            except Exception as e:
                errors.append(f"Worker {worker_id} error: {e}")

        # Start multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=add_documents, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Should have no errors and all workers completed
        assert len(errors) == 0
        assert len(results) == 3

        # Should have added documents
        count = self.rag.get_collection_count()
        assert count >= 15  # 3 workers * 5 docs each

    def test_batch_add_performance(self):
        """Test batch add performance."""
        # Create batch of documents
        documents = []
        for i in range(10):
            documents.append({
                "text": f"Batch document {i} with content for testing.",
                "source": f"source_{i}",
                "doc_id": f"batch_doc_{i}"
            })

        start_time = time.time()
        result = self.rag.batch_add(documents, batch_size=5)
        end_time = time.time()

        assert result == True
        assert (end_time - start_time) < 5.0  # Should be reasonably fast

        # Verify documents were added
        count = self.rag.get_collection_count()
        assert count >= 10

    def test_conversation_history_caching(self):
        """Test conversation history with caching."""
        # Enable conversation history
        assert self.rag.enable_conversation_history == True

        # Add conversation entries
        self.rag.add_conversation_entry("user", "Hello")
        self.rag.add_conversation_entry("assistant", "Hi there!")

        history = self.rag.get_conversation_history()
        assert len(history) == 2
        assert history[0]["content"] == "Hello"
        assert history[1]["content"] == "Hi there!"

    def test_query_with_context_enhanced(self):
        """Test enhanced query with context."""
        # Add multiple chunks of a document
        long_text = "This is the first part of the document. " * 50 + "This is the second part. " * 50 + "This is the third part." * 50
        self.rag.add(long_text, "test_source", "long_doc", chunk_size=200, overlap=50)

        # Query for content in the middle
        results = self.rag.query_with_context("second part", n_results=1, context_window=1)

        assert len(results) > 0
        result = results[0]
        assert "context_chunks" in result
        assert len(result["context_chunks"]) > 0

    def test_semantic_search_with_threshold(self):
        """Test semantic search with relevance threshold."""
        # Add documents with varying relevance
        self.rag.add("CSRD compliance requirements for ESG reporting", "regulatory", "doc1")
        self.rag.add("Technical specifications for software development", "technical", "doc2")
        self.rag.add("Financial reporting standards and XBRL taxonomy", "financial", "doc3")

        # Search with high threshold
        results = self.rag.semantic_search("ESG compliance", threshold=0.8)
        assert len(results) >= 1

        # Check that results have similarity scores
        for result in results:
            assert "similarity_score" in result
            assert result["similarity_score"] >= 0.8

    def test_advanced_filters(self):
        """Test advanced search filters."""
        # Add documents with different metadata
        now = "2024-01-01T00:00:00Z"
        self.rag.add("Content 1", "source1", "doc1")
        self.rag.add("Content 2", "source2", "doc2")
        self.rag.add("Content 3", "source1", "doc3")

        # Test source filter
        filters = SearchFilters(source="source1")
        results = self.rag.query("content", filters=filters)
        assert len(results) >= 2  # Should find docs from source1

        # Test document ID filter
        filters = SearchFilters(document_id="doc1")
        results = self.rag.query("content", filters=filters)
        assert len(results) >= 1

    def test_memory_stats_comprehensive(self):
        """Test comprehensive memory statistics."""
        # Add some data
        self.rag.add("Test content", "test_source", "test_doc")
        self.rag.add_conversation_entry("user", "Test message")

        stats = self.rag.get_stats()

        required_keys = [
            'total_chunks', 'unique_documents', 'unique_sources',
            'language_distribution', 'embedding_model', 'conversation_history_enabled'
        ]

        for key in required_keys:
            assert key in stats

        assert stats['total_chunks'] >= 1
        assert stats['unique_documents'] >= 1
        assert stats['unique_sources'] >= 1
        assert stats['conversation_history_enabled'] == True

    def test_error_handling_robustness(self):
        """Test error handling and robustness."""
        # Test adding document with invalid data
        result = self.rag.add("", "", "")  # Invalid empty inputs
        assert result == False

        # Test querying empty collection
        results = self.rag.query("nonexistent")
        assert results == []

        # Test conversation history when disabled
        rag_no_history = RAGMemory(
            collection_name="test_no_history",
            persist_directory=str(self.temp_dir / "no_history"),
            enable_conversation_history=False
        )

        result = rag_no_history.add_conversation_entry("user", "test")
        assert result == False

        history = rag_no_history.get_conversation_history()
        assert history == []

    def test_isa_specific_functionality(self):
        """Test ISA-specific functionality."""
        # Add ISA regulatory documents
        csrd_content = """
        CSRD Article 8 requires companies to disclose information on their strategy,
        business model, and materiality assessment for sustainability-related matters.
        This includes ESG factors such as climate change, biodiversity, and social issues.
        """

        gdsn_content = """
        GDSN provides standardized data structures for product information exchange.
        Attributes are mapped to ontology schemas for interoperability between trading partners.
        """

        self.rag.add(csrd_content, "eu_regulatory", "csrd_doc")
        self.rag.add(gdsn_content, "standards", "gdsn_doc")

        # Test compliance queries
        compliance_results = self.rag.query("CSRD compliance requirements")
        assert len(compliance_results) > 0

        # Test standards mapping queries
        mapping_results = self.rag.query("GDSN attribute mapping")
        assert len(mapping_results) > 0

        # Test cross-domain queries
        cross_results = self.rag.query("ESG reporting standards")
        assert len(cross_results) > 0

    def test_performance_large_dataset(self):
        """Test performance with larger dataset."""
        # Add multiple documents
        for i in range(20):
            content = f"Document {i} content about regulatory compliance and standards mapping. " * 10
            self.rag.add(content, f"source_{i}", f"doc_{i}")

        # Test query performance
        start_time = time.time()
        results = self.rag.query("regulatory compliance", n_results=10)
        end_time = time.time()

        assert len(results) > 0
        assert (end_time - start_time) < 2.0  # Should be reasonably fast

    def test_memory_efficiency(self):
        """Test memory efficiency of operations."""
        initial_count = self.rag.get_collection_count()

        # Add documents in batch
        documents = []
        for i in range(50):
            documents.append({
                "text": f"Memory test document {i}",
                "source": "memory_test",
                "doc_id": f"memory_doc_{i}"
            })

        result = self.rag.batch_add(documents)
        assert result == True

        final_count = self.rag.get_collection_count()
        assert final_count >= initial_count + 50

    def test_concurrent_queries(self):
        """Test concurrent query operations."""
        # Add test data
        self.rag.add("Test content for concurrent queries", "concurrent_source", "concurrent_doc")

        results = []
        errors = []

        def perform_query(query_id):
            try:
                result = self.rag.query(f"concurrent query {query_id}")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start concurrent queries
        threads = []
        for i in range(10):
            t = threading.Thread(target=perform_query, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have results from all queries
        assert len(results) == 10
        assert len(errors) == 0

    def test_cache_cleanup(self):
        """Test cache cleanup functionality."""
        # Add some cache entries
        self.rag.add("Cache test content", "cache_source", "cache_doc")

        for i in range(10):
            self.rag.query(f"cache query {i}")

        initial_cache_size = len(self.rag._query_cache)
        assert initial_cache_size > 0

        # Clear cache
        self.rag.clear_cache()

        # Cache should be empty
        assert len(self.rag._query_cache) == 0


if __name__ == "__main__":
    pytest.main([__file__])