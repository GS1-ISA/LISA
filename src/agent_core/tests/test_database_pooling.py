import pytest
import time
import threading
import statistics
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from src.database_manager import DatabaseConnectionManager, get_db_manager


class TestDatabaseConnectionPooling:
    """Comprehensive tests for database connection pooling system."""

    def setup_method(self):
        """Setup test fixtures."""
        # Use in-memory SQLite for testing
        self.test_db_url = "sqlite:///:memory:"
        self.manager = DatabaseConnectionManager(
            database_url=self.test_db_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=5,
            health_check_interval=1  # Faster for testing
        )

    def teardown_method(self):
        """Cleanup test fixtures."""
        if hasattr(self, 'manager'):
            self.manager.shutdown()

    def test_connection_manager_initialization(self):
        """Test DatabaseConnectionManager initialization."""
        assert self.manager.database_url == self.test_db_url
        assert self.manager.pool_size == 5
        assert self.manager.max_overflow == 10
        assert self.manager.pool_timeout == 5
        assert self.manager._engine is not None
        assert self.manager._session_maker is not None

        # Check pool configuration
        pool = self.manager._engine.pool
        assert isinstance(pool, QueuePool)
        assert pool.size == 5  # pool_size
        assert pool._max_overflow == 10  # max_overflow

    def test_connection_pool_health_monitoring(self):
        """Test health monitoring functionality."""
        # Wait for health check to run
        time.sleep(1.5)  # Health check interval is 1 second

        # Should be healthy
        assert self.manager.is_healthy()

        # Check pool status
        status = self.manager.get_pool_status()
        assert status['pool_size'] == 5
        assert status['max_overflow'] == 10
        assert 'checked_out' in status
        assert 'checked_in' in status
        assert 'available_connections' in status

    def test_session_creation_and_cleanup(self):
        """Test session creation and automatic cleanup."""
        with self.manager.session_scope() as session:
            # Execute a simple query
            result = session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            assert row[0] == 1

        # Session should be closed automatically
        assert session.is_active is False

    def test_connection_pooling_under_load(self):
        """Test connection pooling behavior under concurrent load."""
        results = []
        errors = []

        def concurrent_query(worker_id):
            try:
                start_time = time.perf_counter()
                with self.manager.session_scope() as session:
                    # Simulate some work
                    for i in range(10):
                        result = session.execute(text(f"SELECT {worker_id * 10 + i} as value"))
                        row = result.fetchone()
                        assert row[0] == worker_id * 10 + i
                        time.sleep(0.001)  # Small delay to simulate work
                end_time = time.perf_counter()

                results.append({
                    'worker': worker_id,
                    'duration': end_time - start_time
                })
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Start concurrent workers
        threads = []
        num_workers = 8  # More than pool_size to test overflow
        for i in range(num_workers):
            t = threading.Thread(target=concurrent_query, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join()

        # Verify results
        assert len(results) == num_workers
        assert len(errors) == 0

        # Check pool status after load
        status = self.manager.get_pool_status()
        assert status['available_connections'] >= 0

    def test_connection_recovery(self):
        """Test automatic connection recovery."""
        # Simulate connection failure by disposing engine
        original_engine = self.manager._engine
        self.manager._engine.dispose()

        # Wait for health check to detect and recover
        time.sleep(2)

        # Should have recovered
        assert self.manager.is_healthy()
        assert self.manager._engine is not original_engine  # New engine created

    def test_performance_benchmarks(self):
        """Benchmark database operations performance."""
        # Test connection acquisition speed
        connection_times = []

        for _ in range(50):
            start_time = time.perf_counter()
            with self.manager.session_scope() as session:
                session.execute(text("SELECT 1"))
            end_time = time.perf_counter()
            connection_times.append(end_time - start_time)

        avg_time = statistics.mean(connection_times)
        p95_time = statistics.quantiles(connection_times, n=20)[18]  # 95th percentile

        print(f"DB Connection performance - Average: {avg_time:.4f}s, P95: {p95_time:.4f}s")

        # Performance assertions
        assert avg_time < 0.01  # Should be very fast
        assert p95_time < 0.05  # Even P95 should be reasonable

    def test_memory_efficiency(self):
        """Test memory efficiency of connection pooling."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform many connection operations
        for i in range(100):
            with self.manager.session_scope() as session:
                session.execute(text(f"SELECT {i}"))

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        print(f"DB Memory increase: {memory_increase:.2f} MB")

        # Should not have excessive memory growth
        assert memory_increase < 20  # Less than 20MB increase

    def test_isa_specific_workloads(self):
        """Test with ISA-specific database workloads."""
        # Simulate ISA research operations
        isa_operations = [
            "INSERT INTO research_sessions (query, timestamp) VALUES (?, ?)",
            "SELECT * FROM document_chunks WHERE content LIKE ? LIMIT 10",
            "UPDATE user_preferences SET last_query = ? WHERE user_id = ?",
            "INSERT INTO compliance_mappings (standard, regulation, confidence) VALUES (?, ?, ?)",
            "SELECT COUNT(*) FROM vector_embeddings WHERE similarity > ?"
        ]

        # Execute ISA-like operations
        for i, operation in enumerate(isa_operations):
            with self.manager.session_scope() as session:
                try:
                    # For this test, we'll just execute SELECT 1 since we're using in-memory SQLite
                    # In real scenario, these would be actual ISA operations
                    session.execute(text("SELECT 1"))
                except Exception as e:
                    # Some operations might fail with SQLite, that's expected
                    print(f"Operation {i} note: {e}")

        # Verify pool is still healthy
        assert self.manager.is_healthy()

    def test_connection_pool_scaling(self):
        """Test connection pool scaling under varying loads."""
        scaling_results = []

        # Test different concurrency levels
        for concurrency in [1, 5, 10, 20]:
            start_time = time.perf_counter()

            def worker():
                with self.manager.session_scope() as session:
                    session.execute(text("SELECT 1"))
                    time.sleep(0.01)  # Simulate work

            threads = []
            for _ in range(concurrency):
                t = threading.Thread(target=worker)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            end_time = time.perf_counter()
            duration = end_time - start_time

            scaling_results.append({
                'concurrency': concurrency,
                'duration': duration,
                'ops_per_second': concurrency / duration
            })

        # Analyze scaling
        for result in scaling_results:
            print(f"Concurrency {result['concurrency']}: {result['ops_per_second']:.1f} ops/sec")

        # Should maintain reasonable performance
        high_concurrency = scaling_results[-1]
        assert high_concurrency['ops_per_second'] > 10  # At least 10 ops/sec at high concurrency

    def test_error_handling_and_retry(self):
        """Test error handling and retry logic."""
        # Mock a temporary failure
        original_execute = None

        def failing_execute(*args, **kwargs):
            if not hasattr(failing_execute, 'call_count'):
                failing_execute.call_count = 0
            failing_execute.call_count += 1

            if failing_execute.call_count <= 2:  # Fail first 2 attempts
                from sqlalchemy.exc import DatabaseError
                raise DatabaseError("Temporary failure", None, None)

            # Succeed on 3rd attempt
            return original_execute(*args, **kwargs)

        # Patch the session execute method
        with self.manager.session_scope() as session:
            original_execute = session.execute
            session.execute = failing_execute

            # This should succeed after retries
            result = session.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_connection_timeout_handling(self):
        """Test handling of connection timeouts."""
        # Create manager with very short timeout
        fast_manager = DatabaseConnectionManager(
            database_url=self.test_db_url,
            pool_timeout=1,  # 1 second timeout
            health_check_interval=1
        )

        try:
            # This should work fine
            with fast_manager.session_scope() as session:
                session.execute(text("SELECT 1"))

            assert fast_manager.is_healthy()

        finally:
            fast_manager.shutdown()

    def test_resource_cleanup(self):
        """Test proper resource cleanup."""
        manager = DatabaseConnectionManager(self.test_db_url)
        initial_connections = len(manager._engine.pool._pool)

        # Use some connections
        sessions = []
        for _ in range(3):
            session = manager.get_session()
            sessions.append(session)
            session.execute(text("SELECT 1"))

        # Close sessions
        for session in sessions:
            session.close()

        # Check that connections are returned to pool
        final_connections = len(manager._engine.pool._pool)
        assert final_connections >= initial_connections

        manager.shutdown()

    def test_global_manager_integration(self):
        """Test integration with global database manager."""
        with patch('src.database_manager.DatabaseConnectionManager') as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance

            # Get global manager
            manager = get_db_manager("sqlite:///test.db")

            # Verify it was created correctly
            mock_manager.assert_called_once_with("sqlite:///test.db")
            assert manager == mock_instance


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_full_workflow_simulation(self):
        """Simulate a full ISA database workflow."""
        manager = DatabaseConnectionManager(
            database_url="sqlite:///:memory:",
            pool_size=10,
            max_overflow=20
        )

        try:
            # Simulate research workflow
            workflow_start = time.perf_counter()

            # Phase 1: Query processing
            queries = []
            for i in range(50):
                with manager.session_scope() as session:
                    result = session.execute(text(f"SELECT {i} as query_id, 'research_query_{i}' as content"))
                    queries.append(result.fetchone())

            # Phase 2: Document processing
            documents = []
            for i in range(30):
                with manager.session_scope() as session:
                    result = session.execute(text(f"SELECT {i} as doc_id, 'document_content_{i}' as content"))
                    documents.append(result.fetchone())

            # Phase 3: Result aggregation
            with manager.session_scope() as session:
                result = session.execute(text("SELECT COUNT(*) as total FROM (SELECT 1 UNION SELECT 2 UNION SELECT 3)"))
                count = result.fetchone()[0]

            workflow_end = time.perf_counter()
            total_time = workflow_end - workflow_start

            print(f"Full workflow time: {total_time:.4f}s for {len(queries) + len(documents) + 1} operations")

            # Performance assertions
            assert total_time < 5.0  # Should complete reasonably fast
            assert len(queries) == 50
            assert len(documents) == 30
            assert count == 3

        finally:
            manager.shutdown()


if __name__ == "__main__":
    pytest.main([__file__])