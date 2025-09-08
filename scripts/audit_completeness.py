#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

NORMATIVE_GLOBS = [
    "**/*.py",
    "**/*.md",
    "**/*.yml",
    "**/*.yaml",
    "**/*.ini",
    "**/*.toml",
    "**/Dockerfile",
    "**/docker-compose.yml",
    "**/requirements*.txt",
    "**/Makefile",
    ".github/workflows/*.yml",
]

EXCLUDE_DIRS = {".git", "node_modules", ".venv", "__pycache__", "context7-master"}


def is_normative(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    for g in NORMATIVE_GLOBS:
        if path.match(g):
            return True
    return False


def load_traceability(p: Path) -> dict[str, list[str]]:
    """Map artefact path -> list of RuleIDs that reference it (any status)."""
    inv: dict[str, list[str]] = {}
    with p.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            artefact = row.get("Artefact", "").strip()
            rule_id = row.get("RuleID", "").strip()
            if artefact:
                inv.setdefault(artefact, []).append(rule_id)
    return inv


def main() -> int:
    root = Path.cwd()
    inv_csv = root / "docs" / "audit" / "inventory.csv"
    trace_csv = root / "docs" / "audit" / "traceability_matrix.csv"
    out_dir = root / "docs" / "audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    inverse_csv = out_dir / "inverse_index.csv"
    gaps_yaml = out_dir / "completeness_gap.yaml"

    trace = load_traceability(trace_csv)
    # Build list of normative artefacts from inventory
    governed: dict[str, list[str]] = {}
    entries: list[tuple[str, int, str]] = []
    with inv_csv.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            path = row["path"].strip()
            p = Path(path)
            try:
                rel = str(p.relative_to(root))
            except Exception:
                rel = path
            pp = Path(rel)
            if not is_normative(pp):
                continue
            governed[rel] = trace.get(path, []) or trace.get(rel, []) or []
            size = int(row.get("size_bytes", "0") or 0)
            entries.append((rel, size, row.get("sha256", "")))

    # Write inverse index
    with inverse_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["artefact", "rule_ids"])
        for artefact, rules in sorted(governed.items()):
            w.writerow([artefact, ";".join(rules)])

    # Compute gaps
    suggestions = []
    for artefact, rules in governed.items():
        if rules:
            continue
        a = artefact
        if a.endswith("Dockerfile") or a.endswith("docker-compose.yml"):
            reason = "Container artefact without explicit governing rule"
            sugg = "Add doc rule in ROADMAP/QUALITY_GATES and CI step verifying build/healthcheck"
        elif a.startswith(".github/workflows/"):
            reason = "Workflow not linked to governance"
            sugg = "Reference in QUALITY_GATES.md and ensure promotion rules cover it"
        elif a.endswith(".py") and "/tests/" not in a:
            reason = "Source module lacks explicit rule linkage"
            sugg = "Add DoD/QUALITY rule referencing tests/type/lint for this module"
        elif "/tests/" in a:
            reason = "Test file not linked"
            sugg = "Ensure test suite is referenced by coverage gate and DoD"
        elif a.endswith(".md"):
            reason = "Doc not governed"
            sugg = "Link in ROADMAP/TODO or ADRs; add DoD clause for keeping updated"
        elif a.endswith("requirements.txt") or a.endswith("requirements-dev.txt"):
            reason = "Dependency file not governed"
            sugg = "Add rule for pip-audit and constraints policy"
        else:
            reason = "Artefact not linked to any rule"
            sugg = "Add appropriate governance in docs and CI"
        suggestions.append({"path": artefact, "reason": reason, "suggestion": sugg})

    # Write YAML
    import yaml

    with gaps_yaml.open("w", encoding="utf-8") as f:
        yaml.safe_dump({"gaps": suggestions}, f, sort_keys=False)

    print(f"Wrote {inverse_csv} and {gaps_yaml} (gaps={len(suggestions)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
