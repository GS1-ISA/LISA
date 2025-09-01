#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
from statistics import mean

from ISA_SuperApp.src.utils.json_canonical import canonical_dumps


def bench(label: str, use_orjson: bool, iters: int = 20000) -> float:
    os.environ["CANONICAL_USE_ORJSON"] = "1" if use_orjson else "0"
    # medium-size object
    obj = {
        "a": 1,
        "b": 2,
        "nested": {
            "x": "ä",
            "y": list(range(20)),
        },
        "list": [{"i": i, "v": i * 2} for i in range(50)],
    }
    # warmup
    for _ in range(500):
        canonical_dumps(obj)
    # measure
    t0 = time.perf_counter()
    for _ in range(iters):
        canonical_dumps(obj)
    t1 = time.perf_counter()
    dur = t1 - t0
    print(f"{label}: {iters/dur:.1f} ops/s, {dur*1000/iters:.3f} ms/op over {iters} iters")
    return iters / dur


def determinism_check() -> None:
    obj = {"b": 2, "a": 1, "nested": {"y": [3, 2, 1], "x": "ä"}}
    os.environ["CANONICAL_USE_ORJSON"] = "0"
    s1 = canonical_dumps(obj)
    s2 = canonical_dumps(obj)
    assert s1 == s2
    os.environ["CANONICAL_USE_ORJSON"] = "1"
    s3 = canonical_dumps(obj)
    s4 = canonical_dumps(obj)
    assert s3 == s4
    print("Determinism: OK for stdlib and orjson")


def main() -> int:
    determinism_check()
    base = bench("stdlib", use_orjson=False)
    try:
        import orjson  # noqa: F401

        fast = bench("orjson", use_orjson=True)
        print(f"Speedup: {fast/base:.2f}x")
    except Exception as e:
        print(f"orjson not available or failed to import: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

