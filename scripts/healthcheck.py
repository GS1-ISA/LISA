#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path.cwd()
REPORT = ROOT / "docs" / "audit" / "healthcheck.md"


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return 0, out
    except FileNotFoundError:
        return 127, f"SKIPPED: {' '.join(cmd)} (not installed)"
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output


def section(title: str, body: str) -> str:
    return f"## {title}\n\n```\n{body.rstrip()}\n```\n"


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    md: list[str] = ["# Project Healthcheck", ""]

    _rc, out = run(["ruff", "check", "."])
    md.append(section("ruff (lint)", out))

    _rc, out = run(["mypy", "ISA_SuperApp/src"])  # advisory
    md.append(section("mypy (types)", out))

    _rc, out = run(
        [
            "bash",
            "-lc",
            "cd ISA_SuperApp && pytest -q tests/unit/test_snapshot_canonical_sample.py",
        ]
    )  # determinism
    md.append(section("pytest (determinism snapshot)", out))

    _rc, out = run(["bandit", "-qq", "-r", "ISA_SuperApp/src"])  # advisory
    md.append(section("bandit (security)", out))

    _rc, out = run(["pip-audit"])  # advisory
    md.append(section("pip-audit (deps)", out))

    # Docs refs
    _rc, out = run(["python3", "scripts/docs_ref_lint.py"])
    md.append(section("docs-ref-lint", out))

    # Coherence audit
    _rc, out = run(["python3", "scripts/coherence_audit.py"])
    md.append(section("coherence-audit", out))
    try:
        score = (ROOT / "COHERENCE_SCORECARD.md").read_text(encoding="utf-8")
        md.append(section("coherence-scorecard", score))
    except Exception:
        md.append(section("coherence-scorecard", "No scorecard found."))

    REPORT.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
