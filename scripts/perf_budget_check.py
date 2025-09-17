#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    path = Path(os.getenv("PERF_HIST_FILE", "perf_histogram.json"))
    if not path.exists():
        print(f"perf-budget: missing {path}")
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    p95_s = float(data.get("p95_s", 0.0))
    budget_ms = int(os.getenv("PERF_P95_MS", "400"))
    enforce = os.getenv("PERF_BUDGET_ENFORCE", "0") == "1"
    print(f"perf-budget: p95={p95_s*1000:.1f} ms budget={budget_ms} ms enforce={enforce}")
    if enforce and (p95_s * 1000.0 > budget_ms):
        print("::error::p95 latency exceeds budget")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

