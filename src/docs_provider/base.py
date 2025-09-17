from __future__ import annotations

# Compatibility shim to expose base types at src.docs_provider.base
try:
    from .src.docs_provider.base import (
        DocsProvider,
        DocsSnippet,
        NullProvider,
        ProviderResult,
    )
except Exception:  # pragma: no cover
    # Minimal fallbacks to keep imports alive during partial refactors
    from dataclasses import dataclass
    from typing import Protocol

    @dataclass(frozen=True)
    class DocsSnippet:  # type: ignore[no-redef]
        source: str
        content: str
        version: str | None = None
        url: str | None = None
        license: str | None = None

    @dataclass(frozen=True)
    class ProviderResult:  # type: ignore[no-redef]
        snippets: list[DocsSnippet]

    class DocsProvider(Protocol):  # type: ignore[no-redef]
        def get_docs(
            self,
            query: str,
            *,
            libs: list[str],
            version: str | None = None,
            limit: int = 5,
            section_hints: list[str] | None = None,
        ) -> ProviderResult: ...

    class NullProvider(DocsProvider):  # type: ignore[no-redef]
        def get_docs(
            self,
            query: str,
            *,
            libs: list[str],
            version: str | None = None,
            limit: int = 5,
            section_hints: list[str] | None = None,
        ) -> ProviderResult:
            return ProviderResult(snippets=[])


__all__ = [
    "DocsProvider",
    "DocsSnippet",
    "NullProvider",
    "ProviderResult",
]
