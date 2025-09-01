import logging
import os
import sys


def _install_trace_log_factory() -> None:
    """Augment log records with trace/span ids if OpenTelemetry is present.

    Adds `trace_id` and `span_id` attributes to all LogRecords so formatters can
    include them without KeyError.
    """
    try:
        from opentelemetry.trace import get_current_span  # type: ignore
    except Exception:
        # Install a factory that still provides empty fields
        def factory(record: logging.LogRecord) -> logging.LogRecord:  # type: ignore[override]
            record.trace_id = ""
            record.span_id = ""
            return record

        logging.setLogRecordFactory(factory)  # type: ignore[arg-type]
        return

    old_factory = logging.getLogRecordFactory()

    def factory(*args, **kwargs):  # type: ignore[override]
        record = old_factory(*args, **kwargs)  # type: ignore[misc]
        try:
            span = get_current_span()
            ctx = span.get_span_context() if span is not None else None
            if ctx and getattr(ctx, "is_valid", False):
                record.trace_id = format(ctx.trace_id, "032x")
                record.span_id = format(ctx.span_id, "016x")
            else:
                record.trace_id = ""
                record.span_id = ""
        except Exception:
            record.trace_id = ""
            record.span_id = ""
        return record

    logging.setLogRecordFactory(factory)  # type: ignore[arg-type]


def setup_logging():
    level = os.getenv("ISA_LOG_LEVEL", "INFO").upper()
    _install_trace_log_factory()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | trace=%(trace_id)s span=%(span_id)s | %(message)s",
        stream=sys.stdout,
    )
