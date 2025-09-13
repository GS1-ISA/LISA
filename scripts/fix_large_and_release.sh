#!/usr/bin/env bash
set -euo pipefail

# Remove >100MB installer zips from Git history, ignore them going forward,
# force-push the cleaned branch, and optionally create a GitHub Release
# attaching the local installer files — all in one go.
#
# Usage examples:
#   scripts/fix_large_and_release.sh --files \
#     "isa-desktop-0.2.0-universal.dmg.zip" \
#     "isa-desktop-0.2.0-universal 2.dmg.zip" \
#     --tag v0.2.0 --release
#
#   scripts/fix_large_and_release.sh --files "path/to/*.dmg.zip"
#
# Requirements: git, python3/pip (to install git-filter-repo), gh (optional for release)

TAG=""            # e.g. v0.2.0
DO_RELEASE=false   # set true with --release
FILES=()

die() { echo "ERROR: $*" >&2; exit 1; }

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --files)
      shift
      # Collect until next flag or end
      while [[ $# -gt 0 && "$1" != --* ]]; do
        FILES+=("$1"); shift
      done
      ;;
    --tag)
      TAG="$2"; shift 2 ;;
    --release)
      DO_RELEASE=true; shift ;;
    -h|--help)
      grep '^# ' "$0" | sed 's/^# //'; exit 0 ;;
    *) die "Unknown arg: $1" ;;
  esac
done

[[ ${#FILES[@]} -gt 0 ]] || die "No files specified. Use --files <path> [more paths]"

echo "==> Ensuring git repo and current branch"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Not a git repo"
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "==> Installing git-filter-repo if missing"
if ! command -v git-filter-repo >/dev/null 2>&1; then
  python3 -m pip install --user git-filter-repo >/dev/null 2>&1 || die "Install git-filter-repo (pip) failed"
  export PATH="$HOME/.local/bin:$HOME/Library/Python/$(python3 -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin:$PATH"
fi

echo "==> Purging large files from git history"
cmd=(git filter-repo --invert-paths)
for f in "${FILES[@]}"; do cmd+=(--path "$f"); done
"${cmd[@]}"

echo "==> Ignoring future installer zips"
{ echo ''; echo '# Ignore installer archives'; echo 'isa-desktop-*.dmg.zip'; } >> .gitignore || true
git add .gitignore || true
if ! git diff --cached --quiet; then
  git commit -m "Ignore installers; purge large binaries from history"
fi

echo "==> Pushing cleaned history to origin/$BRANCH (force)"
git push -u origin "$BRANCH" --force

if $DO_RELEASE; then
  [[ -n "$TAG" ]] || die "--release requires --tag <version>"
  echo "==> Creating GitHub Release $TAG with installer assets (gh)"
  if ! gh auth status >/dev/null 2>&1; then
    echo "GitHub CLI not authenticated. Run: gh auth login" >&2
    exit 1
  fi
  # Collect existing local files for upload (globs supported)
  ASSETS=()
  for f in "${FILES[@]}"; do
    for m in $f; do [[ -f "$m" ]] && ASSETS+=("$m"); done
  done
  [[ ${#ASSETS[@]} -gt 0 ]] || die "No local assets found to upload"
  gh release create "$TAG" "${ASSETS[@]}" -t "$TAG" -n "Desktop build $TAG"
fi

echo "==> Done"
