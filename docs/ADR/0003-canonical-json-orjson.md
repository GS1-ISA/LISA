# ADR 0003 — Canonical JSON with Optional orjson
Last updated: 2025-09-02

Context
- We require deterministic JSON for snapshots and reproducible artifacts.
- Performance can matter on large outputs; orjson is significantly faster but not always available.

Decision
- Keep stdlib json as the default canonical writer for maximum portability.
- Add an optional path using orjson, controlled by env `CANONICAL_USE_ORJSON=1`.
- Maintain identical canonical properties (sorted keys, UTF-8, compact separators) as far as practical.
- Validate parity with snapshot tests before enabling in production flows.

Consequences
- Gains performance where enabled; safe fallback preserves determinism if orjson is missing.
- Slightly more complexity in the writer; minimal risk due to fallback.

Status: Accepted (conditional enablement via env)

Adoption Notes (2025-09-01)
- Bench summary (scripts/bench_q11_orjson.py; results in docs/research/q11_orjson_determinism/results.md):
  - Determinism parity: OK for stdlib and orjson with sorted keys + UTF‑8 + explicit newline policy.
  - Performance: orjson ≈13.5× faster than stdlib on a medium payload locally.
- Policy: keep stdlib as default; allow opting into orjson via `CANONICAL_USE_ORJSON=1` in perf‑sensitive paths.
- Promotion: enable orjson by default only after cross‑OS verification and 7 green nightly snapshot runs.
