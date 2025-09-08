from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol


@dataclass(frozen=True)
class DocsSnippet:
    """A single snippet of documentation."""

    source: str
    content: str
    version: Optional[str] = None
    url: Optional[str] = None
    license: Optional[str] = None


@dataclass(frozen=True)
class ProviderResult:
    """The result returned by a documentation provider."""

    snippets: List[DocsSnippet]


class DocsProvider(Protocol):
    """A protocol for a documentation provider."""

    def get_docs(
        self,
        query: str,
        *,
        libs: List[str],
        version: Optional[str] = None,
        limit: int = 5,
        section_hints: Optional[List[str]] = None,
    ) -> ProviderResult:
        """Fetches documentation for a given query."""
        ...


class NullProvider(DocsProvider):
    """A default, no-op provider that returns no results."""

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
