from __future__ import annotations

from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    """Very simple HTML → text extractor (deterministic).

    Removes scripts/styles, collapses whitespace, returns UTF-8 text.
    """
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ")
    # Normalize whitespace
    text = " ".join(text.split())
    return text.strip()
