#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/decrypt_env.sh --in .env.enc --out .env --pass-file PATH
# or: ./scripts/decrypt_env.sh --in .env.enc --out .env --pass "mypassword"

show_help() {
  cat <<'EOF'
decrypt_env.sh - decrypt an encrypted .env.enc using password

Options:
  --in     Path to encrypted file (required)
  --out    Path to output plaintext (default: .env)
  --pass   Password string (not recommended on command line)
  --pass-file Path to file containing password
  --help

Example:
  ./scripts/decrypt_env.sh --in .env.enc --out .env --pass-file ~/.env_pass
EOF
}

IN_FILE=""
OUT_FILE=".env"
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
  read -s -p "Decryption password: " PASS
  echo
fi

openssl enc -d -aes-256-cbc -salt -pbkdf2 -iter 100000 -in "$IN_FILE" -out "$OUT_FILE" -pass pass:"$PASS"

echo "Decrypted $IN_FILE -> $OUT_FILE"
