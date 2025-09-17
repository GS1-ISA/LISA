import statistics
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Import all Phase 2 components
from src.agent_core.llm_client import CachedOpenRouterClient
from src.agent_core.streaming_processor import StreamingDocumentProcessor
from src.database_manager import DatabaseConnectionManager
from src.shared.paths import DATABASE_URLS


class TestPhase2Integration:
    """Integration tests for all Phase 2 improvements working together."""

    def setup_method(self):
        """Setup comprehensive test environment."""
        self.temp_dir = Path("integration_test_dir")
        self.temp_dir.mkdir(exist_ok=True)

        # Initialize all components
        self._setup_database()
        self._setup_llm_client()
        self._setup_streaming_processor()

    def teardown_method(self):
        """Cleanup all test resources."""
        # Stop background processes
        if hasattr(self, "warmer") and self.warmer.running:
            self.warmer.stop()

        if hasattr(self, "db_manager"):
            self.db_manager.shutdown()

        # Cleanup temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _setup_database(self):
        """Setup database with connection pooling."""
        self.db_manager = DatabaseConnectionManager(
            database_url=DATABASE_URLS["MEMORY"],
            pool_size=10,
            max_overflow=15,
            health_check_interval=2
        )

    def _setup_llm_client(self):
        """Setup LLM client with pre-warming."""
        with patch("redis.Redis"):
            self.llm_client = CachedOpenRouterClient(
                redis_host="localhost",
                redis_port=6379,
                ttl_seconds=300
            )
            self.warmer = self.llm_client.warmer

    def _setup_streaming_processor(self):
        """Setup streaming processor."""
        self.streaming_processor = StreamingDocumentProcessor(
            chunk_size=2000,  # Smaller for testing
            overlap_size=200,
            llm_client=self.llm_client
        )

    def test_end_to_end_isa_workflow(self):
        """Test complete ISA workflow with all Phase 2 optimizations."""
        # Start pre-warming
        self.warmer.start()

        # ISA-specific test data
        isa_documents = [
            {
                "content": """
                CSRD Article 8 requires comprehensive ESG disclosures including:
                - Climate change mitigation strategies
                - Biodiversity impact assessments
                - Social responsibility metrics
                - Governance structure transparency

                Companies must report on their value chain impacts and implement
                due diligence processes for sustainable business practices.
                """ * 10,
                "metadata": {"source": "eu_regulatory", "type": "csrd"}
            },
            {
                "content": """
                GDSN standards provide structured data exchange for retail products:
                - GTIN identification system
                - Attribute mapping matrices
                - Regulatory compliance flags
                - Supply chain traceability

                Integration with XBRL taxonomy enables automated reporting workflows.
                """ * 10,
                "metadata": {"source": "gs1_standards", "type": "gdsn"}
            },
            {
                "content": """
                XBRL taxonomy framework for ESG reporting:
                - Structured data tags for environmental metrics
                - Social impact disclosures
                - Governance indicators
                - Assurance and verification requirements

                Automated validation against regulatory templates ensures compliance.
                """ * 10,
                "metadata": {"source": "xbrl_taxonomy", "type": "esg_reporting"}
            }
        ]

        workflow_start = time.perf_counter()

        # Phase 1: Store documents in database with connection pooling
        stored_docs = []
        for i, doc in enumerate(isa_documents):
            with self.db_manager.session_scope():
                # Simulate storing document metadata
                doc_id = f"doc_{i}"
                stored_docs.append({
                    "id": doc_id,
                    "content": doc["content"],
                    "metadata": doc["metadata"]
                })

        # Phase 2: Process documents with streaming processor (uses pre-warmed models)
        processing_results = []
        for doc in stored_docs:
            result = self.streaming_processor.process_document(
                doc["content"],
                f"Analyze {doc['metadata']['type']} content for compliance requirements"
            )
            processing_results.append({
                "doc_id": doc["id"],
                "result": result,
                "chunks": result["metadata"]["total_chunks"]
            })

        # Phase 3: Query and retrieve with optimized models
        research_queries = [
            "CSRD compliance requirements analysis",
            "GDSN to XBRL mapping integration",
            "ESG reporting framework assessment"
        ]

        query_results = []
        for query in research_queries:
            # Simulate LLM query (would use pre-warmed models)
            messages = [{"role": "user", "content": query}]

            # Mock the response for testing
            with patch.object(self.llm_client.underlying_client, "chat_completion") as mock_chat:
                mock_chat.return_value = {
                    "content": f"Analysis result for: {query}",
                    "model_used": "test-model",
                    "usage": {"total_tokens": 150}
                }

                result = self.llm_client.chat_completion(messages)
                query_results.append({
                    "query": query,
                    "result": result,
                    "cached": "hits" in self.llm_client.get_cache_stats()
                })

        workflow_end = time.perf_counter()
        total_workflow_time = workflow_end - workflow_start

        # Performance assertions
        print(f"End-to-end ISA workflow: {total_workflow_time:.4f}s")
        assert total_workflow_time < 15.0  # Should complete within reasonable time

        # Verify all components worked
        assert len(stored_docs) == 3
        assert len(processing_results) == 3
        assert len(query_results) == 3

        # Check streaming processing results
        for result in processing_results:
            assert result["chunks"] > 0
            assert "content" in result["result"]

        # Check query results
        for result in query_results:
            assert "content" in result["result"]
            assert result["result"]["model_used"] == "test-model"

    def test_concurrent_workload_simulation(self):
        """Test concurrent ISA workloads across all Phase 2 systems."""
        # Start pre-warming
        self.warmer.start()
        time.sleep(0.1)  # Let warmer initialize

        results = []
        errors = []

        def concurrent_isa_worker(worker_id):
            try:
                worker_start = time.perf_counter()

                # Simulate database operations
                with self.db_manager.session_scope():
                    # Simulate ISA research operations
                    for _i in range(5):
                        # In real scenario, this would be actual ISA operations
                        pass  # Simplified for testing

                # Simulate document processing
                test_content = f"ISA document content for worker {worker_id}. " * 50
                result = self.streaming_processor.process_document(
                    test_content,
                    f"Process ISA content worker {worker_id}"
                )

                # Simulate LLM queries
                messages = [{"role": "user", "content": f"ISA query {worker_id}"}]
                with patch.object(self.llm_client.underlying_client, "chat_completion") as mock_chat:
                    mock_chat.return_value = {
                        "content": f"Response {worker_id}",
                        "model_used": "test-model",
                        "usage": {"total_tokens": 50}
                    }
                    self.llm_client.chat_completion(messages)

                worker_end = time.perf_counter()

                results.append({
                    "worker": worker_id,
                    "duration": worker_end - worker_start,
                    "chunks_processed": result["metadata"]["total_chunks"],
                    "llm_calls": 1
                })

            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Start concurrent workers
        threads = []
        num_workers = 8
        for i in range(num_workers):
            t = threading.Thread(target=concurrent_isa_worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Analyze results
        assert len(results) == num_workers
        assert len(errors) == 0

        total_time = sum(r["duration"] for r in results)
        avg_time = total_time / num_workers
        total_chunks = sum(r["chunks_processed"] for r in results)

        print(f"Concurrent workload - Avg time: {avg_time:.4f}s, Total chunks: {total_chunks}")

        # Performance assertions
        assert avg_time < 5.0  # Should be reasonably fast
        assert total_chunks > 0

        # Check system health
        assert self.db_manager.is_healthy()
        warm_stats = self.warmer.get_warm_stats()
        assert warm_stats["warm_up_count"] >= 0

    def test_performance_benchmarks_integration(self):
        """Comprehensive performance benchmarks across all systems."""
        # Start all systems
        self.warmer.start()
        time.sleep(0.2)

        benchmark_results = {}

        # 1. Database connection pooling benchmark
        db_times = []
        for _ in range(100):
            start = time.perf_counter()
            with self.db_manager.session_scope() as session:
                session.execute("SELECT 1")
            end = time.perf_counter()
            db_times.append(end - start)

        benchmark_results["database"] = {
            "avg_time": statistics.mean(db_times),
            "p95_time": statistics.quantiles(db_times, n=20)[18],
            "total_operations": len(db_times)
        }

        # 2. LLM pre-warming and caching benchmark
        llm_times = []
        cache_hits_before = self.llm_client.get_cache_stats()["hits"]

        for i in range(50):
            messages = [{"role": "user", "content": f"ISA benchmark query {i}"}]
            start = time.perf_counter()

            with patch.object(self.llm_client.underlying_client, "chat_completion") as mock_chat:
                mock_chat.return_value = {
                    "content": f"Response {i}",
                    "model_used": "test-model",
                    "usage": {"total_tokens": 100}
                }
                self.llm_client.chat_completion(messages)

            end = time.perf_counter()
            llm_times.append(end - start)

        cache_hits_after = self.llm_client.get_cache_stats()["hits"]

        benchmark_results["llm"] = {
            "avg_time": statistics.mean(llm_times),
            "p95_time": statistics.quantiles(llm_times, n=20)[18],
            "cache_hits": cache_hits_after - cache_hits_before,
            "total_operations": len(llm_times)
        }

        # 3. Streaming processor benchmark
        processor_times = []
        test_documents = [
            "ISA regulatory content. " * 100,
            "Compliance requirements document. " * 150,
            "Standards mapping guide. " * 200
        ]

        for doc in test_documents:
            start = time.perf_counter()
            self.streaming_processor.process_document(
                doc, "Analyze regulatory content"
            )
            end = time.perf_counter()
            processor_times.append(end - start)

        benchmark_results["streaming"] = {
            "avg_time": statistics.mean(processor_times),
            "total_chunks": sum(result["metadata"]["total_chunks"] for result in
                              [self.streaming_processor.process_document(doc, "test")
                               for doc in test_documents[:1]]),  # Just one for stats
            "total_operations": len(test_documents)
        }

        # Print comprehensive benchmark results
        print("\n=== Phase 2 Integration Benchmarks ===")
        for component, metrics in benchmark_results.items():
            print(f"{component.upper()}:")
            print(".4f")
            print(".4f")
            if "cache_hits" in metrics:
                print(f"  Cache hits: {metrics['cache_hits']}")
            if "total_chunks" in metrics:
                print(f"  Total chunks: {metrics['total_chunks']}")
            print(f"  Operations: {metrics['total_operations']}")

        # Overall performance assertions
        assert benchmark_results["database"]["avg_time"] < 0.01  # Fast DB access
        assert benchmark_results["llm"]["avg_time"] < 0.5  # Reasonable LLM response time
        assert benchmark_results["streaming"]["avg_time"] < 3.0  # Reasonable processing time

    def test_memory_efficiency_integration(self):
        """Test memory efficiency across all Phase 2 systems."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Start all systems
        self.warmer.start()

        # Perform memory-intensive operations
        large_documents = []
        for i in range(20):
            content = f"ISA compliance document {i}. " * 300  # Large documents
            large_documents.append(content)

            # Process through streaming processor
            self.streaming_processor.process_document(
                content, f"Analyze document {i}"
            )

            # Store in database
            with self.db_manager.session_scope():
                # Simulate storage operations
                pass

        # Make many LLM calls
        for i in range(100):
            messages = [{"role": "user", "content": f"Query {i}"}]
            with patch.object(self.llm_client.underlying_client, "chat_completion") as mock_chat:
                mock_chat.return_value = {
                    "content": f"Response {i}",
                    "model_used": "test-model",
                    "usage": {"total_tokens": 50}
                }
                self.llm_client.chat_completion(messages)

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        print(f"Integration memory increase: {memory_increase:.2f} MB")

        # Should not have excessive memory growth
        assert memory_increase < 200  # Less than 200MB increase for this workload

        # Stop warmer
        self.warmer.stop()

    def test_error_resilience_integration(self):
        """Test error resilience across integrated systems."""
        # Test database connection failure recovery
        original_engine = self.db_manager._engine
        self.db_manager._engine.dispose()

        # Wait for health check to recover
        time.sleep(3)

        # Should have recovered
        assert self.db_manager.is_healthy()
        assert self.db_manager._engine is not original_engine

        # Test LLM model failure and recovery
        with patch.object(self.llm_client.underlying_client, "chat_completion") as mock_chat:
            # Simulate failures followed by recovery
            mock_chat.side_effect = [
                Exception("Model temporarily unavailable"),
                Exception("Rate limit exceeded"),
                {
                    "content": "Recovered response",
                    "model_used": "backup-model",
                    "usage": {"total_tokens": 100}
                }
            ]

            messages = [{"role": "user", "content": "Test resilience"}]

            # Should eventually succeed
            result = self.llm_client.chat_completion(messages)
            assert result["content"] == "Recovered response"
            assert result["model_used"] == "backup-model"

    def test_isa_compliance_scenarios(self):
        """Test ISA-specific compliance and regulatory scenarios."""
        compliance_scenarios = [
            {
                "query": "CSRD Article 8 reporting requirements",
                "documents": [
                    "EU sustainability reporting standards",
                    "Climate disclosure mandates",
                    "Value chain due diligence"
                ]
            },
            {
                "query": "GDSN attribute mapping for ESG data",
                "documents": [
                    "GS1 standards integration",
                    "Product data synchronization",
                    "Regulatory compliance flags"
                ]
            },
            {
                "query": "XBRL taxonomy for ESG disclosures",
                "documents": [
                    "Financial reporting frameworks",
                    "ESG data tagging standards",
                    "Automated validation rules"
                ]
            }
        ]

        for scenario in compliance_scenarios:
            # Process query with pre-warmed models
            messages = [{"role": "user", "content": scenario["query"]}]

            with patch.object(self.llm_client.underlying_client, "chat_completion") as mock_chat:
                mock_chat.return_value = {
                    "content": f'Compliance analysis: {scenario["query"]}',
                    "model_used": "compliance-model",
                    "usage": {"total_tokens": 200}
                }

                result = self.llm_client.chat_completion(messages)
                assert "compliance analysis" in result["content"].lower()

            # Process related documents
            for doc_title in scenario["documents"]:
                doc_content = f"{doc_title} content. " * 100

                # Store in database
                with self.db_manager.session_scope():
                    # Simulate document storage
                    pass

                # Process with streaming
                stream_result = self.streaming_processor.process_document(
                    doc_content,
                    f"Extract compliance information from {doc_title}"
                )

                assert stream_result["metadata"]["total_chunks"] > 0
                assert len(stream_result["content"]) > 0

    def test_scalability_under_load(self):
        """Test scalability of integrated Phase 2 systems under load."""
        # Start all systems
        self.warmer.start()
        time.sleep(0.1)

        load_test_results = []

        # Test different load levels
        for load_level in [10, 25, 50, 100]:
            load_start = time.perf_counter()

            # Simulate concurrent operations
            def load_worker(worker_id):
                # Database operations
                with self.db_manager.session_scope():
                    pass  # Simplified

                # LLM operations
                messages = [{"role": "user", "content": f"Load test query {worker_id}"}]
                with patch.object(self.llm_client.underlying_client, "chat_completion") as mock_chat:
                    mock_chat.return_value = {
                        "content": f"Response {worker_id}",
                        "model_used": "test-model",
                        "usage": {"total_tokens": 50}
                    }
                    self.llm_client.chat_completion(messages)

                # Streaming operations
                content = f"Load test document {worker_id}. " * 20
                self.streaming_processor.process_document(content, "Process load test")

            threads = []
            for i in range(load_level):
                t = threading.Thread(target=load_worker, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            load_end = time.perf_counter()
            duration = load_end - load_start

            load_test_results.append({
                "load_level": load_level,
                "duration": duration,
                "ops_per_second": load_level / duration
            })

        # Analyze scalability
        for result in load_test_results:
            print(f"Load {result['load_level']}: {result['ops_per_second']:.1f} ops/sec")

        # Should maintain reasonable performance
        high_load = load_test_results[-1]
        assert high_load["ops_per_second"] > 5  # At least 5 operations per second under high load

        # Stop systems
        self.warmer.stop()


if __name__ == "__main__":
    pytest.main([__file__])
