# GEMINI CLI — Agent Instructions
Last updated: 2025-09-02

Objectives:
- Keep documentation accurate and navigable.
- Parse FastAPI to refresh `docs/dev/api.md`.
- Ensure `pytest -q` passes on macOS and Windows.

Steps:
1. Generate repo manifest (paths/languages).
2. Run tests: `./scripts/test_all.sh` or `scripts\win\test_all.ps1`.
3. Propose minimal diffs; include tests & docs.
