Title: ADR 0004 — JSON Schema Validation via fastjsonschema

Context
- Pydantic v2 provides rich model validation and typed APIs. For pure JSON Schema validation at high throughput, a compiled validator like fastjsonschema can be faster.

Decision
- Introduce a JSON Schema validation utility based on fastjsonschema for heavy schema-only checks.
- Keep Pydantic models for domain types and transformation logic.
- Use fastjsonschema selectively in hot loops where schema validation dominates cost; guard behind feature flags/config.

Consequences
- Improved throughput for schema-only paths; two validation mechanisms increase cognitive load slightly.
- Requires dependency (fastjsonschema) in dev/ci; optional in prod depending on usage.

Status: Accepted (selective use)

Adoption Notes (2025-09-01)
- Bench summary (scripts/bench_q12_validation.py; results in docs/research/q12_compiled_validators/results.md):
  - Parity: both Pydantic v2 and fastjsonschema reject invalid inputs in our sample.
  - Performance (simple schema): Pydantic v2 was faster (~1.0–1.2µs/op vs fastjsonschema ~3.0µs/op) in local measurements.
- Policy: keep Pydantic v2 as default validator for model‑backed code paths. Use fastjsonschema selectively for pure JSON Schema validation where it shows wins on real schemas.
- Next: run benches with representative, larger schemas to reassess; adopt behind a feature flag if it wins in targeted hot paths.
