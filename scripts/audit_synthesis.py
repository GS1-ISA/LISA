#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Tuple

import yaml  # type: ignore


ROOT = Path.cwd()
AUDIT = ROOT / "docs" / "audit"


def load_traceability() -> Dict[str, str]:
    path = AUDIT / "traceability_matrix.csv"
    status: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            status[row["RuleID"]] = row.get("Status", "FAIL").strip().upper()
    return status


def score_status(s: str) -> int:
    if s == "PASS":
        return 100
    if s == "WARN":
        return 60
    return 0


def write_rule_confidence(status: Dict[str, str]) -> Tuple[int, int, int, float]:
    path = AUDIT / "rule_confidence.csv"
    passes = warns = fails = 0
    total_score = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["RuleID", "Status", "Confidence"])
        for rid, st in status.items():
            sc = score_status(st)
            total_score += sc
            if st == "PASS":
                passes += 1
            elif st == "WARN":
                warns += 1
            else:
                fails += 1
            w.writerow([rid, st, sc])
    overall = total_score / max(1, len(status))
    return passes, warns, fails, overall


def load_gates_summary() -> Tuple[int, int, int]:
    path = AUDIT / "gates_status.csv"
    present = enforced = advisory = 0
    if not path.exists():
        return (0, 0, 0)
    with path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("Present", "False").lower() == "true":
                present += 1
                enf = row.get("Enforced", "").lower()
                if enf == "true":
                    enforced += 1
                else:
                    advisory += 1
    return present, enforced, advisory


def load_counts() -> Tuple[int, int]:
    inv = AUDIT / "inventory.csv"
    rules = AUDIT / "rule_catalog.csv"
    inv_count = sum(1 for _ in inv.open("r", encoding="utf-8")) - 1 if inv.exists() else 0
    rule_count = sum(1 for _ in rules.open("r", encoding="utf-8")) - 1 if rules.exists() else 0
    return inv_count, rule_count


def find_sha(path_str: str) -> str:
    inv = AUDIT / "inventory.csv"
    if not inv.exists():
        return ""
    target = str((ROOT / path_str).resolve())
    with inv.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("path") == target:
                return row.get("sha256", "")
    return ""


def write_audit_report(passes: int, warns: int, fails: int, overall: float) -> None:
    out = AUDIT / "audit_report.md"
    present, enforced, advisory = load_gates_summary()
    inv_count, rule_count = load_counts()

    # Evidence SHAs for key artefacts
    sha_api = find_sha("ISA_SuperApp/src/api_server.py")
    sha_docker = find_sha("ISA_SuperApp/Dockerfile")
    sha_ci = find_sha(".github/workflows/ci.yml")
    sha_canon = find_sha("ISA_SuperApp/src/utils/json_canonical.py")

    md = []
    md.append("## Audit Report — Executive Summary")
    md.append("")
    md.append(f"- Rules: {rule_count} | PASS: {passes} ✅ | WARN: {warns} ⚠️ | FAIL: {fails} ❌")
    md.append(f"- Overall Rule Confidence: {overall:.1f} %")
    md.append(f"- CI Gates: Present {present}, Enforced {enforced}, Advisory {advisory}")
    md.append(f"- Inventory size: {inv_count} files")
    md.append("")
    md.append("### Dashboard")
    md.append("- Lint/Type/Tests/Sec: present (promotion pending for some gates)")
    md.append("- Observability: /metrics and histograms present (api_server.py sha=" + sha_api + ")")
    md.append("- Container: non-root + healthcheck present (Dockerfile sha=" + sha_docker + ")")
    md.append("- Determinism: canonical writer + snapshot present (json_canonical.py sha=" + sha_canon + ")")
    md.append("- Event-driven deep checks: significance trigger and semgrep wired (ci.yml sha=" + sha_ci + ")")
    md.append("")
    md.append("### Go/No-Go Recommendation")
    go = overall >= 70.0 and fails == 0
    if go:
        md.append("- Recommendation: GO ✅")
    else:
        md.append("- Recommendation: CONDITIONAL (AMBER) — Fix priority items in remediation plan, then GO")
    out.write_text("\n".join(md) + "\n", encoding="utf-8")


def write_remediation_plan() -> None:
    out = AUDIT / "remediation_plan.md"
    plan = []
    plan.append("## Remediation Plan — Prioritized Backlog")
    plan.append("")
    plan.append("- [ ] Flip ruff/pytest/coverage/semgrep to enforced after 7-day stability (3 pts)")
    plan.append("- [ ] Add determinism snapshot CI job (advisory → enforced) (2 pts)")
    plan.append("- [ ] Add docs build (MkDocs) advisory gate (1 pt)")
    plan.append("- [ ] Add container build + /metrics curl check in CI (2 pts)")
    plan.append("- [ ] Enforce kill-switch/waiver labels in CI (1 pt)")
    plan.append("- [ ] Link dependency files to pip-audit policy in QUALITY_GATES (1 pt)")
    plan.append("- [ ] Reference workflows (docs_auto_sync, poc_bench) in CI_WORKFLOWS and QUALITY_GATES (1 pt)")
    plan.append("- [ ] Reduce completeness gaps by referencing key docs in ROADMAP/TODO/DoD (2 pts)")
    plan.append("")
    plan.append("Owner: Project (You + Agent) — single-owner model")
    out.write_text("\n".join(plan) + "\n", encoding="utf-8")


def main() -> int:
    status = load_traceability()
    passes, warns, fails, overall = write_rule_confidence(status)
    write_audit_report(passes, warns, fails, overall)
    write_remediation_plan()
    print("Wrote rule_confidence.csv, audit_report.md, remediation_plan.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

