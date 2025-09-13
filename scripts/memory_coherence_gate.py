#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def compute_drift(a: str, b: str) -> float:
    """Return a simple drift score in [0,1], higher = more drift.

    Uses Jaccard distance over lowercase word sets as a lightweight proxy.
    """
    wa = set(a.lower().split())
    wb = set(b.lower().split())
    if not wa and not wb:
        return 0.0
    inter = len(wa & wb)
    union = len(wa | wb)
    jaccard = inter / union if union else 1.0
    return 1.0 - jaccard


def load_last_two_summaries(mem_file: Path) -> tuple[str, str] | None:
    if not mem_file.exists():
        return None
    try:
        lines = [
            json.loads(line)
            for line in mem_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        summaries = [
            obj
            for obj in lines
            if obj.get("kind") in ("store",) and "Q:" in obj.get("content", "")
        ]
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
