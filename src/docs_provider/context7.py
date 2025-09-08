from __future__ import annotations

# Compatibility shim to expose get_provider at src.docs_provider.context7
# while the implementation currently lives under src/docs_provider/src/docs_provider/context7.py

try:
    from .src.docs_provider.context7 import (  # type: ignore
        Context7Provider,
        get_provider,
    )
except Exception:  # pragma: no cover
    # Fallback to base NullProvider if implementation path changes
    from .src.docs_provider.base import NullProvider as Context7Provider  # type: ignore

    def get_provider():  # type: ignore
        return Context7Provider()
