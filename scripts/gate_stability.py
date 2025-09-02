#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

STATE = Path("docs/audit/gate_stability.json")

def load() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            return {}
    return {}

def save(data: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser(description="Update gate stability counters")
    ap.add_argument("--gate", required=True, help="gate id, e.g., tests, coverage, mypy, semgrep, determinism")
    ap.add_argument("--status", required=True, choices=["green", "red"])
    ap.add_argument("--window", type=int, default=7, help="days required for promotion")
    ns = ap.parse_args()

    data = load()
    g = data.get(ns.gate, {"green_days": 0, "window": ns.window, "promoted": False})
    if ns.status == "green":
        g["green_days"] = g.get("green_days", 0) + 1
    else:
        g["green_days"] = 0
    g["window"] = ns.window
    if g["green_days"] >= ns.window:
        g["promoted"] = True
    data[ns.gate] = g
    save(data)
    print(json.dumps({ns.gate: g}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
