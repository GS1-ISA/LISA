from __future__ import annotations

# Compatibility shim to expose get_provider at src.docs_provider.context7
# while the implementation currently lives under src/docs_provider/src/docs_provider/context7.py

try:
    from .src.docs_provider.context7 import Context7Provider, get_provider
except Exception:  # pragma: no cover
    # Fallback to base NullProvider if implementation path changes
    from .src.docs_provider.base import NullProvider as Context7Provider

    def get_provider():
        return Context7Provider()


__all__ = ["Context7Provider", "get_provider"]
