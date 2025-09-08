#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

COVERAGE_XML = Path("ISA_SuperApp/coverage.xml")
COVERAGE_BASELINE = Path("docs/audit/coverage_baseline.json")
SIZE_BASELINE = Path("docs/audit/size_baseline.json")


def parse_coverage_pct(xml_path: Path) -> float:
    if not xml_path.exists():
        return 0.0
    root = ET.parse(xml_path).getroot()
    lines_valid = float(root.attrib.get("lines-valid", 0))
    lines_covered = float(root.attrib.get("lines-covered", 0))
    return (lines_covered / lines_valid * 100.0) if lines_valid else 0.0


def repo_disk_usage() -> int:
    total = 0
    try:
        out = subprocess.check_output(["git", "ls-files"], text=True)
        for line in out.splitlines():
            p = Path(line)
            if p.exists():
                try:
                    total += p.stat().st_size
                except Exception:
                    pass
    except Exception:
        pass
    return total


def repo_file_count() -> int:
    try:
        out = subprocess.check_output(["git", "ls-files"], text=True)
        return len([l for l in out.splitlines() if l])
    except Exception:
        return 0


def main() -> int:
    # coverage baseline
    pct = parse_coverage_pct(COVERAGE_XML)
    COVERAGE_BASELINE.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_BASELINE.write_text(
        json.dumps({"coverage_pct": pct}, indent=2), encoding="utf-8"
    )
    print(f"coverage baseline -> {COVERAGE_BASELINE} ({pct:.2f}%)")

    # size baseline
    size = repo_disk_usage()
    files = repo_file_count()
    SIZE_BASELINE.parent.mkdir(parents=True, exist_ok=True)
    SIZE_BASELINE.write_text(
        json.dumps({"size": size, "files": files}, indent=2), encoding="utf-8"
    )
    print(f"size baseline -> {SIZE_BASELINE} (size={size} bytes, files={files})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
