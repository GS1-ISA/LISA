#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path


class Evidence:
    def __init__(self, file: Path, line: int, text: str):
        self.file = file
        self.line = line
        self.text = text.strip()


def grep_first(path: Path, pattern: re.Pattern[str]) -> Evidence | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return None
    for i, line in enumerate(lines, start=1):
        if pattern.search(line):
            return Evidence(path, i, line)
    return None


def search_paths(globs: list[str]) -> list[Path]:
    out: list[Path] = []
    for g in globs:
        out.extend(Path.cwd().glob(g))
    return out


def find_evidence(rule_text: str, source_file: str) -> tuple[str, Evidence | None]:
    t = rule_text.lower()
    # Lint (ruff)
    if "ruff" in t or ("lint" in t and "ruff" in source_file.lower()):
        for p in search_paths([".github/workflows/ci.yml", ".pre-commit-config.yaml", "pyproject.toml"]):
            ev = grep_first(p, re.compile(r"ruff"))
            if ev:
                return "PASS", ev
    # Typecheck (mypy)
    if "mypy" in t or ("typecheck" in t or "typing" in t):
        for p in search_paths([".github/workflows/ci.yml", ".pre-commit-config.yaml", "pyproject.toml"]):
            ev = grep_first(p, re.compile(r"mypy"))
            if ev:
                return "PASS", ev
    # Tests (pytest)
    if "test" in t or "coverage" in t:
        for p in search_paths([".github/workflows/ci.yml", "ISA_SuperApp/tests/**"]):
            ev = grep_first(p, re.compile(r"pytest|tests"))
            if ev:
                return "PASS", ev
    # Determinism / snapshots
    if "determinism" in t or "snapshot" in t or "canonical" in t:
        for p in search_paths(["ISA_SuperApp/src/utils/json_canonical.py", "ISA_SuperApp/tests/unit/test_snapshot_canonical_sample.py"]):
            if p.exists():
                ev = grep_first(p, re.compile(r"canonical|snapshot|sorted"))
                if ev:
                    return "PASS", ev
    # Prometheus / metrics
    if "prometheus" in t or "metrics" in t:
        p = Path("ISA_SuperApp/src/api_server.py")
        if p.exists():
            ev = grep_first(p, re.compile(r"/metrics|prometheus_client"))
            if ev:
                return "PASS", ev
    # Docker healthcheck / non-root
    if "docker" in t or "healthcheck" in t:
        p = Path("ISA_SuperApp/Dockerfile")
        if p.exists():
            ev = grep_first(p, re.compile(r"HEALTHCHECK|USER app|EXPOSE"))
            if ev:
                return "PASS", ev
    # Security scans: bandit, pip-audit, trivy, gitleaks, sbom
    if any(k in t for k in ["bandit", "pip-audit", "gitleaks", "trivy", "sbom", "syft", "secrets"]):
        for p in search_paths([".github/workflows/ci.yml", ".github/workflows/weekly.yml"]):
            ev = grep_first(p, re.compile(r"bandit|pip-audit|gitleaks|trivy|sbom|syft"))
            if ev:
                return "PASS", ev
    # Semgrep / static analysis
    if "semgrep" in t or "static" in t:
        p = Path(".github/workflows/ci.yml")
        if p.exists():
            ev = grep_first(p, re.compile(r"semgrep"))
            if ev:
                return "PASS", ev
    # Significance trigger / deep checks
    if "significance" in t or "deep checks" in t or "on-demand" in t:
        p = Path(".github/workflows/ci.yml")
        if p.exists():
            ev = grep_first(p, re.compile(r"significance_trigger|Deep checks"))
            if ev:
                return "PASS", ev
    # Kill-switch (policy) — doc-only for now
    if "kill-switch" in t:
        return "WARN", None
    # Break-glass / waiver — doc-only, WARN
    if "break-glass" in t or "waiver" in t:
        return "WARN", None
    return "FAIL", None


def main() -> int:
    root = Path.cwd()
    catalog = root / "docs" / "audit" / "rule_catalog.csv"
    out = root / "docs" / "audit" / "traceability_matrix.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with catalog.open("r", encoding="utf-8") as f_in, out.open("w", newline="", encoding="utf-8") as f_out:
        r = csv.DictReader(f_in)
        w = csv.writer(f_out)
        w.writerow(["RuleID", "SourceFile", "Line", "Artefact", "Status", "Evidence"])
        for row in r:
            rule_id = row["RuleID"]
            source = row["SourceFile"]
            line = row["Line"]
            text = row["Title"]
            status, ev = find_evidence(text, source)
            if ev:
                snippet = ev.text[:200].replace("\n", " ")
                w.writerow([rule_id, source, line, str(ev.file), status, f"{ev.line}: {snippet}"])
            else:
                w.writerow([rule_id, source, line, "", status, ""])
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
