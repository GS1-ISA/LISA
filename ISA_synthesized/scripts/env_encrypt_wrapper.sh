#!/usr/bin/env bash
set -euo pipefail

# Wrapper to run the repo's encrypt script in a shell-agnostic way.
# Usage: env_encrypt_wrapper.sh <pass-file> <in-env> <out-env-enc>

if [ "$#" -ne 3 ]; then
  echo "usage: $0 <pass-file> <in-env> <out-env-enc>" >&2
  exit 2
fi

passfile="$1"
infile="$2"
outfile="$3"

if [ ! -f "$infile" ]; then
  echo "input file '$infile' not found" >&2
  exit 3
fi

# Ensure openssl is available
if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl not found in PATH" >&2
  exit 4
fi

# Prefer running the repository helper if present
if [ -f "scripts/encrypt_env.sh" ]; then
  echo "Running scripts/encrypt_env.sh..."
  # invoke with bash to avoid zsh attribute quirks
  bash scripts/encrypt_env.sh --in "$infile" --out "$outfile" --pass-file "$passfile"
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "Encryption successful (via scripts/encrypt_env.sh) -> $outfile"
    exit 0
  fi
  echo "encrypt_env.sh failed with exit $rc, falling back to openssl" >&2
fi

# Fallback: directly use openssl compatible command
echo "Using fallback openssl to create $outfile"
salt_hex=$(openssl rand -hex 8)
# Use AES-256-CBC with pbkdf2 and 100000 iterations to match the repo scripts
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -S "$salt_hex" -in "$infile" -out "$outfile" -pass file:"$passfile"
rc=$?
if [ $rc -ne 0 ]; then
  echo "openssl fallback failed with exit $rc" >&2
  exit $rc
fi

echo "Encryption successful (openssl fallback) -> $outfile"
exit 0
