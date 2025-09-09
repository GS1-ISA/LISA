#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from pathlib import Path


def run_once(goal: str) -> None:
    # Import inside to avoid startup overhead in arg parsing
    from orchestrator.graph import PlanToolReflect

    runner = PlanToolReflect()
    _ = runner.run(goal)


def percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    k = (len(data) - 1) * p
    f = int(k)
    c = min(f + 1, len(data) - 1)
    if f == c:
        return data[f]
    d0 = data[f] * (c - k)
    d1 = data[c] * (k - f)
    return d0 + d1


def main() -> int:
    ap = argparse.ArgumentParser(description="Emit latency histogram for a core path (advisory)")
    ap.add_argument("--runs", type=int, default=200, help="number of iterations")
    ap.add_argument("--goal", default="measure core path latency")
    ap.add_argument("--out", default="perf_histogram.json")
    ns = ap.parse_args()

    # Ensure stubbed, offline operation
    os.environ.setdefault("ADAPTER_STUB_MODE", "1")
    os.environ.setdefault("ORCHESTRATOR_USE_AGENT_CORE", "0")

    durs: list[float] = []
    for _ in range(max(1, ns.runs)):
        t0 = time.perf_counter()
        run_once(ns.goal)
        durs.append(time.perf_counter() - t0)

    durs.sort()
    result = {
        "runs": len(durs),
        "mean_s": statistics.mean(durs) if durs else 0.0,
        "median_s": statistics.median(durs) if durs else 0.0,
        "p95_s": percentile(durs, 0.95),
        "p99_s": percentile(durs, 0.99),
        "min_s": durs[0] if durs else 0.0,
        "max_s": durs[-1] if durs else 0.0,
        "buckets": {
            "<1ms": sum(1 for x in durs if x < 0.001),
            "1-5ms": sum(1 for x in durs if 0.001 <= x < 0.005),
            "5-20ms": sum(1 for x in durs if 0.005 <= x < 0.020),
            "20-50ms": sum(1 for x in durs if 0.020 <= x < 0.050),
            ">=50ms": sum(1 for x in durs if x >= 0.050),
        },
    }
    out = Path(ns.out)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

