import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional
import sys
import os

# Add the src directory to the path to import MultiLevelCache
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from src.cache.multi_level_cache import get_multilevel_cache


class DiskCache:
    """Multi-level cache wrapper for docs provider with ISA optimizations."""

    def __init__(self, cache_dir: str | Path = ".cache/docs_provider", ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Use MultiLevelCache for better performance
        self.multilevel_cache = get_multilevel_cache()

    def _get_cache_key(
        self, query: str, libs: list[str], version: Optional[str]
    ) -> str:
        """Creates a deterministic cache key."""
        key_string = f"{query}|{'|'.join(sorted(libs))}|{version or ''}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, query: str, libs: list[str], version: Optional[str]) -> Optional[Any]:
        """Retrieves an item from the multi-level cache."""
        key = self._get_cache_key(query, libs, version)
        return self.multilevel_cache.get(f"docs:{key}")

    def set(self, query: str, libs: list[str], version: Optional[str], payload: Any):
        """Saves an item to the multi-level cache."""
        key = self._get_cache_key(query, libs, version)
        self.multilevel_cache.set(f"docs:{key}", payload)

    def purge(self):
        """Removes all items from the multi-level cache."""
        self.multilevel_cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return self.multilevel_cache.get_stats()
