#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ISA_SuperApp.src.memory.drift import compute_drift


def load_last_two_summaries(mem_file: Path) -> tuple[str, str] | None:
    if not mem_file.exists():
        return None
    try:
        lines = [json.loads(l) for l in mem_file.read_text(encoding="utf-8").splitlines() if l.strip()]
        summaries = [l for l in lines if l.get("kind") in ("store",) and "Q:" in l.get("content", "")]
        if len(summaries) < 2:
            return None
        return summaries[-2]["content"], summaries[-1]["content"]
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Memory coherence gate (advisory)")
    ap.add_argument("--log", default="agent/memory/memory_log.jsonl")
    ap.add_argument("--threshold", type=float, default=0.9)
    ns = ap.parse_args()
    p = Path(ns.log)
    pair = load_last_two_summaries(p)
    if not pair:
        print("memory-coherence: not enough data")
        return 0
    a, b = pair
    d = compute_drift(a, b)
    print(f"memory-coherence: drift={d:.3f} (threshold {ns.threshold:.3f})")
    # advisory only: print warning if drift too high
    if d > ns.threshold:
        print("WARNING: memory drift exceeded advisory threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

