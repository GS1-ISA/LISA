#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def _connect(path: Path, collection: str):
    import chromadb

    client = chromadb.PersistentClient(path=str(path))
    col = client.get_or_create_collection(name=collection)
    return col


def _peek(col, n: int = 5) -> Dict[str, Any]:
    # Try peek (preferred), fall back to get(limit=...)
    try:
        return col.peek(n)
    except Exception:
        try:
            return col.get(limit=n)
        except Exception as e:
            raise RuntimeError(f"Failed to read collection: {e}")


REQUIRED = [
    "document_id",
    "source",
    "chunk_id",
    "chunk_text",
    "created_at",
    "embedding_model",
    "language",
    "checksum",
]


def _validate(mds: List[Dict[str, Any]]) -> List[str]:
    problems: List[str] = []
    for i, md in enumerate(mds):
        missing = [k for k in REQUIRED if k not in md]
        if missing:
            problems.append(f"item {i} missing: {', '.join(missing)}")
    return problems


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Inspect vector store entries and validate schema fields"
    )
    p.add_argument(
        "--path",
        default="storage/vector_store/research_db",
        help="Persistent DB directory",
    )
    p.add_argument(
        "--collection", default="research_collection", help="Collection name"
    )
    p.add_argument("--limit", type=int, default=5, help="Number of entries to preview")
    args = p.parse_args(argv)

    col = _connect(Path(args.path), args.collection)
    try:
        count = col.count()
    except Exception:
        count = -1

    data = _peek(col, args.limit)
    docs = data.get("documents", []) or []
    mds = data.get("metadatas", []) or []
    ids = data.get("ids", []) or []

    problems = _validate(mds)

    print("--- Vector Store Inspection ---")
    print(f"path: {args.path}")
    print(f"collection: {args.collection}")
    print(f"count: {count}")
    print(f"preview: {len(docs)} items")
    for i in range(len(docs)):
        print(
            f"- id: {ids[i] if i < len(ids) else '?'} | source: {mds[i].get('source','?')} | chunk_id: {mds[i].get('chunk_id','?')}"
        )
    if problems:
        print("\nSchema issues:")
        for pbl in problems:
            print(f"- {pbl}")
        return 1
    else:
        print("\nSchema validation: OK (required fields present)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
