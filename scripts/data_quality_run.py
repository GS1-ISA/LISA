#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SAMPLE = Path("docs/data_quality/sample.jsonl")
REPORT_JSON = Path("docs/audit/data_quality_report.json")
REPORT_MD = Path("docs/audit/data_quality_report.md")

@dataclass
class Violation:
    row: int
    field: str
    message: str

def load_samples() -> list[dict[str, Any]]:
    if not SAMPLE.exists():
        return []
    rows: list[dict[str, Any]] = []
    for i, line in enumerate(SAMPLE.read_text().splitlines(), 1):
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"__error__": f"invalid json at line {i}"})
    return rows

def validate(rows: list[dict[str, Any]]) -> list[Violation]:
    v: list[Violation] = []
    for idx, r in enumerate(rows, 1):
        # required fields
        for f in ("id", "name", "price"):
            if f not in r:
                v.append(Violation(idx, f, "missing"))
        # types and ranges
        if isinstance(r.get("price"), (int, float)):
            if r["price"] < 0:
                v.append(Violation(idx, "price", "negative"))
        else:
            if "price" in r:
                v.append(Violation(idx, "price", "not a number"))
        # name non-empty
        if "name" in r and (not isinstance(r["name"], str) or not r["name"].strip()):
            v.append(Violation(idx, "name", "empty or not string"))
    return v

def main() -> int:
    rows = load_samples()
    violations = validate(rows)
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps([vi.__dict__ for vi in violations], indent=2), encoding="utf-8"
    )
    # Markdown summary
    md = ["# Data Quality Report", ""]
    md.append(f"Rows: {len(rows)} | Violations: {len(violations)}")
    md.append("")
    for vi in violations[:200]:
        md.append(f"- row {vi.row} | {vi.field}: {vi.message}")
    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_JSON} and {REPORT_MD}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
