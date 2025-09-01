# Metrics & Monitoring
Last updated: 2025-09-02

- `/metrics` endpoint exposes counters & gauges.
- Extend with histograms and structured logs for production.

## OpenTelemetry (Optional Tracing)

- Enable by setting `OTEL_ENABLED=1` in the environment.
- Configure exporter endpoint with `OTEL_EXPORTER_OTLP_ENDPOINT` (default `http://127.0.0.1:4318`).
- The server auto-instruments FastAPI and outgoing requests when enabled; spans are exported via OTLP/HTTP.
- Logs include `trace_id` and `span_id` fields when OpenTelemetry is present.

### One-command tracing (Jaeger)

- Start local Jaeger with OTLP receiver:

```
docker compose -f infra/otel/docker-compose.yml up -d
```

- Enable tracing in a separate shell and run the API:

```
export OTEL_ENABLED=1
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
make api
```

- Open Jaeger UI: http://127.0.0.1:16686 and search for `service.name = ISA_SuperApp`.

- Stop Jaeger:

```
docker compose -f infra/otel/docker-compose.yml down
```
