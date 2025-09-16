import pytest
import time
import statistics
import threading
from pathlib import Path
from unittest.mock import Mock, patch
from src.agent_core.query_optimizer import QueryOptimizer
from src.agent_core.streaming_processor import StreamingDocumentProcessor
from src.agent_core.memory.rag_store import RAGMemory


class TestPerformanceBenchmarks:

    def setup_method(self):
        """Setup benchmark test fixtures."""
        self.temp_dir = Path("benchmark_temp_dir")
        self.temp_dir.mkdir(exist_ok=True)

        # Initialize components
        self.optimizer = QueryOptimizer()
        self.rag_memory = RAGMemory(
            collection_name="benchmark_test",
            persist_directory=str(self.temp_dir)
        )

        # Mock LLM client for streaming processor
        self.mock_client = Mock()
        self.streaming_processor = StreamingDocumentProcessor()
        self.streaming_processor.llm_client = self.mock_client

    def teardown_method(self):
        """Cleanup benchmark fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_query_optimizer_performance(self):
        """Benchmark QueryOptimizer performance."""
        test_queries = [
            "What are CSRD compliance requirements?",
            "Map GDSN attributes to XBRL taxonomy for ESG reporting",
            "Analyze regulatory documents for sustainability disclosures",
            "How do ontology schemas work in standards mapping?",
            "Extract compliance information from this PDF document",
            "Compare EU CSRD with US SEC climate disclosure rules",
            "Integrate GDSN product data with regulatory reporting systems",
            "Validate ESG disclosure requirements across jurisdictions"
        ]

        # Benchmark optimization performance
        times = []
        for query in test_queries:
            start_time = time.perf_counter()
            result = self.optimizer.optimize_query(query)
            end_time = time.perf_counter()

            duration = end_time - start_time
            times.append(duration)

            # Verify result quality
            assert result.model in self.optimizer.model_configs
            assert 0.0 <= result.temperature <= 0.5
            assert result.max_tokens > 0

        # Performance assertions
        avg_time = statistics.mean(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile

        print(f"QueryOptimizer - Average: {avg_time:.4f}s, P95: {p95_time:.4f}s")

        # Should be fast (< 10ms per optimization)
        assert avg_time < 0.01
        assert p95_time < 0.02

    def test_streaming_processor_performance(self):
        """Benchmark StreamingDocumentProcessor performance."""
        # Create test documents of various sizes
        small_doc = "This is a small regulatory document. " * 50
        medium_doc = "This is a medium regulatory document about CSRD compliance. " * 500
        large_doc = "This is a large regulatory document with extensive ESG requirements. " * 2000

        documents = [
            ("small", small_doc),
            ("medium", medium_doc),
            ("large", large_doc)
        ]

        # Mock LLM responses
        self.mock_client.chat_completion.return_value = {
            'content': 'Processed content analysis',
            'model_used': 'test-model',
            'usage': {'total_tokens': 100}
        }

        results = {}
        for size_name, document in documents:
            # Benchmark processing
            start_time = time.perf_counter()
            result = self.streaming_processor.process_document(
                document, "Analyze regulatory requirements"
            )
            end_time = time.perf_counter()

            duration = end_time - start_time
            results[size_name] = {
                'duration': duration,
                'chunks': result['metadata']['total_chunks'],
                'chars': len(document)
            }

            print(f"StreamingProcessor {size_name} - {duration:.4f}s, {result['metadata']['total_chunks']} chunks")

        # Performance assertions
        # Small document should be fast
        assert results['small']['duration'] < 0.1
        # Large document should still be reasonable
        assert results['large']['duration'] < 5.0
        # Processing should scale roughly linearly
        small_to_medium_ratio = results['medium']['duration'] / results['small']['duration']
        assert small_to_medium_ratio < 20  # Should not be excessively slower

    def test_rag_memory_performance(self):
        """Benchmark RAGMemory performance."""
        # Setup test data
        documents = []
        for i in range(100):
            content = f"Regulatory document {i} about CSRD compliance and ESG reporting requirements. " * 20
            documents.append({
                'text': content,
                'source': f'regulatory_{i % 5}',  # 5 different sources
                'doc_id': f'doc_{i}'
            })

        # Benchmark batch add
        start_time = time.perf_counter()
        success = self.rag_memory.batch_add(documents)
        add_duration = time.perf_counter() - start_time

        assert success == True
        print(f"RAG batch add (100 docs) - {add_duration:.4f}s")

        # Benchmark queries
        query_times = []
        queries = [
            "CSRD compliance",
            "ESG reporting requirements",
            "regulatory standards",
            "sustainability disclosures",
            "compliance mandates"
        ]

        for query in queries:
            # Warm up cache
            self.rag_memory.query(query, n_results=5)

            # Benchmark cached queries
            start_time = time.perf_counter()
            for _ in range(10):  # Multiple runs for stable measurement
                results = self.rag_memory.query(query, n_results=5)
                assert len(results) > 0
            end_time = time.perf_counter()

            avg_query_time = (end_time - start_time) / 10
            query_times.append(avg_query_time)

        avg_query_time = statistics.mean(query_times)
        p95_query_time = statistics.quantiles(query_times, n=20)[18]

        print(f"RAG queries - Average: {avg_query_time:.4f}s, P95: {p95_query_time:.4f}s")

        # Performance assertions
        assert add_duration < 10.0  # Batch add should be reasonable
        assert avg_query_time < 0.1  # Queries should be fast
        assert p95_query_time < 0.2  # Even P95 should be acceptable

    def test_memory_scaling_benchmark(self):
        """Benchmark memory usage scaling."""
        initial_stats = self.rag_memory.get_stats()

        # Add increasing amounts of data
        scaling_points = []
        for batch_size in [10, 50, 100, 200]:
            documents = []
            for i in range(batch_size):
                content = f"Scaling test document {i} with regulatory content. " * 10
                documents.append({
                    'text': content,
                    'source': 'scaling_test',
                    'doc_id': f'scale_doc_{len(scaling_points)}_{i}'
                })

            start_time = time.perf_counter()
            self.rag_memory.batch_add(documents)
            duration = time.perf_counter() - start_time

            stats = self.rag_memory.get_stats()
            scaling_points.append({
                'batch_size': batch_size,
                'total_chunks': stats['total_chunks'],
                'duration': duration
            })

        # Analyze scaling
        for point in scaling_points:
            chunks_per_second = point['total_chunks'] / point['duration']
            print(f"Batch {point['batch_size']}: {chunks_per_second:.1f} chunks/sec")

        # Should maintain reasonable performance
        final_point = scaling_points[-1]
        assert final_point['duration'] < 15.0  # Even large batches should be reasonable

    def test_concurrent_performance(self):
        """Benchmark concurrent operations."""
        # Setup test data
        for i in range(50):
            self.rag_memory.add(
                f"Concurrent test document {i}",
                "concurrent_source",
                f"concurrent_doc_{i}"
            )

        results = []
        errors = []

        def concurrent_query(worker_id):
            try:
                start_time = time.perf_counter()
                for i in range(20):  # Each worker does 20 queries
                    results_list = self.rag_memory.query(f"concurrent query {worker_id}_{i}", n_results=3)
                    assert len(results_list) > 0
                end_time = time.perf_counter()

                duration = end_time - start_time
                results.append({
                    'worker': worker_id,
                    'duration': duration,
                    'queries_per_second': 20 / duration
                })
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Start concurrent workers
        threads = []
        num_workers = 5
        for i in range(num_workers):
            t = threading.Thread(target=concurrent_query, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Analyze results
        assert len(errors) == 0, f"Concurrent errors: {errors}"
        assert len(results) == num_workers

        total_qps = sum(r['queries_per_second'] for r in results)
        avg_qps = total_qps / num_workers

        print(f"Concurrent performance - Avg {avg_qps:.1f} queries/sec per worker")

        # Should maintain good performance under concurrency
        assert avg_qps > 10  # At least 10 queries per second per worker

    def test_caching_effectiveness(self):
        """Benchmark caching effectiveness."""
        # Setup test data
        for i in range(20):
            self.rag_memory.add(
                f"Caching test document {i} with regulatory content",
                "cache_source",
                f"cache_doc_{i}"
            )

        query = "regulatory content caching test"

        # Measure uncached performance
        self.rag_memory.clear_cache()  # Ensure clean state

        uncached_times = []
        for _ in range(5):
            start_time = time.perf_counter()
            results = self.rag_memory.query(query, n_results=5)
            end_time = time.perf_counter()
            uncached_times.append(end_time - start_time)

        # Measure cached performance
        cached_times = []
        for _ in range(10):  # More runs for cached
            start_time = time.perf_counter()
            results = self.rag_memory.query(query, n_results=5)
            end_time = time.perf_counter()
            cached_times.append(end_time - start_time)

        uncached_avg = statistics.mean(uncached_times)
        cached_avg = statistics.mean(cached_times)

        improvement_ratio = uncached_avg / cached_avg if cached_avg > 0 else float('inf')

        print(f"Caching effectiveness - Uncached: {uncached_avg:.4f}s, Cached: {cached_avg:.4f}s, Ratio: {improvement_ratio:.1f}x")

        # Caching should provide significant improvement
        assert improvement_ratio > 2.0  # At least 2x improvement

    def test_end_to_end_workflow_performance(self):
        """Benchmark complete ISA workflow performance."""
        # Setup comprehensive test data
        isa_documents = [
            {
                'content': "CSRD Article 8 requires ESG disclosures including climate risks, biodiversity impacts, and social factors. " * 50,
                'source': 'eu_regulatory',
                'doc_id': 'csrd_article_8'
            },
            {
                'content': "GDSN standards provide attribute mappings for product data including regulatory compliance fields. " * 50,
                'source': 'gdsn_standards',
                'doc_id': 'gdsn_mapping'
            },
            {
                'content': "XBRL taxonomy defines structured reporting formats for ESG and financial data integration. " * 50,
                'source': 'xbrl_taxonomy',
                'doc_id': 'xbrl_esg'
            }
        ]

        # Mock streaming responses
        self.mock_client.chat_completion.return_value = {
            'content': 'Comprehensive analysis of regulatory requirements',
            'model_used': 'test-model',
            'usage': {'total_tokens': 200}
        }

        # Measure end-to-end workflow
        workflow_start = time.perf_counter()

        # 1. Optimize queries
        queries = [
            "CSRD compliance requirements analysis",
            "GDSN to XBRL mapping integration",
            "ESG reporting framework assessment"
        ]

        optimizations = []
        for query in queries:
            opt_start = time.perf_counter()
            optimization = self.optimizer.optimize_query(query)
            opt_end = time.perf_counter()
            optimizations.append({
                'query': query,
                'optimization_time': opt_end - opt_start,
                'result': optimization
            })

        # 2. Process documents
        processing_results = []
        for doc in isa_documents:
            proc_start = time.perf_counter()
            result = self.streaming_processor.process_document(
                doc['content'], f"Analyze {doc['source']} content"
            )
            proc_end = time.perf_counter()
            processing_results.append({
                'doc_id': doc['doc_id'],
                'processing_time': proc_end - proc_start,
                'chunks': result['metadata']['total_chunks']
            })

        # 3. Store in RAG memory
        storage_start = time.perf_counter()
        success = self.rag_memory.batch_add(isa_documents)
        storage_end = time.perf_counter()

        # 4. Query and retrieve
        query_results = []
        for query in queries:
            query_start = time.perf_counter()
            results = self.rag_memory.query(query, n_results=5)
            query_end = time.perf_counter()
            query_results.append({
                'query': query,
                'query_time': query_end - query_start,
                'results_count': len(results)
            })

        workflow_end = time.perf_counter()
        total_workflow_time = workflow_end - workflow_start

        # Performance analysis
        print(f"End-to-end workflow performance:")
        print(f"Total time: {total_workflow_time:.4f}s")
        print(f"Query optimization: {sum(o['optimization_time'] for o in optimizations):.4f}s")
        print(f"Document processing: {sum(p['processing_time'] for p in processing_results):.4f}s")
        print(f"Storage: {storage_end - storage_start:.4f}s")
        print(f"Querying: {sum(q['query_time'] for q in query_results):.4f}s")

        # Assertions
        assert total_workflow_time < 20.0  # Complete workflow should be reasonable
        assert success == True
        assert all(q['results_count'] > 0 for q in query_results)

        # Individual component performance
        avg_optimization_time = statistics.mean(o['optimization_time'] for o in optimizations)
        avg_query_time = statistics.mean(q['query_time'] for q in query_results)

        assert avg_optimization_time < 0.01  # Fast optimization
        assert avg_query_time < 0.1  # Fast querying

    def test_memory_efficiency_benchmark(self):
        """Benchmark memory efficiency."""
        # Track memory usage during operations
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform memory-intensive operations
        large_documents = []
        for i in range(100):
            content = f"Memory efficiency test document {i}. " * 200
            large_documents.append({
                'text': content,
                'source': 'memory_test',
                'doc_id': f'memory_doc_{i}'
            })

        # Measure memory during batch add
        self.rag_memory.batch_add(large_documents)
        after_add_memory = process.memory_info().rss / 1024 / 1024

        # Measure memory during queries
        for i in range(50):
            self.rag_memory.query(f"memory test query {i}")

        after_query_memory = process.memory_info().rss / 1024 / 1024

        memory_increase = after_query_memory - initial_memory

        print(f"Memory efficiency - Initial: {initial_memory:.1f}MB, Final: {after_query_memory:.1f}MB, Increase: {memory_increase:.1f}MB")

        # Should not have excessive memory growth
        assert memory_increase < 500  # Less than 500MB increase for this workload


if __name__ == "__main__":
    pytest.main([__file__])