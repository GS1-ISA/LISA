#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate || { echo "Run scripts/bootstrap.sh first"; exit 1; }
pip install -r requirements-dev.txt
pip install pre-commit
pre-commit install
echo "Dev tools installed (pytest/black/ruff/mypy) and pre-commit hooks enabled ✅"
