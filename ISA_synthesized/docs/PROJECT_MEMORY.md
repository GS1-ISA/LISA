# Project Memory (Curated)

## Vision (Long-term)
- ISA as autonomous, standards-aware assistant for GS1 NL.

## Principles
- Plan → Act → Verify → Document → Commit.
- No secrets in VCS. Deterministic builds.

## Decisions (Chronological)
- 2025-08-20: Gemini orchestrator loop adopted. Tokens generated at build/run into webui/tokens.css.
- 2025-08-20: PYTHONPATH set for all subprocesses from api_server.

## Open Risks
- Codesigning for macOS distribution pending Developer ID.
- STUB mode when keys absent—communicate clearly in UI/logs.

## Next Milestones
- Expand smoke tests to exercise API routes and DB integrations.
- CI matrix (macOS arm64/x64 + universal DMG).
