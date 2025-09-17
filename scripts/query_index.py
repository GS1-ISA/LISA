#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

INDEX_PATH = Path("docs/audit/search_index.jsonl")


@dataclass
class Record:
    path: str
    rel: str
    ext: str
    size: int
    mtime: str
    title: str = ""
    preview: str = ""
    headings: list[str] | None = None


def load_index(index_path: Path) -> Iterable[Record]:
    if not index_path.exists():
        print(
            f"Index not found: {index_path}. Run `make index` first.", file=sys.stderr
        )
        sys.exit(2)
    with index_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            yield Record(
                path=obj.get("path", ""),
                rel=obj.get("rel", ""),
                ext=obj.get("ext", ""),
                size=int(obj.get("size", 0)),
                mtime=obj.get("mtime", ""),
                title=obj.get("title", ""),
                preview=obj.get("preview", ""),
                headings=obj.get("headings"),
            )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Query the repository search index (JSONL)"
    )
    ap.add_argument("query", nargs="?", default="", help="free-text query")
    ap.add_argument(
        "--index", default=str(INDEX_PATH), help="path to search_index.jsonl"
    )
    ap.add_argument("--md", action="store_true", help="limit to Markdown files")
    ap.add_argument(
        "--code", action="store_true", help="limit to common code extensions"
    )
    ap.add_argument(
        "--path-substr", default="", help="substring to match in relative path"
    )
    ap.add_argument("--title", default="", help="substring to match in title")
    ap.add_argument("--heading", default="", help="substring to match in headings")
    ap.add_argument(
        "--contains", default="", help="substring to match in markdown preview text"
    )
    ap.add_argument(
        "--since",
        default="",
        help="ISO date/time; only show mtime >= this (e.g., 2025-09-01)",
    )
    ap.add_argument("--top", type=int, default=20, help="max results to show")
    return ap.parse_args()


CODE_EXTS = {
    ".py",
    ".ts",
    ".js",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cpp",
    ".yml",
    ".yaml",
    ".toml",
}


def score_record(
    r: Record, q: str, title_q: str, heading_q: str, contains_q: str
) -> int:
    ql = q.lower()
    s = 0
    if ql:
        if ql in r.rel.lower():
            s += 5
        if ql in r.title.lower():
            s += 8
        if r.headings and any(ql in h.lower() for h in r.headings):
            s += 6
        if r.preview and ql in r.preview.lower():
            s += 3
    if title_q and title_q.lower() in r.title.lower():
        s += 5
    if (
        heading_q
        and r.headings
        and any(heading_q.lower() in h.lower() for h in r.headings)
    ):
        s += 4
    if contains_q and r.preview and contains_q.lower() in r.preview.lower():
        s += 2
    return s


def main() -> int:
    ns = parse_args()
    try:
        since_dt = datetime.fromisoformat(ns.since) if ns.since else None
    except Exception:
        print("Invalid --since value; expected ISO date/time", file=sys.stderr)
        return 2

    idx_path = Path(ns.index)
    rows = list(load_index(idx_path))

    def passes_filters(r: Record) -> bool:
        if ns.md and r.ext != ".md":
            return False
        if ns.code and r.ext not in CODE_EXTS:
            return False
        if ns.path_substr and ns.path_substr.lower() not in r.rel.lower():
            return False
        if ns.title and ns.title.lower() not in r.title.lower():
            return False
        if ns.heading and (
            not r.headings
            or not any(ns.heading.lower() in h.lower() for h in r.headings)
        ):
            return False
        if (
            ns.contains
            and ns.ext == ".md"
            and ns.contains.lower() not in (r.preview or "").lower()
        ):
            return False
        if since_dt:
            try:
                mt = datetime.fromisoformat(r.mtime)
                if mt < since_dt:
                    return False
            except Exception:
                pass
        return True

    filtered = [r for r in rows if passes_filters(r)]
    # Rank
    ranked = sorted(
        filtered,
        key=lambda r: (
            score_record(r, ns.query, ns.title, ns.heading, ns.contains),
            r.ext == ".md",
        ),
        reverse=True,
    )

    n = 0
    for r in ranked:
        print(f"{r.rel} | {r.title or '(no title)'} | {r.ext} | {r.size}B | {r.mtime}")
        if r.headings:
            print(f"  headings: {', '.join(r.headings[:5])}")
        if r.ext == ".md" and r.preview:
            prev = r.preview.replace("\n", " ")
            print(f"  preview: {prev[:200]}")
        n += 1
        if n >= ns.top:
            break

    if n == 0:
        print("No results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
