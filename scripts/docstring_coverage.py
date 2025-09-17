#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from pathlib import Path


def count_docstrings(root: Path) -> tuple[int, int]:
    total = 0
    documented = 0
    for p in root.rglob("*.py"):
        # Skip tests and dunder files
        rel = p.as_posix()
        if "/tests/" in rel:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Module docstring
        total += 1
        if ast.get_docstring(tree):
            documented += 1
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                total += 1
                if ast.get_docstring(node):
                    documented += 1
    return total, documented


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compute docstring coverage under a directory"
    )
    ap.add_argument("--path", default="src", help="Root directory to scan")
    ap.add_argument(
        "--min", type=float, default=0.0, help="Minimum required coverage (advisory)"
    )
    args = ap.parse_args()

    root = Path(args.path)
    total, documented = count_docstrings(root)
    pct = (documented / total * 100.0) if total else 100.0
    print(
        f"Docstring coverage: {documented}/{total} = {pct:.1f}% (min {args.min:.1f}%)"
    )
    # Advisory metric: exit 0 regardless
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
