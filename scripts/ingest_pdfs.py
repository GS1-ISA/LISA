#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# Optional deps: PyPDF2 and PyYAML
try:  # pdf reader
    from PyPDF2 import PdfReader  # type: ignore
except Exception:  # pragma: no cover - optional import
    PdfReader = None  # type: ignore

try:  # yaml loader
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional import
    yaml = None  # type: ignore


@dataclass
class SourceSpec:
    path: Path
    include: list[str]


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()


def load_manifest(path: Path) -> tuple[list[SourceSpec], int]:
    if yaml is None:
        raise RuntimeError("PyYAML not installed; run: pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    src_specs: list[SourceSpec] = []
    for src in data.get("source", []) or []:
        base = Path(src.get("path", "."))
        include = list(src.get("include", []))
        src_specs.append(SourceSpec(path=base, include=include))
    # default: page chunking capped by max_pages
    max_pages = int((data.get("chunking", {}) or {}).get("max_pages", 50))
    return src_specs, max_pages


def iter_pdfs(specs: list[SourceSpec]) -> Iterable[Path]:
    for spec in specs:
        base = spec.path
        if not base.exists():
            continue
        patterns = spec.include or ["*.pdf"]
        for pat in patterns:
            for p in base.rglob(pat):
                if p.suffix.lower() == ".pdf":
                    yield p


def extract_pages(pdf_path: Path, max_pages: int) -> list[tuple[int, str]]:
    if PdfReader is None:
        raise RuntimeError("PyPDF2 not installed; run: pip install PyPDF2")
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:  # corrupt or encrypted
        return []
    pages: list[tuple[int, str]] = []
    limit = min(max_pages, len(reader.pages)) if max_pages > 0 else len(reader.pages)
    for i in range(limit):
        try:
            text = reader.pages[i].extract_text() or ""
        except Exception:
            text = ""
        # Normalize whitespace lightly
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        pages.append((i + 1, text))
    return pages


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ingest PDFs into a simple JSONL index (advisory/offline)"
    )
    ap.add_argument(
        "--manifest",
        default="data/ingestion_manifests/isa_goals_pdfs_manifest.yaml",
        help="Path to ingestion manifest YAML",
    )
    ap.add_argument("--out", default="pdf_index.jsonl", help="Output JSONL path")
    ap.add_argument(
        "--max-pages", type=int, default=None, help="Override max pages per PDF"
    )
    ns = ap.parse_args()

    specs, max_pages_manifest = load_manifest(Path(ns.manifest))
    max_pages = int(ns.max_pages) if ns.max_pages is not None else max_pages_manifest

    out_path = Path(ns.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with out_path.open("w", encoding="utf-8") as wf:
        for pdf in iter_pdfs(specs):
            pages = extract_pages(pdf, max_pages=max_pages)
            for page_no, text in pages:
                rec = {
                    "document_id": pdf.stem,
                    "source": str(pdf),
                    "page": page_no,
                    "text": text[:4000],  # cap per-line for safety
                    "checksum": sha256_text(text),
                }
                wf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1
    print(f"Wrote {count} page records to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
