Title: ADR 0003 — Canonical JSON with Optional orjson

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

