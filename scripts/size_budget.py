#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import json
import subprocess
from pathlib import Path

BASELINE = Path("docs/audit/size_baseline.json")


def repo_disk_usage() -> int:
    # approximate: sum of file sizes under git ls-files
    total = 0
    try:
        out = subprocess.check_output(["git", "ls-files"], text=True)
        for line in out.splitlines():
            p = Path(line)
            if p.exists():
                with contextlib.suppress(Exception):
                    total += p.stat().st_size
    except Exception:
        pass
    return total


def repo_file_count() -> int:
    try:
        out = subprocess.check_output(["git", "ls-files"], text=True)
        return len([name for name in out.splitlines() if name])
    except Exception:
        return 0


def pct(delta: float, base: float) -> float:
    return (delta / base * 100.0) if base > 0 else 0.0


def main() -> int:
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    size = repo_disk_usage()
    files = repo_file_count()
    baseline = {"size": 0, "files": 0}
    if BASELINE.exists():
        with contextlib.suppress(Exception):
            baseline = json.loads(BASELINE.read_text())
    size_delta = size - baseline.get("size", 0)
    files_delta = files - baseline.get("files", 0)
    print(
        f"Repo size: {size / 1024 / 1024:.2f} MB (Δ {size_delta / 1024 / 1024:.2f} MB)"
    )
    print(f"File count: {files} (Δ {files_delta})")
    # advisory budget: warn if >10% increase
    if baseline.get("size", 0) > 0 and pct(size_delta, baseline["size"]) > 10.0:
        print("WARNING: repo size increased >10% since baseline")
    if baseline.get("files", 0) > 0 and pct(files_delta, baseline["files"]) > 10.0:
        print("WARNING: file count increased >10% since baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
