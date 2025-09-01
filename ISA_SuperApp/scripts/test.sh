#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate || { echo "Run scripts/bootstrap.sh first"; exit 1; }
export ISA_TEST_MODE=1
if command -v pytest >/dev/null; then pytest -q; else python -m pytest -q; fi
python scripts/smoke_test.py
echo "Tests finished ✅"
