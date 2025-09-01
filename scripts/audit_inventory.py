#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
from datetime import UTC, datetime
from pathlib import Path

EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        yield p


def main() -> int:
    root = Path.cwd()
    out_dir = root / "docs" / "audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "inventory.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "sha256", "last_modified_iso", "size_bytes"])
        for p in iter_files(root):
            try:
                stat = p.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat()
                size = stat.st_size
                digest = sha256_file(p)
                w.writerow([str(p), digest, mtime, size])
            except Exception:
                # best-effort
                continue
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
