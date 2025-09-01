#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml  # type: ignore


POLICY = Path(".agent/policy.yaml")


def error(msg: str) -> None:
    print(f"[policy-lint] ERROR: {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"[policy-lint] WARN: {msg}")


def main() -> int:
    if not POLICY.exists():
        warn("Policy file not found (skip)")
        return 0
    try:
        data = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    except Exception as e:
        error(f"Failed to parse YAML: {e}")
        return 1

    # Basic schema checks
    ok = True
    meta = data.get("meta", {})
    gates = data.get("gates", {})
    jobs: List[Dict[str, Any]] = data.get("jobs", []) or []

    if not isinstance(meta, dict) or "version" not in meta:
        error("meta.version missing")
        ok = False

    if not isinstance(gates, dict) or "promote_after_green_days" not in gates:
        error("gates.promote_after_green_days missing")
        ok = False

    seen_ids = set()
    for i, job in enumerate(jobs):
        jid = job.get("id")
        when = job.get("when", {})
        if not jid:
            error(f"jobs[{i}].id missing")
            ok = False
        elif jid in seen_ids:
            error(f"duplicate job id: {jid}")
            ok = False
        else:
            seen_ids.add(jid)
        if not isinstance(when, dict):
            error(f"jobs[{i}].when must be a mapping")
            ok = False

    print("[policy-lint] OK" if ok else "[policy-lint] FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
