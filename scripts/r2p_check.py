#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


TOUCH_PATHS = (
    "src/agent_core/",
    "src/orchestrator/",
    "src/mapping/",
)


def git_diff_names(base: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", base, "HEAD"], cwd=str(ROOT)
        ).decode()
        return [l.strip() for l in out.splitlines() if l.strip()]
    except Exception:
        return []


def main() -> int:
    base = os.getenv("R2P_BASE", "origin/main")
    files = git_diff_names(base)
    if not files:
        print("::notice::r2p-check: no changed files detected vs base")
        return 0

    # Determine if adoption-relevant areas were touched
    touched = any(any(f.startswith(p) for p in TOUCH_PATHS) for f in files)
    if not touched:
        print("::notice::r2p-check: no adoption-relevant paths changed")
        return 0

    # Signals to look for
    has_adr = any(f.startswith("docs/ADR/") and f.endswith(".md") for f in files)
    tests_touched = any(
        f.startswith("src/agent_core/tests/") or f.startswith("src/orchestrator/tests/")
        for f in files
    )
    # Presence of flag or adapter usage in diff (best-effort grep)
    adapter_touched = any("agent_core_adapter" in f for f in files)

    ok = True
    if not has_adr:
        print("::warning::r2p-check: No ADR changes detected under docs/ADR for adoption-relevant changes")
        ok = False
    if not tests_touched:
        print("::warning::r2p-check: No tests updated under src/*/tests for adoption-relevant changes")
        ok = False
    if not adapter_touched:
        print("::notice::r2p-check: Adapter path not touched (may be fine if rules-only change)")

    # Advisory: never block for now; exit 0 regardless
    if ok:
        print("::notice::r2p-check: adoption checklist satisfied (ADR + tests present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

