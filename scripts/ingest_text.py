#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.agent_core.memory.rag_store import RAGMemory


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(
        description="Ingest a local text file into the vector store with canonical metadata and write a manifest"
    )
    p.add_argument("--doc-id", required=True, help="Document ID (schema: document_id)")
    p.add_argument(
        "--source",
        required=True,
        help="Canonical source (e.g., iso-27001, internal-policy-hr, or a URL)",
    )
    p.add_argument("--file", required=True, help="Path to a UTF-8 text file to ingest")
    p.add_argument("--page", type=int, default=None, help="Optional page number")
    p.add_argument(
        "--out-dir",
        default="data/ingestion_manifests",
        help="Directory to write manifest JSON",
    )
    args = p.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        raise SystemExit(f"Input file not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")
    checksum = sha256_hex(text)

    rag = RAGMemory()
    rag.add(text=text, source=args.source, doc_id=args.doc_id, page=args.page)

    # Write a simple manifest capturing lineage
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "document_id": args.doc_id,
        "source_uri": args.source,
        "ingested_from": str(file_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "raw_checksum": f"sha256:{checksum}",
        "chunking": {"size": 1000, "overlap": 200},
        "embedding_model": rag.embedding_model_name,
    }
    out_path = out_dir / f"{args.doc_id}.json"
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Ingested '{args.doc_id}' from {file_path} -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
