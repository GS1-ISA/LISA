#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


OUT_DIR = Path("agent/outcomes")
REPORT = Path("docs/audit/agent_outcomes_summary.md")


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


def summarize() -> str:
    per_strategy: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    total = 0
    success = 0
    for rec in iter_records():
        strat = str(rec.get("strategy", "?"))
        status = str(rec.get("status", "fail"))
        per_strategy[strat]["count"] += 1
        if status == "success":
            per_strategy[strat]["success"] += 1
            success += 1
        total += 1
        if rec.get("coverage_delta") is not None:
            per_strategy[strat]["coverage_delta_sum"] += float(rec["coverage_delta"])
        if rec.get("type_errors") is not None:
            per_strategy[strat]["type_errors_sum"] += float(rec["type_errors"])

    lines = []
    lines.append("# Agent Outcomes Summary")
    lines.append("")
    lines.append(f"Total tasks: {total} | Success: {success} | Win-rate: { (success/total*100 if total else 0):.1f}%")
    lines.append("")
    lines.append("## By Strategy")
    for strat, m in sorted(per_strategy.items()):
        cnt = int(m.get("count", 0))
        succ = int(m.get("success", 0))
        wr = (succ / cnt * 100) if cnt else 0
        cov = m.get("coverage_delta_sum", 0.0)
        terr = m.get("type_errors_sum", 0.0)
        lines.append(f"- {strat}: {cnt} tasks | win-rate {wr:.1f}% | coverage Δ sum {cov:+.2f} | type errors sum {terr:.0f}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(summarize(), encoding="utf-8")
    print(f"wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

