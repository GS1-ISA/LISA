from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from uuid import uuid4


def _json_formatter(record: logging.LogRecord) -> str:
    payload = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "level": record.levelname,
        "name": record.name,
        "msg": record.getMessage(),
        "module": record.module,
        "line": record.lineno,
        "cid": getattr(record, "cid", None) or os.getenv("CORRELATION_ID") or str(uuid4()),
    }
    return json.dumps(payload, ensure_ascii=False)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        return _json_formatter(record)


def setup_logging(level: str | None = None, log_file: str | None = None) -> None:
    level = level or os.getenv("ISA_LOG_LEVEL", "INFO")
    log_file = log_file or os.getenv("ISA_LOG_FILE", "logs/isa_c.log")
    os.makedirs("logs", exist_ok=True)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(JsonFormatter())
    root.addHandler(stream)

    rotate = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    rotate.setFormatter(JsonFormatter())
    root.addHandler(rotate)
