#!/usr/bin/env bash
set -euo pipefail

# Auto stage, commit, branch, push, open PR, and enable auto-merge.
# Requires: git, gh (GitHub CLI) authenticated (gh auth login)
#
# Usage:
#   scripts/auto_git.sh --msg "chore: tidy" [--branch feature/tidy] [--automerge]
#   scripts/auto_git.sh --msg "docs: refresh" --automerge
#

MSG=""
BRANCH=""
DO_AUTOMERGE=false

die() { echo "ERROR: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --msg) MSG="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --automerge) DO_AUTOMERGE=true; shift ;;
    -h|--help)
      sed -n '1,60p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ -n "$MSG" ]] || die "--msg is required"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Not a git repo"
CURR_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Determine branch
if [[ -z "$BRANCH" ]]; then
  ts=$(date +%Y%m%d-%H%M%S)
  BRANCH="chore/auto-${ts}"
fi

echo "==> Staging changes"
git add -A
if git diff --cached --quiet; then
  echo "No staged changes; exiting"
  exit 0
fi

echo "==> Creating/switching to branch: $BRANCH"
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git checkout "$BRANCH"
else
  git checkout -b "$BRANCH"
fi

echo "==> Committing"
git commit -m "$MSG"

echo "==> Pushing to origin/$BRANCH"
git push -u origin "$BRANCH"

echo "==> Creating PR -> main"
PR_URL=$(gh pr create --base main --head "$BRANCH" --title "$MSG" --body "Automated PR via scripts/auto_git.sh" --label autoupdate || true)
echo "PR: ${PR_URL:-'(already exists?)'}"

if $DO_AUTOMERGE; then
  echo "==> Enabling auto-merge (squash)"
  # If PR exists, enable automerge
  gh pr merge --auto --squash "$BRANCH" || true
fi

echo "==> Done"
