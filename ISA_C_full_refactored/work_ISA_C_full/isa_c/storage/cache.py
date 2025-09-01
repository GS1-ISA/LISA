from __future__ import annotations
import hashlib, os

try:
    from diskcache import Cache  # type: ignore
except Exception:  # noqa: BLE001
    Cache = None  # type: ignore


class DataCache:
    def __init__(self, cache_dir: str = ".cache", ttl: int = 3600):
        self.ttl = ttl
        self.cache = Cache(cache_dir) if Cache else None

    def get_or_fetch(self, key: str, fetch_func):
        ck = hashlib.md5(key.encode()).hexdigest()
        if self.cache:
            if ck in self.cache:
                return self.cache[ck]
            data = fetch_func()
            self.cache.set(ck, data, expire=self.ttl)
            return data
        # Fallback: no persistent cache
        return fetch_func()
