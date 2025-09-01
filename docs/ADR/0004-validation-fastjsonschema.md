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

