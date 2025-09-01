#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path.cwd()
DOCS = ROOT / "docs"
REPORT = DOCS / "audit" / "docs_ref_report.md"


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)(#[^)]+)?\)")


@dataclass
class Finding:
    path: Path
    kind: str
    detail: str


def md_files() -> Iterable[Path]:
    for p in DOCS.rglob("*.md"):
        yield p


def check_title(path: Path) -> list[Finding]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if not lines:
        return [Finding(path, "empty", "file is empty")]
    # Title is either 'Title:' or first level heading
    ok = False
    for line in lines[:5]:
        s = line.strip()
        if s.startswith("Title:") or s.startswith("# "):
            ok = True
            break
    return [] if ok else [Finding(path, "title", "missing Title: or top-level heading in first 5 lines")]


def check_links(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings: list[Finding] = []
    # Markdown links
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip()
        if target.startswith("http"):
            continue
        target_path = (path.parent / target).resolve()
        if not target_path.exists():
            findings.append(Finding(path, "link", f"broken link -> {target}"))
    # Refs: lines (simple heuristic 'Refs:' then comma/semicolon-separated paths)
    for line in text.splitlines():
        if line.strip().startswith("Refs:"):
            rest = line.split(":", 1)[1]
            for tok in re.split(r"[,;]", rest):
                cand = tok.strip()
                if not cand or cand.startswith("http"):
                    continue
                t = (ROOT / cand).resolve()
                if not t.exists():
                    findings.append(Finding(path, "ref", f"broken ref -> {cand}"))
    return findings


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    all_findings: list[Finding] = []
    for p in md_files():
        all_findings.extend(check_title(p))
        all_findings.extend(check_links(p))
    # Write report
    lines = ["# Docs Reference Report", ""]
    if not all_findings:
        lines.append("No issues found.")
    else:
        by_kind: dict[str, list[Finding]] = {}
        for f in all_findings:
            by_kind.setdefault(f.kind, []).append(f)
        for kind, items in sorted(by_kind.items()):
            lines.append(f"## {kind} — {len(items)}")
            for f in items:
                rel = f.path.relative_to(ROOT)
                lines.append(f"- {rel}: {f.detail}")
            lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

