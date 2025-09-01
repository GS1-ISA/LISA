#!/usr/bin/env bash
set -euo pipefail

# One-shot bootstrap for a new GitHub repository using GitHub CLI (gh).
# Creates the repo, pushes current code, enables auto-merge, applies
# branch protection, and prints next steps. Run from the repo root.
#
# Requirements:
# - gh (GitHub CLI) installed and authenticated: gh auth status
# - git installed
#
# Usage:
#   scripts/bootstrap_repo.sh -o <owner> -r <repo> [-v public|private] [-b main]
#
# Environment fallbacks:
#   GH_OWNER, GH_REPO, GH_VISIBILITY, GH_DEFAULT_BRANCH

OWNER="${GH_OWNER:-}"
REPO="${GH_REPO:-}"
VISIBILITY="${GH_VISIBILITY:-public}"
DEFAULT_BRANCH="${GH_DEFAULT_BRANCH:-main}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--owner) OWNER="$2"; shift 2;;
    -r|--repo) REPO="$2"; shift 2;;
    -v|--visibility) VISIBILITY="$2"; shift 2;;
    -b|--branch) DEFAULT_BRANCH="$2"; shift 2;;
    -h|--help)
      grep '^# ' "$0" | sed 's/^# //'; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

if [[ -z "${OWNER}" || -z "${REPO}" ]]; then
  echo "ERROR: owner and repo are required. Use -o <owner> -r <repo> or set GH_OWNER/GH_REPO." >&2
  exit 1
fi

echo "==> Checking GitHub CLI auth"
if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI not authenticated. Run: gh auth login" >&2
  exit 1
fi

echo "==> Ensuring git repository"
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
fi

echo "==> Setting default branch: ${DEFAULT_BRANCH}"
# Create or switch default branch deterministically
if git show-ref --verify --quiet "refs/heads/${DEFAULT_BRANCH}"; then
  git checkout "${DEFAULT_BRANCH}"
else
  # If HEAD detached or no branch yet
  if git rev-parse --verify HEAD >/dev/null 2>&1; then
    git checkout -b "${DEFAULT_BRANCH}"
  else
    git symbolic-ref HEAD "refs/heads/${DEFAULT_BRANCH}"
  fi
fi

echo "==> Staging and committing current content (if any changes)"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "bootstrap: import codebase and CI"
fi

echo "==> Configuring remote and repository"
REMOTE_URL="https://github.com/${OWNER}/${REPO}.git"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "${REMOTE_URL}"
else
  git remote add origin "${REMOTE_URL}"
fi

echo "==> Creating repository on GitHub if it does not exist"
if ! gh repo view "${OWNER}/${REPO}" >/dev/null 2>&1; then
  gh repo create "${OWNER}/${REPO}" --"${VISIBILITY}" --source=. --remote=origin --push
else
  echo "Repo exists; pushing current branch"
  git push -u origin "${DEFAULT_BRANCH}"
fi

echo "==> Enabling auto-merge and repository settings"
gh api -X PATCH "repos/${OWNER}/${REPO}" \
  -f allow_auto_merge=true \
  -f delete_branch_on_merge=true \
  -f allow_squash_merge=true \
  -f allow_merge_commit=false \
  -f allow_rebase_merge=false \
  -f has_issues=true \
  -f has_projects=false \
  -f has_wiki=false >/dev/null

echo "==> Applying minimal branch protection on ${DEFAULT_BRANCH} (no required reviews)"
read -r -d '' PROTECTION_JSON <<'JSON'
{
  "required_status_checks": {"strict": false, "checks": []},
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true
}
JSON

gh api -X PUT \
  -H "Accept: application/vnd.github+json" \
  "repos/${OWNER}/${REPO}/branches/${DEFAULT_BRANCH}/protection" \
  -f required_status_checks.strict=false \
  -f enforce_admins=true \
  -f required_linear_history=true \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f block_creations=false \
  -f required_conversation_resolution=true >/dev/null || true

cat <<EOF

✅ Bootstrap complete for ${OWNER}/${REPO}

Next steps (zero-maintenance defaults already included):
- Auto-merge: Label a green PR with 'automerge' to merge automatically (see .github/workflows/automerge.yml)
- Tidy: PRs with OS cruft or temp folders will fail the 'Tidy Check' (see .github/workflows/tidy.yml)
- CI: PRs run lint/type/tests/coverage, determinism snapshots, docs build, significance-triggered deep checks (container smoke, Semgrep JSON)
- Agent: Run 'Agent Check (On-Demand)' workflow to produce an outcomes JSON for the agent to read

Optional secrets (SBOM/Trivy not required by current config):
- None required. If you later add container registries or private scanners, set those via:
  gh secret set <NAME> --repo ${OWNER}/${REPO}

Tips:
- Actions permissions: Ensure 'Workflow permissions' allow GITHUB_TOKEN read/write under Settings → Actions → General
- Branch protection: Adjust required checks later if you want stricter enforcement

EOF

