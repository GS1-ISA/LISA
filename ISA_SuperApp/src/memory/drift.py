from __future__ import annotations

from collections import Counter
from typing import Tuple


def _tokenize(text: str) -> list[str]:
    import re

    return re.findall(r"[a-z0-9]+", text.lower())


def cosine_similarity(a: Counter[str], b: Counter[str]) -> float:
    import math

    vocab = set(a) | set(b)
    va = [a.get(t, 0) for t in vocab]
    vb = [b.get(t, 0) for t in vocab]
    num = sum(x * y for x, y in zip(va, vb))
    da = math.sqrt(sum(x * x for x in va)) or 1e-9
    db = math.sqrt(sum(y * y for y in vb)) or 1e-9
    return num / (da * db)


def compute_drift(old: str, new: str) -> float:
    """Return drift in [0,1]; 0 = identical, 1 = fully orthogonal.
    Uses simple bag-of-words cosine.
    """
    ca = Counter(_tokenize(old))
    cb = Counter(_tokenize(new))
    sim = cosine_similarity(ca, cb)
    return 1.0 - sim


def check_drift(old: str, new: str, threshold: float = 0.5) -> Tuple[bool, float]:
    drift = compute_drift(old, new)
    return drift > threshold, drift

