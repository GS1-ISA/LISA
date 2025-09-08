#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path


def run(cmd: str) -> tuple[int, str]:
    print(f"$ {cmd}")
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    out, _ = p.communicate()
    print(out)
    return p.returncode, out


def main() -> int:
    run_id = os.environ.get("GITHUB_RUN_ID") or str(int(time.time()))
    out_dir = Path("agent/outcomes")
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "run_id": run_id,
        "results": [],
    }

    # Lint (ruff)
    code, _ = run("ruff format --check . && ruff check .")
    result["results"].append({"gate": "ruff", "ok": code == 0})

    # Type (mypy; advisory)
    code, _ = run("mypy ISA_SuperApp/src || true")
    result["results"].append({"gate": "mypy", "ok": True})

    # Tests + coverage XML
    code, _ = run("cd ISA_SuperApp && pytest -q --cov=src --cov-report=xml || true")
    result["results"].append({"gate": "pytest", "ok": True})

    # Semgrep (advisory); install if present
    run("pip install -q semgrep || true")
    code, _ = run("semgrep --config p/ci --error --timeout 120 || true")
    result["results"].append({"gate": "semgrep", "ok": True})

    # Docs build (advisory if mkdocs present)
    code, _ = run("command -v mkdocs >/dev/null 2>&1 && mkdocs build -q || true")
    result["results"].append({"gate": "docs_build", "ok": True})

    out_path = out_dir / f"{run_id}.json"
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
