#!/usr/bin/env bash
set -euo pipefail
proj="/Users/frisowempe/Desktop/ISA_B/2-main/ISA_SuperDesign_VSCode_Copilot_OneShot_2025-08-17"
sanitizer="$proj/scripts/sanitize_zsh_path.py"
if [ ! -f "$sanitizer" ]; then
  echo "ERROR: sanitizer not found: $sanitizer"; exit 2
fi
backup_dir="$HOME/zsh-init-backup-$(date +%Y%m%d%H%M%S)"
mkdir -p "$backup_dir"
for f in "$HOME/.zprofile" "$HOME/.zshrc"; do
  if [ -f "$f" ]; then
    cp -p "$f" "$backup_dir/" || true
    echo "BACKED_UP: $f -> $backup_dir/"
  else
    echo "NOFILE: $f"
  fi
done
# Run sanitizer with python (avoid loading rc files)
python3 "$sanitizer" "$HOME/.zprofile" "$HOME/.zshrc" || true
changed=0
for f in "$HOME/.zprofile.fixed" "$HOME/.zshrc.fixed"; do
  if [ -f "$f" ]; then
    orig="${f%.fixed}"
    echo "--- DIFF $orig -> $f (redacted) ---"
    diff -u "$orig" "$f" | sed -E \
      -e 's/(API_KEY|GEMINI_[A-Z_]+|GOOGLE_API_KEY|GEMINI_MODEL|GEMINI_THINKING_ENABLED|GEMINI_TIMEOUT|GEMINI_AUTO_LOGIN)[[:space:]]*=\s*[^\n]*/\1=[REDACTED]/g' \
      -e 's/"[^"]*"/[REDACTED]/g' \
      -e "s/'[^']*'/[REDACTED]/g" || true
    cp -p "$f" "$orig"
    chmod 600 "$orig" || true
    echo "APPLIED: $orig"
    changed=1
  fi
done
if [ $changed -eq 0 ]; then
  echo "NO_CHANGES_APPLIED"
else
  echo "SANITIZER_APPLIED"
fi
# run login zsh smoke test and print last 120 lines of trace
/bin/zsh -l -x -c 'exit' 2> /tmp/zsh_login_trace_after.log || true

echo "--- zsh login trace (last 120 lines) ---"
tail -n 120 /tmp/zsh_login_trace_after.log || true
