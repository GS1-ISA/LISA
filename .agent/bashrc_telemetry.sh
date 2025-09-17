#!/usr/bin/env bash
# VS Code terminal telemetry stub — safe, no-op if tools missing.

_isa_ts() { date -u +%s; }

_isa_cpu_mwh() {
  if command -v powermetrics >/dev/null 2>&1; then
    # powermetrics may require privileges; best-effort parse
    local line
    line=$(powermetrics -n 1 -f plist 2>/dev/null | grep -m1 "CPU Power")
    echo "${line##*>}" | sed 's/<.*$//' | tr -d '[:space:]'
  else
    echo "N/A"
  fi
}

_isa_log() {
  local out=".ai/cache/terminal_telemetry.csv"
  mkdir -p .ai/cache 2>/dev/null || true
  echo "$(_isa_ts),$?,$(_isa_cpu_mwh)" >> "$out" 2>/dev/null || true
}

# Append to PROMPT_COMMAND without clobbering existing hooks
if [[ -z "$PROMPT_COMMAND" ]]; then
  PROMPT_COMMAND="_isa_log"
else
  PROMPT_COMMAND="${PROMPT_COMMAND};_isa_log"
fi

export PROMPT_COMMAND

