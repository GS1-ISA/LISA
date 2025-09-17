#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

OUT_DIR = Path("agent/outcomes")
OUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Outcome:
    ts: float
    task: str
    strategy: str
    status: str  # success|fail
    coverage_delta: float | None = None
    type_errors: int | None = None
    duration_sec: float | None = None
    notes: str = ""


def log_outcome(o: Outcome) -> Path:
    ts_id = time.strftime("%Y%m%d-%H%M%S", time.gmtime(o.ts))
    path = OUT_DIR / f"{ts_id}_{o.task.replace(' ', '_')}.jsonl"
    rec = asdict(o)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return path


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Log an agent task outcome")
    ap.add_argument("--task", required=True)
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--status", required=True, choices=["success", "fail"])
    ap.add_argument("--coverage-delta", type=float)
    ap.add_argument("--type-errors", type=int)
    ap.add_argument("--duration-sec", type=float)
    ap.add_argument("--notes", default="")
    return ap.parse_args()


def main() -> int:
    ns = parse_args()
    o = Outcome(
        ts=time.time(),
        task=ns.task,
        strategy=ns.strategy,
        status=ns.status,
        coverage_delta=ns.coverage_delta,
        type_errors=ns.type_errors,
        duration_sec=ns.duration_sec,
        notes=ns.notes,
    )
    p = log_outcome(o)
    print(f"logged -> {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
