#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

OUT_DIR = Path("agent/outcomes")


def iter_records() -> Iterable[dict]:
    if not OUT_DIR.exists():
        return []
    for p in sorted(OUT_DIR.glob("*.jsonl")):
        try:
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        yield json.loads(line)
                    except Exception:
                        continue
        except Exception:
            continue


def main() -> int:
    ap = argparse.ArgumentParser(description="Suggest past fixes from outcomes logs")
    ap.add_argument(
        "--query", required=True, help="substring to search in task names or notes"
    )
    ap.add_argument("--top", type=int, default=10)
    ns = ap.parse_args()

    q = ns.query.lower()
    hits: list[dict] = []
    for rec in iter_records():
        text = (rec.get("task", "") + " " + rec.get("notes", "")).lower()
        if q in text:
            hits.append(rec)
    hits.sort(
        key=lambda r: (r.get("status") == "success", r.get("coverage_delta") or 0.0),
        reverse=True,
    )
    for r in hits[: ns.top]:
        print(
            f"- {r.get('task')} | strat={r.get('strategy')} | status={r.get('status')} "
            f"| covΔ={r.get('coverage_delta')} | type_errs={r.get('type_errors')} | notes={str(r.get('notes') or '')[:80]}"
        )
    if not hits:
        print("No suggestions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
