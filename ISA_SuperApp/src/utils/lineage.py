from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class LineageRecord:
    run_id: str
    ts: float
    inputs: Mapping[str, str]
    outputs: Mapping[str, str]
    context: Mapping[str, Any]


def record_lineage(
    inputs: Mapping[str, str],
    outputs: Mapping[str, str],
    *,
    run_id: str | None = None,
    context: Mapping[str, Any] | None = None,
    log_path: str | Path = ".lineage/log.jsonl",
) -> str:
    """Append a lineage record to JSONL.

    inputs/outputs: mapping of name -> sha256 (file or content hashes)
    returns the run_id.
    """
    rid = run_id or str(uuid.uuid4())
    ctx = dict(context or {})
    ctx.setdefault("cwd", os.getcwd())
    ctx.setdefault("env", {})
    rec = LineageRecord(run_id=rid, ts=time.time(), inputs=inputs, outputs=outputs, context=ctx)
    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
    return rid
