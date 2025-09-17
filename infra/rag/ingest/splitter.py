from __future__ import annotations


def split_text(text: str, max_len: int = 100) -> list[str]:
    """Deterministic splitter for RAG stubs.

    Splits on whitespace boundaries; ensures UTF-8 stable newline policy is irrelevant at this layer.
    """
    if not text:
        return []
    words = text.split()
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for w in words:
        if cur_len + 1 + len(w) > max_len and cur:
            chunks.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len = (cur_len + 1 + len(w)) if cur_len else len(w)
    if cur:
        chunks.append(" ".join(cur))
    return chunks
