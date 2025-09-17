from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TRDoc:
    title: str
    url: str
    date: str  # ISO date
    status: str


def load_fixture(path: str | Path) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def normalize_tr_entries(data: dict) -> list[TRDoc]:
    docs: list[TRDoc] = []
    items = data.get("items", [])
    for it in items:
        title = it.get("title", "")
        url = it.get("url", "")
        date = it.get("date", "")
        status = it.get("status", "")
        # Normalize date to YYYY-MM-DD when possible
        try:
            dt = datetime.fromisoformat(date.replace("Z", "+00:00")).date().isoformat()
        except Exception:
            dt = date
        docs.append(TRDoc(title=title, url=url, date=dt, status=status))
    return docs
