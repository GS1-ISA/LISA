import json
from unittest.mock import Mock, patch

import pytest

from src.agent_core.llm_client import CachedOpenRouterClient


class TestCachedOpenRouterClient:

    def setup_method(self):
        """Setup test fixtures."""
        self.redis_mock = Mock()
        self.client = CachedOpenRouterClient(
            redis_host="localhost",
            redis_port=6379,
            redis_db=0,
            ttl_seconds=3600
        )
        self.client.redis_client = self.redis_mock

    def test_cache_key_generation(self):
        """Test cache key generation for different inputs."""
        messages = [{"role": "user", "content": "Test message"}]
        model = "test-model"
        temperature = 0.5
        max_tokens = 100

        key1 = self.client._generate_cache_key(messages, model, temperature, max_tokens)
        key2 = self.client._generate_cache_key(messages, model, temperature, max_tokens)

        # Same inputs should generate same key
        assert key1 == key2

        # Different inputs should generate different keys
        key3 = self.client._generate_cache_key(
            [{"role": "user", "content": "Different message"}],
            model, temperature, max_tokens
        )
        assert key1 != key3

    def test_cache_hit(self):
        """Test cache hit scenario."""
        messages = [{"role": "user", "content": "Test query"}]
        cached_response = {
            "content": "Cached response",
            "model": "test-model",
            "usage": {"total_tokens": 50}
        }

        # Mock Redis get to return cached data
        self.redis_mock.get.return_value = json.dumps(cached_response)

        result = self.client.chat_completion(messages)

        # Should return cached response
        assert result == cached_response
        assert self.client.cache_hits == 1
        assert self.client.cache_misses == 0

        # Should call Redis get
        self.redis_mock.get.assert_called_once()

    def test_cache_miss(self):
        """Test cache miss scenario."""
        messages = [{"role": "user", "content": "Test query"}]
        api_response = {
            "content": "API response",
            "model": "test-model",
            "usage": {"total_tokens": 50}
        }

        # Mock Redis get to return None (cache miss)
        self.redis_mock.get.return_value = None
        # Mock the underlying client
        with patch.object(self.client.underlying_client, "chat_completion", return_value=api_response) as mock_chat:
            result = self.client.chat_completion(messages)

            # Should return API response
            assert result == api_response
            assert self.client.cache_hits == 0
            assert self.client.cache_misses == 1

            # Should call underlying client
            mock_chat.assert_called_once_with(messages, None, 0.2, None)

            # Should set cache
            self.redis_mock.setex.assert_called_once()

    def test_cache_error_handling(self):
        """Test cache error handling."""
        messages = [{"role": "user", "content": "Test query"}]
        api_response = {
            "content": "API response",
            "model": "test-model",
            "usage": {"total_tokens": 50}
        }

        # Mock Redis operations to fail
        self.redis_mock.get.side_effect = Exception("Redis connection error")
        self.redis_mock.setex.side_effect = Exception("Redis write error")

        # Mock the underlying client
        with patch.object(self.client.underlying_client, "chat_completion", return_value=api_response) as mock_chat:
            result = self.client.chat_completion(messages)

            # Should still work despite cache errors
            assert result == api_response
            mock_chat.assert_called_once()

    def test_cache_stats(self):
        """Test cache statistics tracking."""
        # Reset stats
        self.client.cache_hits = 5
        self.client.cache_misses = 3

        stats = self.client._get_cache_stats()

        assert stats["hits"] == 5
        assert stats["misses"] == 3
        assert stats["total"] == 8
        assert stats["hit_rate_percent"] == 62.5

    def test_cache_stats_zero_requests(self):
        """Test cache stats with zero requests."""
        self.client.cache_hits = 0
        self.client.cache_misses = 0

        stats = self.client._get_cache_stats()

        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["total"] == 0
        assert stats["hit_rate_percent"] == 0

    def test_clear_cache(self):
        """Test cache clearing."""
        pattern = "llm_cache:*"
        self.redis_mock.keys.return_value = ["key1", "key2", "key3"]

        result = self.client.clear_cache(pattern)

        assert result == 3
        self.redis_mock.keys.assert_called_once_with(pattern)
        self.redis_mock.delete.assert_called_once_with("key1", "key2", "key3")

    def test_clear_cache_empty(self):
        """Test clearing empty cache."""
        self.redis_mock.keys.return_value = []

        result = self.client.clear_cache()

        assert result == 0
        self.redis_mock.delete.assert_not_called()

    @patch("src.agent_core.llm_client.CachedOpenRouterClient.chat_completion")
    def test_async_chat_completion_cache_hit(self, mock_sync_chat):
        """Test async cache hit."""
        messages = [{"role": "user", "content": "Test query"}]
        cached_response = {
            "content": "Cached async response",
            "model": "test-model",
            "usage": {"total_tokens": 50}
        }

        # Mock Redis get to return cached data
        self.redis_mock.get.return_value = json.dumps(cached_response)

        import asyncio
        result = asyncio.run(self.client.async_chat_completion(messages))

        # Should return cached response
        assert result == cached_response
        assert self.client.cache_hits == 1

    @patch("src.agent_core.llm_client.CachedOpenRouterClient.chat_completion")
    def test_async_chat_completion_cache_miss(self, mock_sync_chat):
        """Test async cache miss."""
        messages = [{"role": "user", "content": "Test query"}]
        api_response = {
            "content": "Async API response",
            "model": "test-model",
            "usage": {"total_tokens": 50}
        }

        # Mock Redis get to return None (cache miss)
        self.redis_mock.get.return_value = None

        # Mock the underlying async client
        with patch.object(self.client.underlying_client, "async_chat_completion", return_value=api_response) as mock_async_chat:
            import asyncio
            result = asyncio.run(self.client.async_chat_completion(messages))

            # Should return API response
            assert result == api_response
            assert self.client.cache_misses == 1

            # Should call underlying async client
            mock_async_chat.assert_called_once()

    def test_get_cache_stats_method(self):
        """Test the public get_cache_stats method."""
        self.client.cache_hits = 10
        self.client.cache_misses = 5

        stats = self.client.get_cache_stats()

        assert stats["hits"] == 10
        assert stats["misses"] == 5
        assert stats["total"] == 15
        assert stats["hit_rate_percent"] == 66.67

    def test_delegated_methods(self):
        """Test methods delegated to underlying client."""
        with patch.object(self.client.underlying_client, "get_available_free_models", return_value=["model1", "model2"]) as mock_get_models:
            result = self.client.get_available_free_models()
            assert result == ["model1", "model2"]
            mock_get_models.assert_called_once()

        with patch.object(self.client.underlying_client, "get_model_rankings", return_value={"best": "model1"}) as mock_get_rankings:
            result = self.client.get_model_rankings()
            assert result == {"best": "model1"}
            mock_get_rankings.assert_called_once()

        with patch.object(self.client.underlying_client, "get_optimizer_stats", return_value={"stats": "data"}) as mock_get_stats:
            result = self.client.get_optimizer_stats()
            assert result == {"stats": "data"}
            mock_get_stats.assert_called_once()

    def test_cache_ttl_configuration(self):
        """Test cache TTL configuration."""
        client = CachedOpenRouterClient(ttl_seconds=7200)
        assert client.ttl_seconds == 7200

        # Test with default TTL
        client_default = CachedOpenRouterClient()
        assert client_default.ttl_seconds == 3600

    def test_cache_size_limit(self):
        """Test cache size limits (though this is more of an internal Redis concern)."""
        # This would be tested more thoroughly in integration tests
        # Here we just verify the attribute exists
        assert hasattr(self.client, "cache_size")

    def test_isa_specific_caching(self):
        """Test caching with ISA-specific queries."""
        isa_queries = [
            {"role": "user", "content": "What are CSRD compliance requirements?"},
            {"role": "user", "content": "Map GDSN attributes to XBRL taxonomy"},
            {"role": "user", "content": "Analyze ESG regulatory framework"}
        ]

        # Mock cache miss followed by hits
        self.redis_mock.get.side_effect = [None, "cached_data", "cached_data"]

        api_response = {"content": "ISA analysis", "model": "test-model"}

        with patch.object(self.client.underlying_client, "chat_completion", return_value=api_response):
            # First call - cache miss
            result1 = self.client.chat_completion(isa_queries[0])
            assert result1 == api_response
            assert self.client.cache_misses == 1

            # Second call with same query - should hit cache
            result2 = self.client.chat_completion(isa_queries[0])
            assert result2 == "cached_data"  # JSON parsed
            assert self.client.cache_hits == 1

    def test_cache_key_uniqueness(self):
        """Test that different parameters generate different cache keys."""
        base_messages = [{"role": "user", "content": "Test query"}]

        key1 = self.client._generate_cache_key(base_messages, "model1", 0.2, 100)
        key2 = self.client._generate_cache_key(base_messages, "model2", 0.2, 100)  # Different model
        key3 = self.client._generate_cache_key(base_messages, "model1", 0.5, 100)  # Different temp
        key4 = self.client._generate_cache_key(base_messages, "model1", 0.2, 200)  # Different tokens

        keys = [key1, key2, key3, key4]
        assert len(set(keys)) == 4  # All keys should be unique

    def test_cache_performance_under_load(self):
        """Test cache performance with multiple concurrent requests."""
        import threading

        results = []
        errors = []

        def make_request(query_id):
            try:
                messages = [{"role": "user", "content": f"Query {query_id}"}]
                result = self.client.chat_completion(messages)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Mock cache misses
        self.redis_mock.get.return_value = None
        api_response = {"content": "Response", "model": "test"}
        with patch.object(self.client.underlying_client, "chat_completion", return_value=api_response):
            # Simulate concurrent requests
            threads = []
            for i in range(5):
                t = threading.Thread(target=make_request, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # Should have 5 results and no errors
            assert len(results) == 5
            assert len(errors) == 0
            assert self.client.cache_misses == 5

    def test_cache_invalidation_scenarios(self):
        """Test cache invalidation scenarios."""
        messages = [{"role": "user", "content": "Test query"}]

        # Test TTL expiration (simulated)
        self.redis_mock.get.return_value = None  # Simulate expired entry

        api_response = {"content": "Fresh response"}
        with patch.object(self.client.underlying_client, "chat_completion", return_value=api_response):
            result = self.client.chat_completion(messages)
            assert result == api_response
            assert self.client.cache_misses == 1


if __name__ == "__main__":
    pytest.main([__file__])
