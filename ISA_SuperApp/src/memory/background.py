from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from .logs import MemoryEventLogger
from ..memory import KnowledgeGraphMemory


class NapTimeLearner:
    """Summarize recent events into long-term memory after idle periods.

    Idle is defined by ISA_SLEEPTIME_MINUTES (default 30). Caller is responsible for scheduling.
    """

    def __init__(self, log_dir: str | Path | None = None) -> None:
        self.logger = MemoryEventLogger(log_dir)
        self._state_file = Path(log_dir or Path("agent") / "memory") / "nap_state.txt"

    def _last_run(self) -> Optional[datetime]:
        if not self._state_file.exists():
            return None
        try:
            ts = self._state_file.read_text(encoding="utf-8").strip()
            return datetime.fromisoformat(ts)
        except Exception:
            return None

    def _mark_run(self, dt: datetime) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(dt.isoformat(), encoding="utf-8")

    def run_once(self) -> int:
        idle_min = int(os.getenv("ISA_SLEEPTIME_MINUTES", "30"))
        now = datetime.now(timezone.utc)
        last = self._last_run()
        if last and now - last < timedelta(minutes=idle_min):
            return 0

        path = self.logger.path
        if not path.exists():
            self._mark_run(now)
            return 0
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        # Simple summary: collect recent content fields
        import json

        contents = []
        for l in lines[-100:]:
            try:
                contents.append(json.loads(l).get("content", ""))
            except Exception:
                pass
        if not contents:
            self._mark_run(now)
            return 0

        summary = " ".join(contents[:50])
        kg = KnowledgeGraphMemory()
        kg.create_entity("long_term_summary", "summary")
        kg.add_observations("long_term_summary", [summary[:1000]])
        self._mark_run(now)
        return len(contents)

