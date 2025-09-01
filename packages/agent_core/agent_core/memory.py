import json
from pathlib import Path
from typing import Any


class TraceLogger:
    """Appends JSONL events to a trace file (skeleton)."""

    def __init__(self, path: str = ".agent_traces.jsonl"):
        self.path = Path(path)

    def append(self, event: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
