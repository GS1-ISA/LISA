# Data Quality Expectations — Starter Plan
Last updated: 2025-09-02

Scope (Phase 1)
- Select one critical input dataset.
- Define 5–10 expectations (schema, nulls, ranges, regex, uniqueness).
- Keep execution local-first (pydantic-core or Great Expectations) and output HTML/JSON report.

Artifacts
- expectations.json (or GE suite YAML)
- report.html (published under docs/audit or artifacts)

CI (Advisory → Enforced)
- Run expectations on PR for touched pipelines (advisory).
- Promote to enforced for core paths after 7 green runs (no critical failures).

Acceptance
- Expectations run in < 60s on sample; report attached; violations categorized by severity.
