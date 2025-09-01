from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

try:
    import fastjsonschema
except Exception:  # pragma: no cover - optional
    fastjsonschema = None


def compile_schema(schema: Dict[str, Any]) -> Callable[[Dict[str, Any]], None]:
    if fastjsonschema is None:  # pragma: no cover - optional
        raise RuntimeError("fastjsonschema not installed")
    return fastjsonschema.compile(schema)


def compile_schema_file(path: str | Path) -> Callable[[Dict[str, Any]], None]:
    if fastjsonschema is None:  # pragma: no cover - optional
        raise RuntimeError("fastjsonschema not installed")
    p = Path(path)
    data = p.read_text(encoding="utf-8")
    import json

    return fastjsonschema.compile(json.loads(data))
