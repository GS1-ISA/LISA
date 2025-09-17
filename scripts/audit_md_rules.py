#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "node_modules"}
NON_NORMATIVE = [
    "**/COPILOT_DEPLOY.prompt.md",
    "ISA_synthesized/**",
]

# Heuristics for extracting explicit rules/checks/behavioural statements
RULE_PATTERNS = [
    re.compile(
        r"\b(must|shall|required|enforced|prohibited|never|only)\b", re.IGNORECASE
    ),
    re.compile(r"^\s*- \[(?: |x)\] "),  # checkboxes
    re.compile(r"^\s*Acceptance:\s*$", re.IGNORECASE),
    re.compile(r"^\s*Gate[-\s]Flip|^\s*Kill[-\s]Switch|^\s*Waiver", re.IGNORECASE),
]


def iter_md_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        # Skip non-normative onboarding/checklist docs
        skip = False
        for pat in NON_NORMATIVE:
            if p.match(pat):
                skip = True
                break
        if skip:
            continue
        yield p


def extract_rules(path: Path) -> list[tuple[Path, int, str]]:
    rules: list[tuple[Path, int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return rules
    i = 0
    while i < len(lines):
        line = lines[i]
        matched = any(p.search(line) for p in RULE_PATTERNS)
        if matched:
            rules.append((path, i + 1, line.strip()))
            # If this is an Acceptance: line, capture following bullet lines until blank
            if re.match(r"^\s*Acceptance:\s*$", line, re.IGNORECASE):
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("-"):
                    rules.append((path, j + 1, lines[j].strip()))
                    j += 1
                i = j
                continue
        i += 1
    return rules


def main() -> int:
    root = Path.cwd()
    out_dir = root / "docs" / "audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "rules_extracted.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_file", "line", "text"])
        for md in iter_md_files(root):
            for path, line, text in extract_rules(md):
                w.writerow([str(path), line, text])
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
