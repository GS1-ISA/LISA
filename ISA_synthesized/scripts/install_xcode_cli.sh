#!/usr/bin/env bash
set -euo pipefail

# installs or verifies Xcode Command Line Tools on macOS
# Usage: ./scripts/install_xcode_cli.sh

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/install_xcode_cli.log"

echo "[INFO] Starting Xcode CLI install check: $(date)" | tee -a "$LOG_FILE"

function is_installed() {
  if xcode-select -p >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

if is_installed; then
  echo "[OK] Xcode Command Line Tools already installed at $(xcode-select -p)" | tee -a "$LOG_FILE"
  exit 0
fi

echo "[INFO] Xcode Command Line Tools not detected. Triggering installer..." | tee -a "$LOG_FILE"

# The --install command opens the GUI installer; it returns immediately.
xcode-select --install 2>&1 | tee -a "$LOG_FILE" || true

echo "[INFO] Waiting for Xcode Command Line Tools to be installed..." | tee -a "$LOG_FILE"

# Poll until installation completes
for i in {1..120}; do
  if is_installed; then
    echo "[OK] Detected Xcode Command Line Tools at $(xcode-select -p)" | tee -a "$LOG_FILE"
    break
  fi
  sleep 5
done

if ! is_installed; then
  echo "[ERROR] Xcode Command Line Tools not installed after waiting. Check the GUI installer and re-run this script." | tee -a "$LOG_FILE"
  exit 2
fi

echo "[INFO] You may need to accept the Xcode license. If prompted, run:\n  sudo xcodebuild -license accept" | tee -a "$LOG_FILE"

echo "[INFO] Done at $(date)" | tee -a "$LOG_FILE"
exit 0
