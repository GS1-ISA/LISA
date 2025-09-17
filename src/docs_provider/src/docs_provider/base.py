from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DocsSnippet:
    """A single snippet of documentation."""

    source: str
    content: str
    version: str | None = None
    url: str | None = None
    license: str | None = None


@dataclass(frozen=True)
class ProviderResult:
    """The result returned by a documentation provider."""

    snippets: list[DocsSnippet]


class DocsProvider(Protocol):
    """A protocol for a documentation provider."""

    def get_docs(
        self,
        query: str,
        *,
        libs: list[str],
        version: str | None = None,
        limit: int = 5,
        section_hints: list[str] | None = None,
    ) -> ProviderResult:
        """Fetches documentation for a given query."""
        ...


class NullProvider(DocsProvider):
    """A default, no-op provider that returns no results."""

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
