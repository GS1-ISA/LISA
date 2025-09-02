from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional

from .base import MemoryAdapter, MemoryRecord


@dataclass
class StructuredFact:
    id: str
    kind: str
    title: str
    data: dict


class StructuredMemoryAdapter(MemoryAdapter):
    """Structured memory via Pydantic-like models (local, no heavy deps).

    If Agno or Pydantic-AI are present, this class can be extended to integrate
    their stores; for now we keep a local typed store and deterministic behavior.
    """

    def __init__(self) -> None:
        self._store: dict[str, StructuredFact] = {}

    def available(self) -> bool:
        return True

    def store(self, rec: MemoryRecord) -> None:
        title = rec.meta.get("title") or rec.content[:40]
        fid = rec.meta.get("id") or f"fact:{len(self._store)+1}"
        self._store[fid] = StructuredFact(id=fid, kind=rec.kind, title=title, data=rec.meta | {"content": rec.content})

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        q = query.lower()
        hits: list[tuple[int, str]] = []
        for f in self._store.values():
            text = f"{f.title} {f.data.get('content','')}".lower()
            score = text.count(q)
            if score:
                hits.append((score, f"{f.title}: {f.data.get('content','')}") )
        hits.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in hits[:k]]

    def summarize(self, items: Iterable[str], max_len: int = 512) -> str:
        text = " ".join(items)
        return (text[: max_len - 3] + "...") if len(text) > max_len else text

    def delete(self, query: str) -> int:
        q = query.lower()
        keys = [k for k, f in self._store.items() if q in (f.title.lower() + str(f.data).lower())]
        for k in keys:
            del self._store[k]
        return len(keys)

    def embed(self, texts: list[str]) -> list[list[float]] | None:
        return None

