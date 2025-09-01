#!/usr/bin/env python3
"""Check coverage against a baseline and fail on regression > threshold.

Usage: scripts/check_coverage_delta.py [--baseline docs/coverage_baseline.txt] [--threshold 0.5]

Exits non-zero if coverage.xml exists and baseline exists and the drop > threshold percent.
If baseline is missing, prints a notice and exits 0 (advisory mode).
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def read_coverage_percent(coverage_xml: Path) -> float:
    tree = ET.parse(str(coverage_xml))
    root = tree.getroot()
    # Cobertura XML has line-rate attribute (0..1)
    line_rate = root.attrib.get("line-rate")
    if line_rate is None:
        raise ValueError("coverage.xml missing line-rate attribute")
    return float(line_rate) * 100.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coverage", default="coverage.xml")
    ap.add_argument("--baseline", default="docs/coverage_baseline.txt")
    ap.add_argument("--threshold", type=float, default=0.5)
    args = ap.parse_args()

    cov_path = Path(args.coverage)
    base_path = Path(args.baseline)

    if not cov_path.exists():
        print(f"[coverage-delta] {cov_path} not found; skipping")
        return 0
    if not base_path.exists():
        print(f"[coverage-delta] baseline {base_path} not found; skipping (advisory)")
        return 0

    current = read_coverage_percent(cov_path)
    baseline = float(base_path.read_text(encoding="utf-8").strip())
    delta = current - baseline
    print(f"[coverage-delta] current={current:.2f}% baseline={baseline:.2f}% delta={delta:+.2f}pp")
    if delta < -args.threshold:
        print(
            f"[coverage-delta] FAIL: drop {abs(delta):.2f}pp exceeds threshold {args.threshold:.2f}pp",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

