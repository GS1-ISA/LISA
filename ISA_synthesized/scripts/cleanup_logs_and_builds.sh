#!/usr/bin/env bash
set -euo pipefail

# Prune logs and temporary build artifacts to keep the repo clean.
# Usage: ./scripts/cleanup_logs_and_builds.sh [--dry-run]

DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
fi

ROOT=$(cd "$(dirname "$0")/.." && pwd)
LOG_DIR="$ROOT/logs"
DIST_DIR="$ROOT/desktop/electron/dist"
NODE_MODULES="$ROOT/desktop/electron/node_modules"

function rm_or_echo() {
  if [ "$DRY_RUN" = true ]; then
    echo "DRY-RUN: would remove: $1"
  else
    echo "Removing: $1"
    rm -rf "$1"
  fi
}

mkdir -p "$LOG_DIR"

echo "Cleaning logs and build artifacts (dry-run=$DRY_RUN)"
rm_or_echo "$LOG_DIR/*"
rm_or_echo "$DIST_DIR"
rm_or_echo "$NODE_MODULES"

echo "Done"
