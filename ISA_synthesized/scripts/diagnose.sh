#!/usr/bin/env bash
set -euo pipefail
echo "===== System ====="
sw_vers || true
uname -a

echo "===== Python ====="
which python3 || true
python3 --version || true

echo "===== Node/NPM ====="
which node || true
node -v || true
npm -v || true

echo "===== Ports ====="
lsof -i :8787 || true

echo "===== Venv & Packages ====="
if [ -d ".venv" ]; then
  source .venv/bin/activate
  python -m pip list | head -n 50
fi
echo "Diagnostics complete ✅"
