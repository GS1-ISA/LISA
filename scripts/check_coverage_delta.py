#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASELINE = Path("docs/audit/coverage_baseline.json")

def parse_coverage(path: Path) -> float:
    tree = ET.parse(path)
    root = tree.getroot()
    lines_valid = float(root.attrib.get("lines-valid", 0))
    lines_covered = float(root.attrib.get("lines-covered", 0))
    if lines_valid <= 0:
        return 0.0
    return lines_covered / lines_valid * 100.0


def main() -> int:
    ap = argparse.ArgumentParser(description="Check coverage delta vs baseline (advisory)")
    ap.add_argument("--xml", default="ISA_SuperApp/coverage.xml")
    ap.add_argument("--threshold", type=float, default=0.5, help="max allowed drop in percentage points")
    ns = ap.parse_args()

    xml_path = Path(ns.xml)
    if not xml_path.exists():
        print(f"coverage xml not found: {xml_path}")
        return 0
    current = parse_coverage(xml_path)
    baseline_val = 0.0
    if BASELINE.exists():
        try:
            baseline_val = float(json.loads(BASELINE.read_text()).get("coverage_pct", 0.0))
        except Exception:
            baseline_val = 0.0
    delta = current - baseline_val
    print(f"Coverage: {current:.2f}% (baseline {baseline_val:.2f}%, Δ {delta:+.2f} pp)")
    if baseline_val and delta < -ns.threshold:
        print(f"WARNING: coverage decreased more than {ns.threshold:.2f} pp")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
