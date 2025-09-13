#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Ensure venv
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install -U pip wheel >/dev/null 2>&1 || true
pip install -r ISA_SuperApp/requirements.txt -r ISA_SuperApp/requirements-dev.txt >/dev/null 2>&1 || true
# Start API
( cd ISA_SuperApp && python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8787 >/tmp/isa_api.log 2>&1 & echo $! > /tmp/isa_api.pid )
# Wait for /metrics
for i in $(seq 1 30); do curl -fsS http://127.0.0.1:8787/metrics >/dev/null && break || sleep 1; done
# Exercise endpoints
curl -fsS -X POST http://127.0.0.1:8787/ask -H 'Content-Type: application/json' -d '{"question":"What is ISA?","explain":true}' | sed -n '1,5p'
# Cleanup
if [ -f /tmp/isa_api.pid ]; then kill $(cat /tmp/isa_api.pid) || true; rm -f /tmp/isa_api.pid; fi
