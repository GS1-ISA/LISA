from __future__ import annotations

from typing import Iterable, List

from .base import MemoryAdapter, MemoryRecord


class _StubAdapter(MemoryAdapter):
    def __init__(self, name: str) -> None:
        self._name = name
        self._buf: list[str] = []

    def available(self) -> bool:
        return False

    def store(self, rec: MemoryRecord) -> None:
        # keep local minimal buffer for deterministic tests
        self._buf.append(rec.content)

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        q = query.lower()
        return [x for x in self._buf if q in x.lower()][:k]

    def summarize(self, items: Iterable[str], max_len: int = 512) -> str:
        text = " ".join(items)
        return (text[: max_len - 3] + "...") if len(text) > max_len else text

    def delete(self, query: str) -> int:
        before = len(self._buf)
        q = query.lower()
        self._buf = [x for x in self._buf if q not in x.lower()]
        return before - len(self._buf)

    def embed(self, texts: list[str]) -> list[list[float]] | None:
        return None


class MemEngineAdapter(_StubAdapter):
    pass


class ZepAdapter(_StubAdapter):
    pass


class AMemAdapter(_StubAdapter):
    pass


class AwsAugmentedAdapter(_StubAdapter):
    pass


class McpAdapter(_StubAdapter):
    pass

