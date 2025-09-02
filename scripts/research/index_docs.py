from __future__ import annotations

"""Index normalized research docs into the SuperApp retrieval index (offline‑first).

This utility is designed to run in PR CI without network access. It can ingest
fixture JSON files (e.g., W3C TR index) and write a VectorIndex storage JSON.

Usage (Python):
  from scripts.research.index_docs import index_tr_fixture
  index_tr_fixture('scripts/research/tests/fixtures/w3c_tr_index.json', 'storage/research_index.json')
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple


def _ensure_superapp_on_path() -> None:
    repo = Path(__file__).resolve().parents[2]
    sa = repo / "ISA_SuperApp"
    src = sa / "src"
    for p in (str(sa), str(src)):
        if p not in sys.path:
            sys.path.insert(0, p)


def _load_json(path: str | Path) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def _normalize_tr_entries(data: dict) -> List[Tuple[str, str, dict]]:
    """Return docs as (id, text, meta) tuples from W3C TR style JSON."""
    items = data.get("items", [])
    docs: List[Tuple[str, str, dict]] = []
    for it in items:
        title = it.get("title", "").strip()
        url = it.get("url", "")
        status = it.get("status", "")
        date = it.get("date", "")
        if not title:
            continue
        doc_id = f"TR:{title}"
        text = f"{title} ({status}) — {url} — {date}"
        docs.append((doc_id, text, {"source": "w3c_tr", "url": url, "status": status, "date": date}))
    return docs


def index_tr_fixture(fixture_path: str | Path, storage_path: str | Path) -> int:
    """Load a TR fixture JSON and write/update a VectorIndex storage file.

    Returns number of docs written.
    """
    _ensure_superapp_on_path()
    from ISA_SuperApp.src.retrieval import VectorIndex  # type: ignore

    data = _load_json(fixture_path)
    docs = _normalize_tr_entries(data)
    vi = VectorIndex(storage_path=str(storage_path))
    vi.rebuild(docs)
    return len(docs)


def _normalize_fr_entries(data: dict) -> List[Tuple[str, str, dict]]:
    """Return docs as (id, text, meta) tuples from Federal Register JSON."""
    results = data.get("results", [])
    docs: List[Tuple[str, str, dict]] = []
    for it in results:
        title = (it.get("title") or "").strip()
        url = it.get("html_url") or ""
        date = it.get("publication_date") or ""
        doc_type = it.get("type") or ""
        if not title:
            continue
        doc_id = f"FR:{title}"
        text = f"{title} ({doc_type}) — {url} — {date}"
        docs.append((doc_id, text, {"source": "federal_register", "url": url, "status": doc_type, "date": date}))
    return docs


def index_fr_fixture(fixture_path: str | Path, storage_path: str | Path) -> int:
    """Load a Federal Register fixture JSON and write/update a VectorIndex storage file.

    Returns number of docs written.
    """
    _ensure_superapp_on_path()
    from ISA_SuperApp.src.retrieval import VectorIndex  # type: ignore

    data = _load_json(fixture_path)
    docs = _normalize_fr_entries(data)
    vi = VectorIndex(storage_path=str(storage_path))
    vi.rebuild(docs)
    return len(docs)



def kg_from_normalized(docs: list[tuple[str,str,dict]], kg_path: str | Path) -> int:
    """Write normalized docs as KG entities with provenance.

    Each doc becomes an entity with observations containing URL/status/date.
    """
    _ensure_superapp_on_path()
    from ISA_SuperApp.src.memory_store import KnowledgeGraphMemory  # type: ignore

    kg = KnowledgeGraphMemory(path=str(kg_path))
    count = 0
    for doc_id, _text, meta in docs:
        url = meta.get("url", "")
        status = meta.get("status", "")
        date = meta.get("date", "")
        kg.create_entity(doc_id, type=meta.get("source", "research"))
        obs = [s for s in (f"url:{url}", f"status:{status}", f"date:{date}") if s and not s.endswith(":")]
        if obs:
            kg.add_observations(doc_id, obs)
            count += 1
    return count
