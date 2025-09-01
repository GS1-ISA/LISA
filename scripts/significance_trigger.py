#!/usr/bin/env python3
"""Detects whether a PR change is significant enough to run deep checks.

Signals (any true => significant):
- Files changed > threshold_files (default 25)
- LOC delta (adds+deletes) > threshold_loc (default 800)
- Critical path touched (prefix match on provided --critical dirs/files)

Outputs:
- Writes `significant=true|false` and a `reason=...` line to $GITHUB_OUTPUT
"""

from __future__ import annotations

import argparse
import os
import subprocess


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def diff_files(base: str) -> list[str]:
    out = run(["git", "diff", "--name-only", f"{base}...HEAD"]) or ""
    return [line for line in out.splitlines() if line.strip()]


def diff_loc(base: str) -> int:
    out = run(["git", "diff", "--numstat", f"{base}...HEAD"]) or ""
    total = 0
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            total += int(parts[0]) + int(parts[1])
    return total


def touched_critical(changed: list[str], critical: list[str]) -> tuple[bool, str]:
    for f in changed:
        for c in critical:
            if f.startswith(c):
                return True, f
    return False, ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Base commit/branch/sha to diff against")
    ap.add_argument("--threshold-files", type=int, default=25)
    ap.add_argument("--threshold-loc", type=int, default=800)
    ap.add_argument("--critical", action="append", default=[], help="Critical prefixes to watch")
    args = ap.parse_args()

    files = diff_files(args.base)
    loc = diff_loc(args.base)
    crit, hit = touched_critical(files, args.critical)

    significant = len(files) > args.threshold_files or loc > args.threshold_loc or crit
    reason_parts = []
    if len(files) > args.threshold_files:
        reason_parts.append(f"files>{args.threshold_files} ({len(files)})")
    if loc > args.threshold_loc:
        reason_parts.append(f"loc>{args.threshold_loc} ({loc})")
    if crit:
        reason_parts.append(f"critical:{hit}")
    reason = ", ".join(reason_parts) if reason_parts else "none"

    print(f"significant={significant} reason={reason}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"significant={'true' if significant else 'false'}\n")
            f.write(f"reason={reason}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
