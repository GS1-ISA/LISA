#!/usr/bin/env bash
set -euo pipefail

# Small bootstrap helper for developers:
# - ensures shell scripts in scripts/ are executable
# - prints short usage for the encrypt/decrypt helpers

repo_root="$(cd "$(dirname "$0")/.." && pwd)"

echo "[BOOTSTRAP] repo root: $repo_root"
echo "[BOOTSTRAP] making shell scripts in $repo_root/scripts executable"
/bin/chmod a+x "$repo_root"/scripts/*.sh || true

cat <<'USAGE'
Bootstrap complete.

To encrypt your .env (recommended: create a pass-file first):
  printf '%s' 'your-strong-password' > ~/.env_pass
  chmod 600 ~/.env_pass
  bash scripts/env_encrypt_wrapper.sh ~/.env_pass .env .env.enc

To decrypt (verify):
  bash scripts/decrypt_env.sh --in .env.enc --out .env.test --pass-file ~/.env_pass

USAGE

exit 0
