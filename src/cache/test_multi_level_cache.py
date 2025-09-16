"""
Unit tests for MultiLevelCache class.
"""

import unittest
import time
import tempfile
import os
from unittest.mock import Mock, patch
from src.cache.multi_level_cache import MultiLevelCache, ISAL1Cache, ISAL2Cache, ISAL3Cache


class TestISAL1Cache(unittest.TestCase):
    """Test L1 in-memory cache."""

    def setUp(self):
        self.cache = ISAL1Cache(max_size=10, default_ttl=60)

    def test_basic_operations(self):
        """Test basic get/set operations."""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertIsNone(self.cache.get("nonexistent"))

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        self.cache.set("key1", "value1", ttl=1)
        self.assertEqual(self.cache.get("key1"), "value1")
        time.sleep(1.1)
        self.assertIsNone(self.cache.get("key1"))

    def test_priority_eviction(self):
        """Test priority-based eviction."""
        # Fill cache with low priority items
        for i in range(10):
            self.cache.set(f"low_{i}", f"value_{i}", priority=1)

        # Add high priority item
        self.cache.set("high", "high_value", priority=3)

        # Should still have high priority item
        self.assertEqual(self.cache.get("high"), "high_value")


class TestISAL2Cache(unittest.TestCase):
    """Test L2 Redis cache."""

    def setUp(self):
        self.cache = ISAL2Cache(host='localhost', port=6379, default_ttl=60)

    @patch('redis.Redis')
    def test_basic_operations(self, mock_redis):
        """Test basic operations with mocked Redis."""
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        mock_instance.get.return_value = None
        mock_instance.setex.return_value = True

        cache = ISAL2Cache()
        cache.set("key1", "value1")
        mock_instance.setex.assert_called_once()


class TestISAL3Cache(unittest.TestCase):
    """Test L3 file-based cache."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache = ISAL3Cache(cache_dir=self.temp_dir, default_ttl=60)

    def tearDown(self):
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_basic_operations(self):
        """Test basic file operations."""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertIsNone(self.cache.get("nonexistent"))

    def test_ttl_expiration(self):
        """Test TTL expiration in file cache."""
        self.cache.set("key1", "value1", ttl=1)
        self.assertEqual(self.cache.get("key1"), "value1")
        time.sleep(1.1)
        self.assertIsNone(self.cache.get("key1"))


class TestMultiLevelCache(unittest.TestCase):
    """Test full MultiLevelCache integration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache = MultiLevelCache(
            l1_max_size=5,
            l1_ttl=60,
            l2_host='localhost',
            l2_port=6379,
            l2_ttl=120,
            l3_dir=self.temp_dir,
            l3_ttl=300
        )

    def tearDown(self):
        # Clean up
        self.cache.clear()
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    @patch('redis.Redis')
    def test_promotion_logic(self, mock_redis):
        """Test cache promotion from L3 to L1."""
        # Mock Redis to simulate misses
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        mock_instance.get.return_value = None

        # Set in L3 (simulated by setting directly)
        self.cache.l3.set("test_key", "test_value")

        # Get should promote to L1
        result = self.cache.get("test_key")
        self.assertEqual(result, "test_value")

        # Should now be in L1
        self.assertEqual(self.cache.l1.get("test_key"), "test_value")

    def test_isa_priority_rules(self):
        """Test ISA-specific priority rules."""
        # Test high priority pattern
        self.cache.set("llm_response_1", "high_priority_data")
        # Should be in L1 with high priority
        self.assertEqual(self.cache.l1.get("llm_response_1"), "high_priority_data")

    def test_ttl_rules(self):
        """Test ISA-specific TTL rules."""
        # Test long TTL pattern
        self.cache.set("static_config", "config_data")
        # Should have longer TTL
        stats = self.cache.get_stats()
        self.assertIn('isa_optimizations', stats)

    def test_statistics_tracking(self):
        """Test comprehensive statistics."""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss

        stats = self.cache.get_stats()
        self.assertIn('l1_hits', stats)
        self.assertIn('l1_misses', stats)
        self.assertIn('overall_hit_rate', stats)
        self.assertIn('isa_optimizations', stats)


if __name__ == '__main__':
    unittest.main()