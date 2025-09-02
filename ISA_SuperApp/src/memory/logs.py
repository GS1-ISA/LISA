from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class MemoryEvent:
    ts_iso: str
    kind: str
    session_id: str
    content: str
    meta: dict[str, Any]


class MemoryEventLogger:
    def __init__(self, root: str | Path | None = None) -> None:
        base = Path(root) if root else Path("agent") / "memory"
        base.mkdir(parents=True, exist_ok=True)
        self.path = base / "memory_log.jsonl"

    def log(self, kind: str, session_id: str, content: str, meta: dict[str, Any] | None = None) -> None:
        ev = MemoryEvent(
            ts_iso=datetime.now(timezone.utc).isoformat(),
            kind=kind,
            session_id=session_id,
            content=content,
            meta=meta or {},
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(ev), ensure_ascii=False) + "\n")

    def snapshot_to(self, out_path: str | Path) -> int:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            p.write_text("", encoding="utf-8")
            return 0
        data = self.path.read_text(encoding="utf-8")
        p.write_text(data, encoding="utf-8")
        return sum(1 for _ in data.splitlines() if _.strip())

