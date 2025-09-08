
import os
import logging
import json
import time
from pathlib import Path
from typing import List, Optional, Tuple

try:
    # Local feature flags (ISA_D-native)
    from src.feature_flags import FLAGS_FILE
except Exception:  # pragma: no cover
    FLAGS_FILE = Path("infra/feature_flags/local_flags.json")

try:
    from prometheus_client import Counter
    DOCS_PROVIDER_PATH_TOTAL = Counter(
        "docs_provider_path_total",
        "Docs provider path selections",
        labelnames=("path", "flag"),
    )
except Exception:  # pragma: no cover
    DOCS_PROVIDER_PATH_TOTAL = None  # type: ignore

from .base import DocsProvider, ProviderResult, DocsSnippet, NullProvider
from .cache import DiskCache

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Context7Provider(DocsProvider):
    """A client for the Context7 documentation service."""

    def __init__(self):
        self.api_url = os.getenv("CONTEXT7_API_URL", "https://api.context7.com/v1")
        self.project = os.getenv("CONTEXT7_PROJECT")
        self.api_key = os.getenv("CONTEXT7_KEY")
        self.allowed_sources = os.getenv("CONTEXT7_ALLOWED_SOURCES", "").split(',')
        
        cache_ttl = int(os.getenv("CONTEXT7_CACHE_TTL", "3600"))
        self.cache = DiskCache(ttl=cache_ttl)

    def get_docs(
        self,
        query: str,
        *, 
        libs: List[str],
        version: Optional[str] = None,
        limit: int = 5,
        section_hints: Optional[List[str]] = None
    ) -> ProviderResult:
        """Fetches documentation, using a cache and respecting feature flags."""
        cached_result = self.cache.get(query, libs, version)
        if cached_result:
            logging.info(f"Context7 cache hit for query: '{query}'")
            snippets = [DocsSnippet(**data) for data in cached_result]
            return ProviderResult(snippets=snippets)

        if not self.api_key or not self.project:
            logging.warning("Context7 API key or project not set. Returning no docs.")
            return ProviderResult(snippets=[])

        # This is where the actual HTTP request to the Context7 API would go.
        # We will simulate it for now.
        logging.info(f"Context7 API call for query: '{query}' on libs: {libs}")
        simulated_snippets = self._simulate_api_call(query, libs, limit)
        
        # Save to cache
        self.cache.set(query, libs, version, [s.__dict__ for s in simulated_snippets])

        return ProviderResult(snippets=simulated_snippets)

    def _simulate_api_call(self, query: str, libs: List[str], limit: int) -> List[DocsSnippet]:
        """Simulates a call to the external Context7 API."""
        # In a real scenario, this would make an HTTP request.
        # For now, return dummy data based on the library.
        if not libs:
            return []
        
        lib_name = libs[0]
        return [
            DocsSnippet(
                source=f"Context7:{lib_name}",
                content=f"This is a simulated documentation snippet for '{query}' from the library '{lib_name}'.",
                version="1.0.0",
                url=f"https://docs.example.com/{lib_name}/{query.replace(' ', '-')}"
            )
            for _ in range(limit)
        ]

    def _log_memory_event(self, query: str, libs: List[str], cache_hit: bool):
        """Logs a memory event for the API call."""
        try:
            log_path = Path("agent/memory/memory_log.jsonl")
            log_path.parent.mkdir(parents=True, exist_ok=True)
            event = {
                "ts": time.time(),
                "kind": "context7",
                "query": query,
                "libs": libs,
                "cache_hit": cache_hit
            }
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logging.warning(f"Failed to log Context7 memory event: {e}")

def get_provider() -> DocsProvider:
    """Factory to select docs provider with env override + feature flag canary.

    Selection order:
    1) ENV override: CONTEXT7_ENABLED=1 → Context7Provider (new path)
    2) Feature flag: any ISA_REF_DOCS_PROVIDER_* with traffic>0 → Context7Provider
    3) Default: NullProvider (old path)
    """
    env_on = os.getenv("CONTEXT7_ENABLED", "0") == "1"
    flags_allowed = os.getenv("FEATURE_FLAGS_ENABLED", "0") == "1"
    flag_on, flag_name, traffic = _docs_flag_signal() if flags_allowed else (False, "", 0)

    if env_on:
        _record_path_metric("new", flag="ENV")
        logging.info("Context7 selected via ENV override.")
        return Context7Provider()

    if flag_on and traffic > 0:
        _record_path_metric("new", flag=flag_name or "ISA_REF_DOCS_PROVIDER")
        logging.info(
            f"Context7 selected via feature flag {flag_name} at traffic {traffic}%"
        )
        return Context7Provider()

    _record_path_metric("old", flag=flag_name or "-")
    logging.info("Context7 disabled → using NullProvider (old path).")
    return NullProvider()


def _docs_flag_signal() -> Tuple[bool, str, int]:
    """Check local flags for any ISA_REF_DOCS_PROVIDER_* set with traffic>0."""
    try:
        if not FLAGS_FILE.exists():
            return False, "", 0
        data = json.loads(FLAGS_FILE.read_text(encoding="utf-8"))
        flags = data.get("flags", {}) if isinstance(data, dict) else {}
        for name, cfg in flags.items():
            if isinstance(name, str) and name.startswith("ISA_REF_DOCS_PROVIDER_") and isinstance(cfg, dict):
                enabled = bool(cfg.get("enabled", False))
                try:
                    traffic = int(cfg.get("traffic", 0))
                except Exception:
                    traffic = 0
                if enabled and traffic > 0:
                    return True, name, traffic
        return False, "", 0
    except Exception:
        return False, "", 0


def _record_path_metric(path: str, flag: str) -> None:
    try:
        if DOCS_PROVIDER_PATH_TOTAL is not None:
            DOCS_PROVIDER_PATH_TOTAL.labels(path=path, flag=flag).inc()
    except Exception:
        pass
