
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Any

class DiskCache:
    """A simple, file-based cache with TTL."""

    def __init__(self, cache_dir: str | Path = ".cache/docs_provider", ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, query: str, libs: list[str], version: Optional[str]) -> str:
        """Creates a deterministic cache key."""
        key_string = f"{query}|{'|'.join(sorted(libs))}|{version or ''}"
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(self, query: str, libs: list[str], version: Optional[str]) -> Optional[Any]:
        """Retrieves an item from the cache if it exists and is not expired."""
        key = self._get_cache_key(query, libs, version)
        path = self.cache_dir / key
        if not path.exists():
            return None

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            if time.time() - data.get("timestamp", 0) > self.ttl:
                path.unlink()
                return None
            
            return data.get("payload")
        except (IOError, json.JSONDecodeError):
            return None

    def set(self, query: str, libs: list[str], version: Optional[str], payload: Any):
        """Saves an item to the cache."""
        key = self._get_cache_key(query, libs, version)
        path = self.cache_dir / key
        data = {
            "timestamp": time.time(),
            "payload": payload
        }
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f)
        except IOError:
            pass # Fail silently if cache write fails

    def purge(self):
        """Removes all items from the cache directory."""
        for item in self.cache_dir.iterdir():
            item.unlink()
