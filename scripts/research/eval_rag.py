"""Offline RAG eval (minimal).

Loads a VectorIndex storage and runs a small set of queries, printing top hit ids.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def run_eval(storage_path: str | Path, queries: list[str]) -> dict:
    repo = Path(__file__).resolve().parents[2]
    sa_src = repo / "ISA_SuperApp" / "src"
    if str(sa_src) not in sys.path:
        sys.path.insert(0, str(sa_src))
    from retrieval import VectorIndex  # type: ignore

    vi = VectorIndex(storage_path=str(storage_path))
    out = {}
    for q in queries:
        hits = vi.search(q, k=3)
        out[q] = [h.get("id") for h in hits]
    return out


if __name__ == "__main__":
    storage = Path(sys.argv[1] if len(sys.argv) > 1 else "research_index.json")
    queries = ["WebAuthn", "WebRTC"]
    res = run_eval(storage, queries)
    print(json.dumps(res, indent=2))
