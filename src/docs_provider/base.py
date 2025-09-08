from __future__ import annotations

# Compatibility shim to expose base types at src.docs_provider.base
try:
    from .src.docs_provider.base import (  # type: ignore
        DocsProvider,
        DocsSnippet,
        NullProvider,
        ProviderResult,
    )
except Exception:  # pragma: no cover
    # Minimal fallbacks to keep imports alive during partial refactors
    from dataclasses import dataclass
    from typing import List, Optional, Protocol

    @dataclass(frozen=True)
    class DocsSnippet:  # type: ignore
        source: str
        content: str
        version: Optional[str] = None
        url: Optional[str] = None
        license: Optional[str] = None

    @dataclass(frozen=True)
    class ProviderResult:  # type: ignore
        snippets: List[DocsSnippet]

    class DocsProvider(Protocol):  # type: ignore
        def get_docs(
            self,
            query: str,
            *,
            libs: List[str],
            version: Optional[str] = None,
            limit: int = 5,
            section_hints: Optional[List[str]] = None,
        ) -> ProviderResult:
            ...

    class NullProvider(DocsProvider):  # type: ignore
        def get_docs(
            self,
            query: str,
            *,
            libs: List[str],
            version: Optional[str] = None,
            limit: int = 5,
            section_hints: Optional[List[str]] = None,
        ) -> ProviderResult:
            return ProviderResult(snippets=[])
