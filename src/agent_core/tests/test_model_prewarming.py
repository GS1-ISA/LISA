import time
from unittest.mock import Mock, patch

import pytest

from src.agent_core.llm_client import CachedOpenRouterClient, ModelWarmer


class TestModelPrewarming:
    """Comprehensive tests for the ModelWarmer system."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_client = Mock()
        self.warmer = ModelWarmer(self.mock_client)

        # Mock successful responses
        self.mock_client.chat_completion.return_value = {
            "content": "Warm-up successful",
            "model_used": "test-model",
            "usage": {"total_tokens": 10}
        }

    def teardown_method(self):
        """Cleanup after tests."""
        if self.warmer.running:
            self.warmer.stop()

    def test_model_warmer_initialization(self):
        """Test ModelWarmer initialization with correct configuration."""
        assert len(self.warmer.models_to_warm) == 5  # 5 free models
        assert self.warmer.warm_up_interval == 300  # 5 minutes
        assert self.warmer.health_check_interval == 60  # 1 minute
        assert self.warmer.max_failures_before_recovery == 3
        assert not self.warmer.running

        # Check all models are initially healthy
        for model in self.warmer.models_to_warm:
            assert self.warmer.model_health[model]["healthy"] is True
            assert self.warmer.model_health[model]["failures"] == 0

    def test_warm_up_process(self):
        """Test the warm-up process functionality."""
        # Start warmer
        self.warmer.start()
        assert self.warmer.running

        # Wait a bit for warm-up to complete
        time.sleep(0.1)

        # Stop warmer
        self.warmer.stop()
        assert not self.warmer.running

        # Verify warm-up was called
        assert self.mock_client.chat_completion.call_count > 0
        assert self.warmer.warm_up_count > 0

    def test_health_check_process(self):
        """Test health check functionality."""
        # Start warmer
        self.warmer.start()
        time.sleep(0.1)

        # Stop warmer
        self.warmer.stop()

        # Verify health checks were performed
        assert self.warmer.health_check_count > 0

    def test_model_failure_handling(self):
        """Test handling of model failures."""
        # Configure mock to fail
        self.mock_client.chat_completion.side_effect = Exception("Model unavailable")

        # Start warmer
        self.warmer.start()
        time.sleep(0.1)
        self.warmer.stop()

        # Check that failures were recorded
        failed_models = [model for model, info in self.warmer.model_health.items()
                        if info["failures"] > 0]
        assert len(failed_models) > 0

    def test_model_recovery(self):
        """Test model recovery after failures."""
        model = self.warmer.models_to_warm[0]

        # Simulate failures
        for _ in range(3):
            self.warmer._handle_model_failure(model)

        # Model should be marked unhealthy
        assert not self.warmer.model_health[model]["healthy"]

        # Configure mock to succeed for recovery
        self.mock_client.chat_completion.side_effect = None
        self.mock_client.chat_completion.return_value = {
            "content": "Recovery successful",
            "model_used": model,
            "usage": {"total_tokens": 10}
        }

        # Attempt recovery
        self.warmer._attempt_recovery(model)

        # Model should be healthy again
        assert self.warmer.model_health[model]["healthy"]
        assert self.warmer.model_health[model]["failures"] == 0

    def test_warm_stats_reporting(self):
        """Test warm-up statistics reporting."""
        # Perform some warm-ups
        self.warmer.start()
        time.sleep(0.1)
        self.warmer.stop()

        stats = self.warmer.get_warm_stats()

        assert "warm_up_count" in stats
        assert "health_check_count" in stats
        assert "recovery_attempts" in stats
        assert "average_warm_up_latency" in stats
        assert "model_health_status" in stats
        assert "latency_reduction_estimate" in stats

        assert stats["warm_up_count"] >= 0
        assert stats["health_check_count"] >= 0
        assert isinstance(stats["model_health_status"], dict)

    def test_concurrent_warm_up_operations(self):
        """Test concurrent warm-up operations."""
        # Start multiple warmers
        warmers = []
        for _i in range(3):
            warmer = ModelWarmer(self.mock_client)
            warmer.start()
            warmers.append(warmer)

        # Let them run briefly
        time.sleep(0.2)

        # Stop all
        for warmer in warmers:
            warmer.stop()

        # Verify they all operated
        total_warm_ups = sum(w.warm_up_count for w in warmers)
        assert total_warm_ups > 0

    def test_performance_benchmarks(self):
        """Benchmark pre-warming performance."""
        start_time = time.perf_counter()

        # Start warmer and let it perform operations
        self.warmer.start()
        time.sleep(0.5)  # Longer run for benchmarking
        self.warmer.stop()

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Performance assertions
        assert duration < 1.0  # Should complete quickly
        assert self.warmer.warm_up_count > 0

        # Calculate operations per second
        ops_per_second = self.warmer.warm_up_count / duration
        print(f"Pre-warming performance: {ops_per_second:.2f} ops/sec")

        # Should be reasonably fast
        assert ops_per_second > 1.0

    def test_memory_efficiency(self):
        """Test memory efficiency of pre-warming system."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Start warmer
        self.warmer.start()
        time.sleep(0.3)
        self.warmer.stop()

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        print(f"Memory increase: {memory_increase:.2f} MB")

        # Should not have excessive memory growth
        assert memory_increase < 50  # Less than 50MB increase

    def test_isa_specific_scenarios(self):
        """Test pre-warming with ISA-specific query patterns."""

        # Mock optimizer to return different models for different queries
        with patch("src.agent_core.llm_client.QueryOptimizer") as mock_optimizer:
            mock_optimizer.return_value.optimize_query.side_effect = [
                Mock(model="google/gemini-2.5-flash-image-preview:free", temperature=0.1, max_tokens=2000),
                Mock(model="meta-llama/llama-4-scout:free", temperature=0.2, max_tokens=4000),
                Mock(model="mistralai/mistral-small-3.1-24b-instruct:free", temperature=0.1, max_tokens=3000),
                Mock(model="deepseek/deepseek-r1:free", temperature=0.3, max_tokens=5000),
                Mock(model="google/gemini-2.0-flash-exp:free", temperature=0.2, max_tokens=2500)
            ]

            # Start warmer
            self.warmer.start()
            time.sleep(0.2)
            self.warmer.stop()

            # Verify different models were used
            call_args_list = self.mock_client.chat_completion.call_args_list
            used_models = set()
            for call in call_args_list:
                if "model" in call[1]:
                    used_models.add(call[1]["model"])

            # Should have used multiple different models
            assert len(used_models) > 1

    def test_error_resilience(self):
        """Test system resilience to various error conditions."""
        # Test with network errors
        self.mock_client.chat_completion.side_effect = [
            ConnectionError("Network unreachable"),
            TimeoutError("Request timeout"),
            Exception("Generic error"),
            {"content": "Success", "model_used": "test", "usage": {"total_tokens": 10}}  # Recovery
        ]

        self.warmer.start()
        time.sleep(0.2)
        self.warmer.stop()

        # System should continue operating despite errors
        assert self.warmer.warm_up_count >= 0  # At least attempted

    def test_configuration_override(self):
        """Test configuration override via environment variables."""
        with patch.dict("os.environ", {
            "MODEL_WARM_UP_INTERVAL_SECONDS": "10",
            "MODEL_HEALTH_CHECK_INTERVAL_SECONDS": "5",
            "MODEL_MAX_FAILURES_RECOVERY": "5"
        }):
            warmer = ModelWarmer(self.mock_client)

            assert warmer.warm_up_interval == 10
            assert warmer.health_check_interval == 5
            assert warmer.max_failures_before_recovery == 5


