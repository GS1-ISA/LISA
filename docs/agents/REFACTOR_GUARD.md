# Refactor Guard — Local CLI

Purpose: Provide a local, ISA_D-native CLI that mirrors the “ISA_D Refactor Pack” flow without relying on external feature-flag services or GitHub APIs. It integrates with this repo’s CI and artifacts.

Quickstart
- Bootstrap: `python scripts/refactor_guard.py bootstrap`
- Pre-check: `python scripts/refactor_guard.py pre-check`
- Slice: `python scripts/refactor_guard.py slice`
- Scaffold: `python scripts/refactor_guard.py scaffold S01`
- Next: `python scripts/refactor_guard.py next`
- Status: `python scripts/refactor_guard.py status`
- Sweep: `python scripts/refactor_guard.py sweep S01`
- Rollback: `python scripts/refactor_guard.py rollback`

Artifacts
- Board: `artifacts/refactor_guard/board.json` (REFACTOR_2025 with columns)
- Logs: `artifacts/refactor_guard/run.log`
- Coverage/pytest logs: `artifacts/refactor_guard/coverage.xml`, `pytest_run_*.log`
- Flags: `infra/feature_flags/local_flags.json`

Notes
- Pre-check runs tests 3×, computes coverage gaps (<80% in `src/`), and detects flakies across runs. It writes tracking issues under `docs/issues/` and blocks further actions until green/unblocked.
- Slices are derived from `coherence_graph.json` if present (incoming-edge heuristic) or by small folder clusters (≤10 files). Output: `Sxx|<domain>|files|entry-points|flag|est LOC|risk`.
- Scaffold creates a local feature flag and a stub canary dashboard (local file URLs).
- Next simulates PR creation locally by running advisory tools and writing a PR summary stub to `artifacts/refactor_guard/`.
- Sweep writes a deletion plan for legacy files; it does not delete files automatically.
- Rollback flips all `ISA_REF_*` flags to false.
