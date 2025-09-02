#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--min-mb", type=int, default=25)
    ns = ap.parse_args()

    candidates: list[Path] = []
    # archives in repo root
    for pat in ("*.zip", "*.tar.gz", "*.tgz", "*.7z"):
        for p in ROOT.glob(pat):
            try:
                if p.stat().st_size >= ns.min_mb * 1024 * 1024:
                    candidates.append(p)
            except FileNotFoundError:
                pass
    # temp/OS dirs anywhere
    for n in ("__MACOSX", "temp_unzip"):
        candidates.extend([p for p in ROOT.rglob(n) if p.is_dir()])
    # stray .DS_Store (skip .git and .venv)
    for p in ROOT.rglob(".DS_Store"):
        s = str(p)
        if "/.git/" in s or "/.venv/" in s:
            continue
        candidates.append(p)

    uniq = []
    seen = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        uniq.append(c)

    if not uniq:
        print("Nothing to prune")
        return 0
    print("Candidates:")
    for c in uniq:
        print(" -", c)
    if not ns.apply:
        print("(dry-run) Use --apply to delete")
        return 0
    for c in sorted(uniq, key=lambda x: len(str(x)), reverse=True):
        try:
            if c.is_dir():
                shutil.rmtree(c, ignore_errors=True)
            else:
                c.unlink(missing_ok=True)
        except Exception as e:
            print("WARN: ", e)
    print("Prune complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
