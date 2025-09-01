#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path


def slugify(path: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-")
    return s.lower()


def classify(text: str, source: str) -> tuple[str, str]:
    t = text.lower()
    # Severity
    if any(k in t for k in ["must", "shall", "enforced", "never", "prohibited", "kill-switch"]):
        sev = "High"
    elif any(k in t for k in ["should", "acceptance:", "gate", "waiver", "break-glass"]):
        sev = "Medium"
    else:
        sev = "Low"
    # Category
    if any(k in source for k in ["QUALITY_GATES", "CI_WORKFLOWS"]) or "ci" in t or "gate" in t:
        cat = "CI/CD"
    elif any(k in source for k in ["AGENTIC_ARCHITECTURE", "ADR/0002"]) or "agent" in t:
        cat = "Agentic"
    elif any(k in source for k in ["SECURITY", "ADR/"]) or any(
        k in t for k in ["secret", "security", "sbom", "bandit", "trivy", "pip-audit"]
    ):
        cat = "Security"
    elif any(k in t for k in ["coverage", "test", "lint", "type", "determinism", "snapshot"]):
        cat = "Quality"
    elif any(k in t for k in ["prometheus", "metrics", "slo", "logging", "observability"]):
        cat = "Observability"
    elif any(k in t for k in ["data", "schema", "lineage", "privacy", "dpia"]):
        cat = "Data"
    elif any(k in t for k in ["doc", "readme", "adr"]):
        cat = "Docs"
    else:
        cat = "Process"
    return sev, cat


def main() -> int:
    root = Path.cwd()
    rules_csv = root / "docs" / "audit" / "rules_extracted.csv"
    out_csv = root / "docs" / "audit" / "rule_catalog.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with (
        rules_csv.open("r", encoding="utf-8") as f_in,
        out_csv.open("w", newline="", encoding="utf-8") as f_out,
    ):
        r = csv.DictReader(f_in)
        w = csv.writer(f_out)
        w.writerow(["RuleID", "Title", "Severity", "Category", "SourceFile", "Line"])
        for row in r:
            source = row["source_file"]
            line = int(row["line"]) if row["line"].isdigit() else row["line"]
            text = row["text"].strip()
            # Deterministic RuleID: R-<short hash of source:line:text>
            h = hashlib.sha256(f"{source}:{line}:{text}".encode("utf-8")).hexdigest()[:12]
            rule_id = f"R-{h}"
            title = text[:80]
            sev, cat = classify(text, source)
            w.writerow([rule_id, title, sev, cat, source, line])
    print(f"Wrote {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