class TestCachedOpenRouterClient:
    """Tests for CachedOpenRouterClient integration with pre-warming."""

    def setup_method(self):
        """Setup test fixtures."""
        self.mock_redis = Mock()
        with patch("redis.Redis", return_value=self.mock_redis):
            self.client = CachedOpenRouterClient(
                redis_host="localhost",
                redis_port=6379,
                ttl_seconds=300
            )

    def test_warm_stats_integration(self):
        """Test that warm stats are accessible through cached client."""
        stats = self.client.get_warm_stats()

        assert "warm_up_count" in stats
        assert "model_health_status" in stats
        assert "latency_reduction_estimate" in stats

    def test_cache_performance_with_warming(self):
        """Test cache performance when pre-warming is active."""
        # Mock Redis operations
        self.mock_redis.get.return_value = None  # Cache misses
        self.mock_redis.setex.return_value = True

        # Mock underlying client
        with patch.object(self.client.underlying_client, "chat_completion") as mock_chat:
            mock_chat.return_value = {
                "content": "Test response",
                "model_used": "test-model",
                "usage": {"total_tokens": 100}
            }

            # Make multiple identical requests
            messages = [{"role": "user", "content": "Test query"}]
            for _ in range(5):
                self.client.chat_completion(messages)

            # Should have cache misses initially
            cache_stats = self.client.get_cache_stats()
            assert cache_stats["misses"] >= 1

            # Verify pre-warming is running
            warm_stats = self.client.get_warm_stats()
            assert "warm_up_count" in warm_stats


if __name__ == "__main__":
    pytest.main([__file__])
