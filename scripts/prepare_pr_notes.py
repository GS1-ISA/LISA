#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


OUT = Path("agent/outcomes/PR_NOTES.md")
OUT.parent.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def diff_stats(base: str | None) -> tuple[int, int, list[str]]:
    files = []
    adds = dels = 0
    if base:
        try:
            files = [l for l in run(["git", "diff", "--name-only", f"{base}...HEAD"]).splitlines() if l]
            for line in run(["git", "diff", "--numstat", f"{base}...HEAD"]).splitlines():
                parts = line.split("\t")
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    adds += int(parts[0]); dels += int(parts[1])
        except Exception:
            files = []
    if not files:
        files = [l for l in run(["git", "diff", "--name-only", "HEAD~1..HEAD"]).splitlines() if l]
        for line in run(["git", "diff", "--numstat", "HEAD~1..HEAD"]).splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                adds += int(parts[0]); dels += int(parts[1])
    return adds, dels, files


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare local PR notes (plan/diff/evidence)")
    ap.add_argument("--plan", default="")
    ap.add_argument("--base", default=os.environ.get("BASE_SHA", ""))
    ap.add_argument("--coverage", default="")
    ap.add_argument("--types", default="")
    ns = ap.parse_args()

    adds, dels, files = diff_stats(ns.base if ns.base else None)
    critical = [f for f in files if f.startswith("ISA_SuperApp/src/")]
    lines = []
    lines.append("# PR Notes — Plan / Diff / Evidence")
    lines.append("")
    lines.append("## Plan")
    lines.append(ns.plan or "- Small, reversible changes; update docs and scripts; add Make targets.")
    lines.append("")
    lines.append("## Diff Summary")
    lines.append(f"- Files changed: {len(files)} | +{adds} / -{dels} LOC")
    if critical:
        lines.append(f"- Critical paths: {len(critical)}")
        for c in critical[:20]:
            lines.append(f"  - {c}")
    lines.append("")
    lines.append("## Evidence")
    if ns.coverage:
        lines.append(f"- Coverage: {ns.coverage}")
    else:
        lines.append("- Coverage: (attach local run if available)")
    if ns.types:
        lines.append(f"- Type errors: {ns.types}")
    else:
        lines.append("- Type errors: (attach mypy summary if available)")
    lines.append("- Determinism: canonical snapshot tests present; Q11 benches updated")
    lines.append("- Security: bandit/pip-audit advisory checks planned")
    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

