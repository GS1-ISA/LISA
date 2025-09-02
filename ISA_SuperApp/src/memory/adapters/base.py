from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Protocol


@dataclass
class MemoryRecord:
    kind: str  # e.g., short_term | long_term | structured
    content: str
    meta: dict[str, Any]


class MemoryAdapter(Protocol):
    def available(self) -> bool: ...

    def store(self, rec: MemoryRecord) -> None: ...

    def retrieve(self, query: str, k: int = 5) -> List[str]: ...

    def summarize(self, items: Iterable[str], max_len: int = 512) -> str: ...

    def delete(self, query: str) -> int: ...

    def embed(self, texts: list[str]) -> list[list[float]] | None: ...

