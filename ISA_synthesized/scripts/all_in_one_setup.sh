#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Bootstrap Python =="
bash scripts/bootstrap.sh

echo "== Dev tools =="
bash scripts/setup_dev.sh

echo "== Tests =="
bash scripts/test.sh

echo "== VS Code bootstrap =="
bash scripts/bootstrap_vscode.sh || true

echo "== Electron deps =="
cd desktop/electron
npm install
cd ../..

if [ "${BUILD_DMG:-1}" = "1" ]; then
  echo "== Build universal DMG =="
  cd desktop/electron
  npx electron-builder --mac universal
  cd ../..
fi

if [ "${PUBLISH_GH:-0}" = "1" ]; then
  echo "== Publish to GitHub =="
  bash scripts/publish_github.sh
fi

echo "All-in-one setup completed ✅"
