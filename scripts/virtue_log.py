#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


OUT = Path("agent/outcomes/virtue_log.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def main() -> int:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "mission": env("VIRTUE_MISSION", "R"),
        "reason": env("VIRTUE_REASON", "auto"),
        "metric": env("VIRTUE_METRIC", "n/a"),
        "delta": env("VIRTUE_DELTA", "0"),
        "notes": env("VIRTUE_NOTES", ""),
    }
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
