#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import datetime as dt
from pathlib import Path
from typing import Iterable


ROOT = Path.cwd()
AUDIT_DIR = ROOT / "docs" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

EXCLUDE_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "__MACOSX",
    "temp_unzip",
}

EXCLUDE_PATH_PREFIXES = {
    str((ROOT / "ISA_SuperApp" / "webui" / "node_modules").resolve()),
}

MAX_HASH_SIZE = 100 * 1024 * 1024  # 100 MB safety cap for hashing


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIR_NAMES:
        return True
    ap = str(path.resolve())
    for pref in EXCLUDE_PATH_PREFIXES:
        if ap.startswith(pref):
            return True
    return False


def iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if should_skip(p):
            continue
        yield p


def sha256_file(path: Path) -> str:
    size = path.stat().st_size
    h = hashlib.sha256()
    with path.open("rb") as f:
        # If the file is huge, hash only the first MAX_HASH_SIZE bytes for speed,
        # but include size in record so consumers can decide how to treat it.
        remaining = MAX_HASH_SIZE
        while True:
            chunk = f.read(min(1024 * 1024, remaining))
            if not chunk:
                break
            h.update(chunk)
            remaining -= len(chunk)
            if remaining <= 0:
                break
    return h.hexdigest()


def top_md_title(lines: list[str]) -> str:
    for i, line in enumerate(lines[:10]):
        s = line.strip()
        if s.startswith("Title:"):
            return s[len("Title:"):].strip()
        if s.startswith("# "):
            return s[2:].strip()
    return ""


def md_headings(lines: list[str]) -> list[str]:
    heads: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("# "):
            heads.append(s[2:].strip())
        elif s.startswith("## "):
            heads.append(s[3:].strip())
    return heads[:50]


def write_inventory(files: list[Path]) -> None:
    out = AUDIT_DIR / "inventory.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "sha256", "last_modified_iso", "size_bytes"])
        for p in files:
            try:
                st = p.stat()
                sha = sha256_file(p)
                mtime = dt.datetime.fromtimestamp(st.st_mtime, tz=dt.timezone.utc).isoformat()
                w.writerow([str(p.resolve()), sha, mtime, st.st_size])
            except Exception:
                continue


def write_search_index(files: list[Path]) -> None:
    out = AUDIT_DIR / "search_index.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for p in files:
            try:
                st = p.stat()
                rec = {
                    "path": str(p.resolve()),
                    "rel": str(p.relative_to(ROOT)),
                    "ext": p.suffix.lower(),
                    "size": st.st_size,
                    "mtime": dt.datetime.fromtimestamp(st.st_mtime, tz=dt.timezone.utc).isoformat(),
                }
                if p.suffix.lower() == ".md":
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    lines = text.splitlines()
                    rec["title"] = top_md_title(lines)
                    rec["headings"] = md_headings(lines)
                    rec["preview"] = " ".join(lines[:30])[:2000]
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception:
                continue


def main() -> int:
    files = sorted(iter_files(ROOT))
    write_inventory(files)
    write_search_index(files)
    print(f"Indexed {len(files)} files → docs/audit/inventory.csv, docs/audit/search_index.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

