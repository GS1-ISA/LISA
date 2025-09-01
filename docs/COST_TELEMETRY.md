Title: Cost Telemetry & Budgets (FinOps)

Goal: Track and reduce spend for APIs/LLMs/storage/compute with minimal overhead.

Principles
- Attribute costs to features and experiments; measure unit economics (e.g., $ per 1k items).
- Prefer caching, batching, and nightly jobs for heavy/expensive runs.
- Define budgets and alerts; fail closed if limits hit (feature flags).

Implementation Sketch
- API/LLM calls: Add a lightweight logger that records provider, model, tokens, $ estimate, latency, and feature flag; aggregate weekly.
- Storage/Compute: Periodic snapshots (cloud CLI or local metrics) stored as artifacts.
- Reporting: Weekly CI job collates costs and trends; tie to promotion decisions.

Acceptance
- Weekly cost report artifact exists (API/LLM totals, $/1k items, cache hit rate).
- Budgets and alerts configured for costly features; PRs must not exceed budget without override.

