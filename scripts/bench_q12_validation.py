#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field, ValidationError

try:
    import fastjsonschema
except Exception:
    fastjsonschema = None


class Item(BaseModel):
    id: int = Field(ge=1)
    name: str
    price: float = Field(ge=0)
    tags: list[str] = []


SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string"},
        "price": {"type": "number", "minimum": 0},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["id", "name", "price"],
    "additionalProperties": False,
}


def bench_pydantic(iters: int = 20000) -> float:
    ok = {"id": 1, "name": "x", "price": 1.23, "tags": ["a", "b"]}
    # warmup
    for _ in range(200):
        Item.model_validate(ok)
    t0 = time.perf_counter()
    for _ in range(iters):
        Item.model_validate(ok)
    t1 = time.perf_counter()
    dur = t1 - t0
    print(f"pydantic: {iters / dur:.1f} ops/s, {dur * 1000 / iters:.3f} ms/op")
    return iters / dur


def bench_fastjsonschema(iters: int = 20000) -> float:
    if fastjsonschema is None:
        print("fastjsonschema not installed; skipping")
        return 0.0
    validate = fastjsonschema.compile(SCHEMA)
    ok = {"id": 1, "name": "x", "price": 1.23, "tags": ["a", "b"]}
    for _ in range(200):
        validate(ok)
    t0 = time.perf_counter()
    for _ in range(iters):
        validate(ok)
    t1 = time.perf_counter()
    dur = t1 - t0
    print(f"fastjsonschema: {iters / dur:.1f} ops/s, {dur * 1000 / iters:.3f} ms/op")
    return iters / dur


def parity_checks() -> None:
    bad = {"id": 0, "name": "x", "price": -1}
    try:
        Item.model_validate(bad)
        print("pydantic parity: expected ValidationError, got none")
    except ValidationError:
        print("pydantic parity: ValidationError OK")
    if fastjsonschema is not None:
        validate = fastjsonschema.compile(SCHEMA)
        try:
            validate(bad)
            print("fastjsonschema parity: expected error, got none")
        except Exception:
            print("fastjsonschema parity: error OK")


def main() -> int:
    parity_checks()
    p1 = bench_pydantic()
    p2 = bench_fastjsonschema()
    if p2 > 0:
        print(f"Speed ratio fastjsonschema/pydantic: {p2 / p1:.2f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
