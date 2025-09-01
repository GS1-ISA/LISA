#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/encrypt_env.sh --in .env --out .env.enc --pass-file PATH
# or: ./scripts/encrypt_env.sh --in .env --out .env.enc --pass "mypassword"

show_help() {
  cat <<'EOF'
encrypt_env.sh - encrypt a local .env for safe repo storage

Options:
  --in     Path to plaintext .env (required)
  --out    Path to output encrypted file (default: .env.enc)
  --pass   Password string (not recommended on command line)
  --pass-file Path to file containing password
  --help

Example:
  ./scripts/encrypt_env.sh --in .env --out .env.enc --pass-file ~/.env_pass
EOF
}

IN_FILE=""
OUT_FILE=".env.enc"
PASS=""
PASS_FILE=""

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --in) IN_FILE="$2"; shift 2;;
    --out) OUT_FILE="$2"; shift 2;;
    --pass) PASS="$2"; shift 2;;
    --pass-file) PASS_FILE="$2"; shift 2;;
    --help) show_help; exit 0;;
    *) echo "Unknown arg: $1"; show_help; exit 2;;
  esac
done

if [[ -z "$IN_FILE" ]]; then
  echo "Missing --in"; show_help; exit 2
fi

if [[ ! -f "$IN_FILE" ]]; then
  echo "Input file not found: $IN_FILE"; exit 2
fi

if [[ -n "$PASS_FILE" ]]; then
  if [[ ! -f "$PASS_FILE" ]]; then
    echo "Pass file not found: $PASS_FILE"; exit 2
  fi
  PASS=$(<"$PASS_FILE")
fi

if [[ -z "$PASS" ]]; then
  read -s -p "Encryption password: " PASS
  echo
fi

# Use AES-256-CBC with pbkdf2 and many iterations
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 -in "$IN_FILE" -out "$OUT_FILE" -pass pass:"$PASS"

echo "Encrypted $IN_FILE -> $OUT_FILE"
