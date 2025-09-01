# Metrics & Monitoring
Last updated: 2025-09-02

- `/metrics` endpoint exposes counters & gauges.
- Extend with histograms and structured logs for production.

## OpenTelemetry (Optional Tracing)

- Enable by setting `OTEL_ENABLED=1` in the environment.
- Configure exporter endpoint with `OTEL_EXPORTER_OTLP_ENDPOINT` (default `http://127.0.0.1:4318`).
- The server auto-instruments FastAPI and outgoing requests when enabled; spans are exported via OTLP/HTTP.
- Logs include `trace_id` and `span_id` fields when OpenTelemetry is present.
