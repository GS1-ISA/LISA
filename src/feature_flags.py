from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FLAGS_FILE = Path("infra/feature_flags/local_flags.json")


def _load() -> dict[str, Any]:
    if not FLAGS_FILE.exists():
        FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        FLAGS_FILE.write_text(json.dumps({"flags": {}}, indent=2), encoding="utf-8")
    try:
        return json.loads(FLAGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"flags": {}}


def _save(data: dict[str, Any]) -> None:
    FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def is_enabled(name: str) -> bool:
    data = _load()
    cfg = data.get("flags", {}).get(name)
    if not isinstance(cfg, dict):
        return False
    return bool(cfg.get("enabled", False))


def traffic_percent(name: str) -> int:
    data = _load()
    cfg = data.get("flags", {}).get(name)
    if not isinstance(cfg, dict):
        return 0
    try:
        return int(cfg.get("traffic", 0))
    except Exception:
        return 0


def set_flag(name: str, enabled: bool, traffic: int = 0) -> None:
    data = _load()
    data.setdefault("flags", {})[name] = {
        "enabled": bool(enabled),
        "traffic": int(max(0, min(100, traffic))),
    }
    _save(data)
