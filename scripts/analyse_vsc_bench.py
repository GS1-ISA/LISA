#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def load(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def speedups(before: Dict, after: Dict) -> List[str]:
    rows = []
    bb = {e["command"]: e for e in before.get("results", [])}
    aa = {e["command"]: e for e in after.get("results", [])}
    for cmd, b in bb.items():
        a = aa.get(cmd)
        if not a:
            continue
        bmean = float(b.get("mean", 0))
        amean = float(a.get("mean", 0))
        if bmean <= 0 or amean <= 0:
            continue
        pct = (bmean - amean) / bmean * 100.0
        rows.append(
            f"- {cmd}: {pct:.1f}% speed-up (before {bmean:.3f}s → after {amean:.3f}s)"
        )
    return rows


def main() -> int:
    base = Path(".ai/cache/baseline.json")
    aft = Path(".ai/cache/after.json")
    out = Path(".ai/cache/vsc_optimisation_report.md")
    out.parent.mkdir(parents=True, exist_ok=True)

    if not base.exists() or not aft.exists():
        out.write_text(
            "Baseline or after JSON missing. Run hyperfine benchmarks first.",
            encoding="utf-8",
        )
        print(out)
        return 0

    before = load(base)
    after = load(aft)
    rows = speedups(before, after)
    report = ["# VS Code Optimisation Report", "", "## Speed-ups"]
    report.extend(rows or ["- No comparable commands found."])
    report.extend(
        [
            "",
            "## Token Saved",
            "- N/A (use extension metrics if available)",
            "",
            "## CPU mWh Delta",
            "- N/A (see .ai/cache/terminal_telemetry.csv)",
            "",
            "## Next Hypothesis",
            "- Reduce test scope on save; run targeted paths only.",
        ]
    )
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
