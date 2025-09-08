#!/usr/bin/env python3
"""Auto-update markdown docs with a Last updated timestamp.

Scans *.md under repo (including docs/) and adds/refreshes a 'Last updated: YYYY-MM-DD'
line near the top if present or inserts after the title line if missing.

Designed to be run in CI to create an automated PR with doc updates.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "__pycache__",
    "ISA_SuperApp/webui",
    "ISA_SuperApp/__MACOSX",
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    today = dt.date.today().isoformat()
    updated_line = f"Last updated: {today}"
    lines = text.splitlines()

    # Find existing 'Last updated' line
    idx = None
    for i, line in enumerate(lines[:10]):
        if line.strip().lower().startswith("last updated:"):
            idx = i
            break

    changed = False
    if idx is not None:
        if lines[idx] != updated_line:
            lines[idx] = updated_line
            changed = True
    else:
        # Insert after first title line (starts with Title: or # ) if found, else at top
        insert_at = 0
        for i, line in enumerate(lines[:5]):
            if line.startswith("Title:") or line.startswith("# "):
                insert_at = i + 1
                break
        lines.insert(insert_at, updated_line)
        changed = True

    if changed:
        path.write_text(
            "\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8"
        )
    return changed


def main() -> int:
    root = Path.cwd()
    changed_any = False
    for p in root.rglob("*.md"):
        if should_skip(p):
            continue
        try:
            if process_file(p):
                changed_any = True
        except Exception:
            # Don't fail CI for doc update issues; continue best-effort
            continue
    return 0 if changed_any else 0


if __name__ == "__main__":
    raise SystemExit(main())
