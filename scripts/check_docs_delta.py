#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DOC_PATH_PREFIXES = ("docs/",)
DOC_FILES = {"README.md"}
CODE_EXTS = (".py", ".ts", ".tsx", ".js", ".rs", ".go")
CODE_EXTRA = ("Dockerfile",)


def run(cmd: list[str]) -> str:
    out = subprocess.check_output(cmd, text=True).strip()
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Fail if there are code changes without any documentation changes"
    )
    p.add_argument("--base", required=True, help="Base commit SHA to diff against")
    p.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Optional path filters to restrict code check",
    )
    args = p.parse_args(argv)

    diff_cmd = ["git", "diff", "--name-only", args.base, "HEAD"]
    changed = [ln for ln in run(diff_cmd).splitlines() if ln]
    if args.paths:
        changed = [p for p in changed if any(p.startswith(pref) for pref in args.paths)]

    docs_changed = any(
        f.startswith(DOC_PATH_PREFIXES)
        or (Path(f).name in DOC_FILES)
        or f.endswith(".md")
        for f in changed
    )
    code_changed = any(
        Path(f).suffix in CODE_EXTS
        or Path(f).name in CODE_EXTRA
        or f.startswith("src/")
        for f in changed
    )

    if code_changed and not docs_changed:
        print("Doc delta check: code changed but no docs changed.")
        for f in changed:
            print("-", f)
        return 1
    print("Doc delta check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
