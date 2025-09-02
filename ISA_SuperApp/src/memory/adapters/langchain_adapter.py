from __future__ import annotations

from typing import Iterable, List

from .base import MemoryAdapter, MemoryRecord


class LangChainMemoryAdapter(MemoryAdapter):
    """Lightweight wrapper. Uses stubs if langchain is not installed.

    We model buffer/summary/vector behaviors minimally to keep runtime optional.
    """

    def __init__(self) -> None:
        self._buf: list[str] = []
        try:
            import langchain  # noqa: F401
            self._available = True
        except Exception:
            self._available = False

    def available(self) -> bool:
        return self._available

    def store(self, rec: MemoryRecord) -> None:
        self._buf.append(rec.content)

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        # naive lexical filter from buffer
        q = query.lower()
        hits = [x for x in self._buf if q in x.lower()]
        return hits[:k]

    def summarize(self, items: Iterable[str], max_len: int = 512) -> str:
        text = " ".join(items)
        return (text[: max_len - 3] + "...") if len(text) > max_len else text

    def delete(self, query: str) -> int:
        before = len(self._buf)
        q = query.lower()
        self._buf = [x for x in self._buf if q not in x.lower()]
        return before - len(self._buf)

    def embed(self, texts: list[str]) -> list[list[float]] | None:
        # Defer to existing vector index if present; keep adapter simple here
        return None
