#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

STD_MAP = {
    "Security": ["OWASP ASVS", "OpenSSF Scorecard", "SLSA"],
    "CI/CD": ["12-Factor: Build/Release/Run", "DORA Metrics"],
    "Observability": ["Google SRE: Golden Signals", "Prometheus Best Practices"],
    "Quality": ["Testing Pyramid", "Deterministic Builds"],
    "Data": ["GDPR/DPIA", "Data Lineage (OpenLineage)"],
    "Docs": ["Docs-as-code"],
    "Agentic": ["NIST AI RMF", "Safe Autonomy Policies"],
    "Process": ["Lean/Agile"],
}


def infer_deviation(title: str) -> tuple[str, str]:
    t = title.lower()
    if any(k in t for k in ["waiver", "break-glass", "exception"]):
        return ("Yes", "Policy allows exceptions via waiver/break-glass")
    return ("No", "")


def main() -> int:
    root = Path.cwd()
    catalog = root / "docs" / "audit" / "rule_catalog.csv"
    out = root / "docs" / "audit" / "standards_alignment.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with (
        catalog.open("r", encoding="utf-8") as f_in,
        out.open("w", newline="", encoding="utf-8") as f_out,
    ):
        r = csv.DictReader(f_in)
        w = csv.writer(f_out)
        w.writerow(
            [
                "RuleID",
                "Category",
                "Standards",
                "Deviation",
                "Justification",
                "SourceFile",
                "Line",
                "Title",
            ]
        )
        for row in r:
            rid = row["RuleID"]
            cat = row["Category"] or "Process"
            title = row["Title"]
            stds = ";".join(STD_MAP.get(cat, ["Lean/Agile"]))
            dev, why = infer_deviation(title)
            w.writerow(
                [rid, cat, stds, dev, why, row["SourceFile"], row["Line"], title]
            )
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
