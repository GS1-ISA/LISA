"""Canonical JSON writing utilities.

Provides deterministic JSON serialization for snapshot tests and reproducible artifacts
without introducing extra dependencies. Uses stdlib json with sorted keys and
compact separators, UTF-8 encoding, and explicit newline policy.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def canonical_dumps(obj: Any, *, use_orjson: bool | None = None) -> str:
    """Return a canonical JSON string.

    - Sorted keys
    - Compact separators (no extra spaces)
    - ensure_ascii=False (UTF-8)
    - No trailing spaces; caller controls newline policy
    """
    if use_orjson is None:
        use_orjson = os.getenv("CANONICAL_USE_ORJSON", "0") == "1"
    if use_orjson:
        try:
            import orjson  # type: ignore

            # orjson.dumps returns bytes
            return orjson.dumps(
                obj,
                option=orjson.OPT_SORT_KEYS,
            ).decode("utf-8")
        except Exception:
            # Fallback to stdlib
            pass
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_dump_file(obj: Any, path: str | Path, newline: str = "\n") -> None:
    """Write canonical JSON to a file with a consistent newline policy."""
    p = Path(path)
    data = canonical_dumps(obj) + newline
    p.write_text(data, encoding="utf-8", newline="")
