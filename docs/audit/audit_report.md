## Audit Report — Executive Summary

- Rules: 528 | PASS: 100 ✅ | WARN: 11 ⚠️ | FAIL: 417 ❌
- Overall Rule Confidence: 20.2 %
- CI Gates: Present 15, Enforced 5, Advisory 10
- Inventory size: 358 files

### Dashboard
- Lint/Type/Tests/Sec: present (promotion pending for some gates)
- Observability: /metrics and histograms present (api_server.py sha=)
- Container: non-root + healthcheck present (Dockerfile sha=9dddb13a4f1e3d02a5efce8511ec0521cff4dd32bd1830c4e3021d9a8f291713)
- Determinism: canonical writer + snapshot present (json_canonical.py sha=)
- Event-driven deep checks: significance trigger and semgrep wired (ci.yml sha=9a31077bab52699cc969220e2c1146b385501b1ce53396f96198c000723a5458)

### Go/No-Go Recommendation
- Recommendation: CONDITIONAL (AMBER) — Fix priority items in remediation plan, then GO
