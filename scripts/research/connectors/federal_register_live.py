from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests


@dataclass
class FRDoc:
    title: str
    html_url: str
    publication_date: str
    doc_type: str


def fetch_fr_docs(
    query: str, limit: int = 5, *, allow_network: bool = False, timeout: int = 20
) -> List[FRDoc]:
    """Fetch Federal Register documents via API (optional; default OFF).

    Respects env ALLOW_RESEARCH_LIVE=1 to enable without passing allow_network.
    """
    if not (allow_network or os.getenv("ALLOW_RESEARCH_LIVE", "0") == "1"):
        return []
    url = "https://www.federalregister.gov/api/v1/documents.json"
    params = {"per_page": limit, "search": query}
    headers = {"User-Agent": "ISA-ResearchBot"}
    r = requests.get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    out: List[FRDoc] = []
    for it in data.get("results", [])[:limit]:
        title = (it.get("title") or "").strip()
        html_url = it.get("html_url") or ""
        pub = it.get("publication_date") or ""
        doc_type = it.get("type") or ""
        try:
            pub = datetime.fromisoformat(pub).date().isoformat()
        except Exception:
            pass
        if title:
            out.append(
                FRDoc(
                    title=title,
                    html_url=html_url,
                    publication_date=pub,
                    doc_type=doc_type,
                )
            )
    return out
