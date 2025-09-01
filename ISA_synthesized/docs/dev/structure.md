# Directory Structure
Last updated: 2025-09-02

Ownership boundaries:
- `src/` — API and logic — stable contracts; changes require tests.
- `webui/` — static bundle — add features minimally.
- `desktop/electron/` — packaging — keep API startup via scripts.
- `tests/` — pytest — expand coverage, keep deterministic.
- `docs/` — MkDocs — keep nav consistent with files.
