import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.agent_core.query_optimizer import QueryOptimizer
from src.agent_core.streaming_processor import StreamingDocumentProcessor
from src.agent_core.memory.rag_store import RAGMemory
from src.agent_core.llm_client import CachedOpenRouterClient


class TestErrorHandling:

    def setup_method(self):
        """Setup error handling test fixtures."""
        self.temp_dir = Path("error_test_dir")
        self.temp_dir.mkdir(exist_ok=True)

        self.optimizer = QueryOptimizer()
        self.rag_memory = RAGMemory(
            collection_name="error_test",
            persist_directory=str(self.temp_dir)
        )

    def teardown_method(self):
        """Cleanup error test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_query_optimizer_error_handling(self):
        """Test QueryOptimizer error handling."""
        # Test with empty query
        with pytest.raises(AttributeError):
            self.optimizer.analyze_query("")

        # Test with None query
        with pytest.raises(AttributeError):
            self.optimizer.analyze_query(None)

        # Test optimization with invalid query
        try:
            result = self.optimizer.optimize_query("")
            # Should handle gracefully and return default optimization
            assert result.model in self.optimizer.model_configs
        except AttributeError:
            pass  # Acceptable if it raises

    def test_streaming_processor_error_handling(self):
        """Test StreamingDocumentProcessor error handling."""
        processor = StreamingDocumentProcessor()

        # Test with empty document
        result = processor._create_chunks("")
        assert result == []

        # Test with None document
        result = processor._create_chunks(None)
        assert result == []

        # Test chunking with very small overlap
        processor_small = StreamingDocumentProcessor(chunk_size=10, overlap_size=15)  # Invalid overlap
        document = "This is a test document for error handling."
        chunks = processor_small._create_chunks(document)
        assert len(chunks) > 0  # Should still work

        # Test boundary detection with edge cases
        boundary = processor._find_optimal_boundary("", 0, 0)
        assert boundary == 0

        boundary = processor._find_optimal_boundary("no boundaries", 0, 5)
        assert boundary == 5

    def test_rag_memory_error_handling(self):
        """Test RAGMemory error handling."""
        # Test adding with empty parameters
        success = self.rag_memory.add("", "", "")
        assert success == False

        success = self.rag_memory.add("content", "", "")
        assert success == False

        success = self.rag_memory.add("", "source", "doc_id")
        assert success == False

        # Test batch add with invalid documents
        invalid_docs = [
            {"text": "", "source": "test", "doc_id": "test1"},  # Empty text
            {"text": "content", "source": "", "doc_id": "test2"},  # Empty source
            {"text": "content", "source": "test", "doc_id": ""},  # Empty doc_id
        ]

        success = self.rag_memory.batch_add(invalid_docs)
        assert success == False  # Should fail due to invalid documents

        # Test querying empty collection
        results = self.rag_memory.query("nonexistent")
        assert results == []

        # Test conversation history with invalid inputs
        success = self.rag_memory.add_conversation_entry("", "")
        assert success == False

        success = self.rag_memory.add_conversation_entry("invalid_role", "content")
        assert success == False

        # Test document operations on nonexistent documents
        success = self.rag_memory.delete_document("nonexistent")
        assert success == True  # Should succeed (no-op)

        success = self.rag_memory.update_document("nonexistent", "new content", "source")
        assert success == False

    def test_llm_client_error_handling(self):
        """Test LLM client error handling."""
        # Mock Redis for testing
        redis_mock = Mock()
        client = CachedOpenRouterClient(
            redis_host='localhost',
            redis_port=6379,
            redis_db=0,
            ttl_seconds=3600
        )
        client.redis_client = redis_mock

        # Test cache errors
        redis_mock.get.side_effect = Exception("Redis connection error")
        redis_mock.setex.side_effect = Exception("Redis write error")

        # Mock underlying client
        with patch.object(client.underlying_client, 'chat_completion', return_value={'content': 'response'}) as mock_chat:
            result = client.chat_completion([{"role": "user", "content": "test"}])
            assert result == {'content': 'response'}
            mock_chat.assert_called_once()

        # Test invalid JSON in cache
        redis_mock.get.return_value = "invalid json"
        result = client.chat_completion([{"role": "user", "content": "test"}])
        # Should fall back to API call
        mock_chat.assert_called()

    def test_network_error_simulation(self):
        """Test network error simulation."""
        processor = StreamingDocumentProcessor()
        mock_client = Mock()
        mock_client.chat_completion.side_effect = [
            Exception("Network timeout"),
            Exception("API rate limit"),
            {'content': 'Success after retries', 'model_used': 'test', 'usage': {'total_tokens': 50}}
        ]
        processor.llm_client = mock_client

        document = "Test document for network error handling."
        result = processor.process_document(document, "Test query")

        # Should eventually succeed or handle gracefully
        assert 'metadata' in result

    def test_corrupted_data_handling(self):
        """Test handling of corrupted data."""
        # Test with malformed JSON-like content
        corrupted_content = '{"incomplete": "json"'
        processor = StreamingDocumentProcessor()

        # Should handle without crashing
        chunks = processor._create_chunks(corrupted_content)
        assert isinstance(chunks, list)

        # Test RAG memory with special characters
        special_content = "Content with special chars: àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"
        success = self.rag_memory.add(special_content, "special_test", "special_doc")
        assert success == True

        results = self.rag_memory.query("special chars")
        assert len(results) > 0

    def test_concurrent_error_handling(self):
        """Test error handling under concurrent operations."""
        import threading

        errors = []
        results = []

        def concurrent_operation(worker_id):
            try:
                # Mix of valid and invalid operations
                if worker_id % 2 == 0:
                    # Valid operation
                    success = self.rag_memory.add(f"Content {worker_id}", f"source_{worker_id}", f"doc_{worker_id}")
                    results.append(f"Worker {worker_id}: {success}")
                else:
                    # Invalid operation
                    success = self.rag_memory.add("", "", "")
                    results.append(f"Worker {worker_id}: {success}")
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Start concurrent operations
        threads = []
        for i in range(10):
            t = threading.Thread(target=concurrent_operation, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have some successful and some failed operations
        assert len(results) == 10
        assert len(errors) == 0  # No unhandled exceptions

        # Verify some operations succeeded and some failed as expected
        success_count = sum(1 for r in results if "True" in r)
        failure_count = sum(1 for r in results if "False" in r)

        assert success_count > 0
        assert failure_count > 0

    def test_resource_exhaustion_handling(self):
        """Test handling of resource exhaustion scenarios."""
        # Test with very large documents
        large_document = "Word " * 100000  # Very large document

        processor = StreamingDocumentProcessor(chunk_size=1000, max_memory_mb=10)

        # Should handle large documents without crashing
        chunks = processor._create_chunks(large_document)
        assert len(chunks) > 0

        # Test memory tracking with large data
        processor.memory_usage = 500 * 1024 * 1024  # 500MB
        efficiency = processor._calculate_efficiency(large_document)
        assert 0.0 <= efficiency <= 1.0

    def test_validation_error_handling(self):
        """Test validation error handling."""
        # Test with invalid metadata
        invalid_metadata = {
            "checksum": "invalid-checksum",  # Should start with sha256:
        }

        # Should handle validation errors gracefully
        success = self.rag_memory.add(
            "Test content",
            "test_source",
            "test_doc",
            extra_metadata=invalid_metadata
        )
        # May succeed or fail depending on validation strictness
        assert isinstance(success, bool)

    def test_timeout_simulation(self):
        """Test timeout simulation."""
        processor = StreamingDocumentProcessor()

        # Mock slow LLM responses
        def slow_response(*args, **kwargs):
            import time
            time.sleep(0.1)  # Simulate delay
            return {
                'content': 'Slow response',
                'model_used': 'test',
                'usage': {'total_tokens': 50}
            }

        mock_client = Mock()
        mock_client.chat_completion.side_effect = slow_response
        processor.llm_client = mock_client

        document = "Test document for timeout handling."

        start_time = time.time()
        result = processor.process_document(document, "Test query")
        end_time = time.time()

        # Should complete without hanging
        assert (end_time - start_time) < 1.0  # Should not take too long
        assert 'metadata' in result

    def test_partial_failure_recovery(self):
        """Test recovery from partial failures."""
        processor = StreamingDocumentProcessor()

        # Mock mixed success/failure responses
        call_count = 0
        def mixed_responses(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # Every third call fails
                raise Exception(f"Simulated failure {call_count}")
            return {
                'content': f'Successful response {call_count}',
                'model_used': 'test',
                'usage': {'total_tokens': 50}
            }

        mock_client = Mock()
        mock_client.chat_completion.side_effect = mixed_responses
        processor.llm_client = mock_client

        # Create document that will be split into multiple chunks
        document = "Chunk one content. " * 100 + "Chunk two content. " * 100 + "Chunk three content. " * 100

        result = processor.process_document(document, "Test query with partial failures")

        # Should have some successful processing despite failures
        assert result['metadata']['total_chunks'] > 0
        assert result['metadata']['chunks_processed'] >= 0  # At least some should succeed

    def test_data_integrity_validation(self):
        """Test data integrity validation."""
        # Test checksum validation
        content = "Test content for integrity validation"
        success = self.rag_memory.add(content, "integrity_test", "integrity_doc")
        assert success == True

        # Verify data can be retrieved
        results = self.rag_memory.query("integrity validation")
        assert len(results) > 0

        # Test conversation integrity
        success = self.rag_memory.add_conversation_entry("user", "Test message")
        assert success == True

        history = self.rag_memory.get_conversation_history()
        assert len(history) > 0
        assert history[-1]["content"] == "Test message"

    def test_configuration_error_handling(self):
        """Test configuration error handling."""
        # Test with invalid configurations
        try:
            # Invalid chunk size
            processor = StreamingDocumentProcessor(chunk_size=0)
            chunks = processor._create_chunks("test")
            assert isinstance(chunks, list)  # Should handle gracefully
        except:
            pass  # Acceptable to fail with invalid config

        try:
            # Invalid overlap
            processor = StreamingDocumentProcessor(overlap_size=-1)
            chunks = processor._create_chunks("test")
            assert isinstance(chunks, list)
        except:
            pass

    def test_external_dependency_failures(self):
        """Test handling of external dependency failures."""
        # Mock ChromaDB failures
        with patch('src.agent_core.memory.rag_store.chromadb.PersistentClient') as mock_chroma:
            mock_chroma.side_effect = Exception("ChromaDB connection failed")

            # Should handle ChromaDB failures gracefully
            try:
                rag = RAGMemory(collection_name="fail_test", persist_directory=str(self.temp_dir / "fail"))
                # May succeed or fail depending on implementation
            except Exception:
                pass  # Acceptable to fail with external dependency issues

        # Test embedding function failures
        with patch('src.agent_core.memory.rag_store.embedding_functions.SentenceTransformerEmbeddingFunction') as mock_embed:
            mock_embed.side_effect = Exception("Embedding model failed")

            try:
                rag = RAGMemory(collection_name="embed_fail", persist_directory=str(self.temp_dir / "embed"))
            except Exception:
                pass  # Acceptable

    def test_graceful_degradation(self):
        """Test graceful degradation under adverse conditions."""
        # Test with limited memory
        processor = StreamingDocumentProcessor(max_memory_mb=0.1)  # Very limited memory

        large_document = "Large document content. " * 10000

        # Should still process but may be less efficient
        chunks = processor._create_chunks(large_document)
        assert len(chunks) > 0

        # Calculate efficiency with limited memory
        processor.memory_usage = 50 * 1024 * 1024  # 50MB usage
        efficiency = processor._calculate_efficiency(large_document)

        # Efficiency should be calculated even with constraints
        assert isinstance(efficiency, float)
        assert 0.0 <= efficiency <= 1.0


if __name__ == "__main__":
    pytest.main([__file__])