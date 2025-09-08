#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
IDX = ROOT / "docs" / "audit" / "search_index.jsonl"
OUT = ROOT / "docs" / "INDEX.md"


def load() -> list[dict]:
    rows: list[dict] = []
    if not IDX.exists():
        return rows
    with IDX.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("ext") == ".md" and obj.get("rel", "").startswith("docs/"):
                    rows.append(obj)
            except Exception:
                continue
    return rows


def main() -> int:
    rows = load()
    rows.sort(key=lambda r: str(r.get("title") or r.get("rel") or ""))
    lines: list[str] = []
    lines.append("# Documentation Index")
    lines.append("")
    lines.append(
        "This index is generated from the docs audit search index. Use it to quickly find key documents."
    )
    lines.append("")
    for r in rows:
        rel = r.get("rel", "")
        # links should be relative to docs/, so strip leading 'docs/' if present
        link = rel[5:] if rel.startswith("docs/") else rel
        title = r.get("title") or link
        lines.append(f"- [{title}]({link})")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
