#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate || { echo "Run scripts/bootstrap.sh first"; exit 1; }
export ISA_TEST_MODE=0
exec uvicorn src.api_server:app --host 127.0.0.1 --port 8787
