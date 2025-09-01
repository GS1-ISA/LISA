## Phase 9 — Scenario Simulation

This document simulates five critical user journeys from unit → integration → deploy and checks compliance against documented rules. Evidence cites file paths, line numbers, and sha256 from docs/audit/inventory.csv.

### Scenario 1: Start API and expose metrics
- Steps:
  - Launch FastAPI app (uvicorn). Access /metrics for Prometheus scrape.
  - Container healthcheck probes /metrics.
- Evidence:
  - ISA_SuperApp/src/api_server.py:112 (sha256=9e8ca6db32717b42a053880777bcf24018f0ab7eb2a57940b9fd334d982e0fd9) `@app.get("/metrics")`
  - ISA_SuperApp/src/api_server.py:75,79–84,92,105–106 (metrics middleware and counters)
  - ISA_SuperApp/Dockerfile:20 (sha256=3504e4a1a9a2c2b83ef9b3c4a138745653bcc8cbd29f2c812fe1e2e68438f44b) `HEALTHCHECK ... /metrics`
- Status: ✅ PASS — Observability rules and container healthcheck in place.

### Scenario 2: Validate record via /validate endpoint
- Steps:
  - Post JSON payload to /validate; expect violations for insufficient geo precision; expect pass for ≥6 decimals.
- Evidence:
  - ISA_SuperApp/src/api_server.py:65–66 (sha256=9e8ca6db32717b42a053880777bcf24018f0ab7eb2a57940b9fd334d982e0fd9) `@app.post("/validate")`
  - ISA_SuperApp/tests/unit/test_api_validate.py:10,18 (sha256=2c4427342e30922823e4e8d14b9793a73b8341b8f1f1f6f37b6215318e6dad56)
- Status: ✅ PASS — Endpoint and tests satisfy NeSy validator rules.

### Scenario 3: Deterministic canonical JSON
- Steps:
  - Serialize object with canonical_dumps; verify snapshot matches; optionally enable orjson via env.
- Evidence:
  - ISA_SuperApp/src/utils/json_canonical.py:16,41–44 (sha256=b6875cc74a05119e8c905f5925a71d44bc27915980c68148cabf7f74b3a0da1c)
  - ISA_SuperApp/tests/unit/test_snapshot_canonical_sample.py:6,11 (sha256=01a58339974adeac3d87da3ab1d3dc03c6e23be98613d538e896fced1603bb04)
- Status: ✅ PASS — Determinism and optional orjson path (ADR‑0003) implemented.

### Scenario 4: Small PR pipeline (non‑significant)
- Steps:
  - Run ruff format/check, mypy (advisory), pytest (advisory), coverage XML + delta (advisory), bandit/pip‑audit (present), radon (advisory), type coverage artifact.
- Evidence (.github/workflows/ci.yml sha256=d9b727bd10aa7ff3ca3da5d5d1b5ac4290dc8d7d37cc1713a88e1b83e2184686):
  - Lines 63–64 ruff; 65–74 mypy + linecount; 80–97 pytest + coverage XML + delta; 98–105 bandit/pip‑audit; 109 radon.
- Status: ✅ PASS (advisory where planned) — Matches QUALITY_GATES with promotion rules.

### Scenario 5: Significant PR pipeline
- Steps:
  - Changes exceed thresholds or touch critical paths → run semgrep and extended tests; summarize significance reason.
- Evidence:
  - .github/workflows/ci.yml:42 significance_trigger; 110–120 semgrep and extended tests.
- Status: ✅ PASS — Event‑driven deep checks enabled per CI_WORKFLOWS.

No violations detected in these journeys given current scope (no staging/prod deployment simulation). For container build/run and docs build, we recommend adding optional gates when ready.

