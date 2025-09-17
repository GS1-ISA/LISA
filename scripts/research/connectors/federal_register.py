from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FRDoc:
    title: str
    html_url: str
    publication_date: str  # YYYY-MM-DD
    doc_type: str


def load_fixture(path: str | Path) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def normalize_fr_entries(data: dict) -> list[FRDoc]:
    docs: list[FRDoc] = []
    results = data.get("results", [])
    for it in results:
        title = (it.get("title") or "").strip()
        url = it.get("html_url") or ""
        pub = it.get("publication_date") or ""
        doc_type = it.get("type") or ""
        if not title:
            continue
        # Normalize date
        with contextlib.suppress(Exception):
            pub = datetime.fromisoformat(pub).date().isoformat()
        docs.append(
            FRDoc(title=title, html_url=url, publication_date=pub, doc_type=doc_type)
        )
    return docs
