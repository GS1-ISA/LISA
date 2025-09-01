from __future__ import annotations

import json
import os
import time
from typing import Any

STATE_PATH = ".autodev/state.json"


def load_state() -> dict[str, Any]:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"runs": 0, "done": [], "cost_eur": 0.0, "last_task": None}


def save_state(s: dict[str, Any]) -> None:
    os.makedirs(".autodev", exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)


def tick_cost(s: dict[str, Any], delta: float) -> None:
    s["cost_eur"] = round(s.get("cost_eur", 0.0) + delta, 4)
    s["runs"] = s.get("runs", 0) + 1
    s["ts"] = int(time.time())
