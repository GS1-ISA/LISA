#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


DISALLOWED = re.compile(r"^\s*from\s+src\.agent_core\.|^\s*import\s+src\.agent_core\.")
ALLOWLIST = {
    ROOT / "src" / "orchestrator" / "src" / "orchestrator" / "agent_core_adapter.py",
}


def main() -> int:
    violations = []
    for base in (ROOT / "src" / "orchestrator", ROOT / "src" / "llm"):
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            if p in ALLOWLIST:
                continue
            try:
                for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                    if DISALLOWED.search(line):
                        violations.append(
                            f"{p.relative_to(ROOT)}:{i}: disallowed direct import of agent_core"
                        )
            except Exception:
                continue
    if violations:
        print("\n".join(violations))
        return 1
    print("import-guard: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
