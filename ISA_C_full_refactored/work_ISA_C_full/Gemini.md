
# Gemini Contract
## Purpose
Execute small autonomous development steps based on roadmap.md.
## Context
Python project with agent loop. Write artifacts to out/. Patches to patches/.
## Constraints
- Max tokens: {{MAX_TOKENS}}
- JSON-only outputs following schema
- No secrets in logs
## Output Schema (JSON)
{
  "decision": "plan|implement|reflect",
  "files": [{"path": "out/...", "content": "..." }],
  "patches": [{"path": "RELATIVE/PATH", "unified_diff": "..." }],
  "notes": "brief rationale",
  "next_action": "string"
}
## Style
Deterministic. No prose outside JSON.
