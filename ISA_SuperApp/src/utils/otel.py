from __future__ import annotations

import os
from typing import Any


def init_tracing(app: Any, service_name: str = "ISA_SuperApp") -> bool:
    """Initialize OpenTelemetry tracing for FastAPI if enabled and available.

    Controlled by env `OTEL_ENABLED=1`. Exports to OTLP endpoint from
    `OTEL_EXPORTER_OTLP_ENDPOINT` (default http://127.0.0.1:4318).

    Returns True if instrumentation was attached, False otherwise.
    """
    if os.getenv("OTEL_ENABLED", "0") != "1":
        return False
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4318")
        resource = Resource.create({"service.name": service_name})

        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        # Instrument FastAPI app and outgoing requests
        FastAPIInstrumentor.instrument_app(app)
        RequestsInstrumentor().instrument()
        return True
    except Exception:
        return False

