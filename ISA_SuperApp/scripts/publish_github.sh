#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' not found. Install: brew install gh"
  exit 1
fi

REPO_NAME="${REPO_NAME:-isa-superdesign}"
REPO_VISIBILITY="${REPO_VISIBILITY:-private}"
REPO_OWNER="${REPO_OWNER:-}" # set to your GitHub org/user to avoid prompt

git init
git add -A
git commit -m "feat: initial turnkey commit"

if [ -n "$REPO_OWNER" ]; then
  gh repo create "$REPO_OWNER/$REPO_NAME" --$REPO_VISIBILITY --source . --push --disable-issues=false --disable-wiki=true
else
  gh repo create "$REPO_NAME" --$REPO_VISIBILITY --source . --push --disable-issues=false --disable-wiki=true
fi

echo "GitHub repository created and pushed ✅"
