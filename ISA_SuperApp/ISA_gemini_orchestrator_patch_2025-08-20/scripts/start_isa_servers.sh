#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -f ".venv/bin/python" ]]; then python3 -m venv .venv; fi
source .venv/bin/activate
pip -q install -r requirements.txt || true
python scripts/verify_credentials.py || { echo "Fix env first"; exit 1; }
python scripts/generate_tokens.py --out webui/tokens.css
exec uvicorn src.api_server:app --reload --port 8787
