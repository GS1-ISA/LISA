Last updated: 2025-09-01T21:42:39Z

POC Q11 — Determinism & Performance (orjson vs stdlib)

Determinism: OK for stdlib and orjson
stdlib: 26212.3 ops/s, 0.038 ms/op over 20000 iters
orjson: 353912.9 ops/s, 0.003 ms/op over 20000 iters
Speedup: 13.50x
