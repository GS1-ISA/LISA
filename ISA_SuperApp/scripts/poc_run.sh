#!/usr/bin/env bash
set -euo pipefail

# PoC run helper for ISA SuperDesign (macOS)
# - prepares venv and installs Python deps
# - starts backend (uvicorn) in background and logs to logs/poc_uvicorn.log
# - launches the Electron app (dev)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p logs

# Ensure basic PATH so /bin/sleep and coreutils are available in non-login shells
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

# Load .env if present
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
else
  echo "ERROR: .env not found in project root. Copy .env.example -> .env and add your keys." >&2
  exit 1
fi

# Ensure venv
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# Use the venv's python/pip directly
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || true
fi
if [ -f requirements-dev.txt ]; then
  pip install -r requirements-dev.txt || true
fi
pip install -e . || true

## Helper: check if a PID is listening on port 8787 and stop it
PORT=8787
# Determine if anything is listening on the port. Prefer lsof, fall back to pgrep, else python connect test.
EXISTING_PID=""
if command -v lsof >/dev/null 2>&1; then
  EXISTING_PID="$(lsof -ti TCP:${PORT} -sTCP:LISTEN || true)"
fi
if [ -z "$EXISTING_PID" ] && command -v pgrep >/dev/null 2>&1; then
  # try to find uvicorn or python process that may be serving the API
  EXISTING_PID="$(pgrep -f 'uvicorn|src.api_server' | head -n 1 || true)"
fi
if [ -z "$EXISTING_PID" ]; then
  # final check: attempt to connect with python; if connect succeeds, we can't determine PID automatically
  if python - <<PY >/dev/null 2>&1
import socket
try:
    s=socket.socket(); s.settimeout(0.5); s.connect(('127.0.0.1', ${PORT})); s.close();
    print('1')
except Exception:
    pass
PY
  then
    EXISTING_PID="UNKNOWN"
  fi
fi
if [ -n "$EXISTING_PID" ]; then
  echo "Port ${PORT} is in use by pid=${EXISTING_PID}. Attempting to stop it..."
  if [ "$EXISTING_PID" = "UNKNOWN" ]; then
    echo "Warning: port ${PORT} appears occupied but PID couldn't be determined. Please free the port and retry." >&2
    exit 1
  fi
  # Try graceful TERM first
  kill $EXISTING_PID || true
  python - <<PY
import time
time.sleep(2)
PY
  if kill -0 $EXISTING_PID 2>/dev/null; then
    echo "Process ${EXISTING_PID} still alive, forcing kill..."
    kill -9 $EXISTING_PID || true
    python - <<PY
import time
time.sleep(1)
PY
  fi
  if kill -0 $EXISTING_PID 2>/dev/null; then
    echo "Warning: could not stop process ${EXISTING_PID}. Please free port ${PORT} and retry." >&2
    exit 1
  else
    echo "Stopped previous process on port ${PORT} (pid=${EXISTING_PID})."
  fi
fi

# Start backend (uvicorn) in background and capture logs
nohup uvicorn src.api_server:app --reload --port ${PORT} &> logs/poc_uvicorn.log &
UVICORN_PID=$!
echo "Started backend (uvicorn) pid=$UVICORN_PID, log: $REPO_ROOT/logs/poc_uvicorn.log"

# Start electron app (dev)
cd "$REPO_ROOT/desktop/electron"
# ensure node deps exist
if [ ! -d node_modules ]; then
  npm ci --no-audit --no-fund || npm install --no-audit --no-fund || true
fi

echo "Launching Electron (developer mode) in background. Backend pid: $UVICORN_PID"
# Launch electron in background and redirect logs to repo logs
cd "$REPO_ROOT/desktop/electron"
nohup npx electron . &> "$REPO_ROOT/logs/poc_electron.log" &
ELECTRON_PID=$!
echo "Started Electron pid=$ELECTRON_PID, log: $REPO_ROOT/logs/poc_electron.log"
echo "PoC started. Backend pid=$UVICORN_PID, Electron pid=$ELECTRON_PID"

# Print short tail of logs for quick feedback
sleep 1
echo "--- backend log (first 200 lines) ---"
sed -n '1,200p' "$REPO_ROOT/logs/poc_uvicorn.log" || true
echo "--- electron log (first 200 lines) ---"
sed -n '1,200p' "$REPO_ROOT/logs/poc_electron.log" || true
