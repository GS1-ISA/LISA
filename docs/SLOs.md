# Service Level Objectives (Initial)
Last updated: 2025-09-02

Scope: API (FastAPI) and Validator endpoint.

Metrics
- Request rate, 5xx error rate, latency histograms (P50, P95, P99), saturation (CPU/mem when available).

Initial SLOs
- Availability: 99.5% monthly (API endpoints).
- Latency: P95 < 200ms for simple GETs; P95 < 500ms for /validate.
- Error budget: 0.5% monthly; burn-rate alerts at 2× and 5×.

Alert Tests
- Synthetic failures/lags in non-prod to validate alert pipelines.

Review Cadence
- Monthly SLO review; adjust targets as the system matures.
