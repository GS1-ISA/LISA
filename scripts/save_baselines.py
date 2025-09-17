#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import json
import subprocess
from pathlib import Path

try:
    from src.xml_utils import XMLParseError, XMLValidationError, parse_coverage_xml
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from xml_utils import XMLParseError, XMLValidationError, parse_coverage_xml

COVERAGE_XML = Path("ISA_SuperApp/coverage.xml")
COVERAGE_BASELINE = Path("docs/audit/coverage_baseline.json")
SIZE_BASELINE = Path("docs/audit/size_baseline.json")


def parse_coverage_pct(xml_path: Path) -> float:
    if not xml_path.exists():
        return 0.0
    try:
        data = parse_coverage_xml(xml_path)
        return data["coverage_pct"]
    except (XMLParseError, XMLValidationError) as e:
        print(f"Error parsing coverage XML {xml_path}: {e}")
        return 0.0
    except Exception as e:
        print(f"Unexpected error parsing coverage XML {xml_path}: {e}")
        return 0.0


def repo_disk_usage() -> int:
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
