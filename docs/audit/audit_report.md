## Audit Report — Executive Summary

- Rules: 1410 | PASS: 138 ✅ | WARN: 10 ⚠️ | FAIL: 1262 ❌
- Overall Rule Confidence: 10.2 %
- CI Gates: Present 15, Enforced 5, Advisory 10
- Inventory size: 8432 files

### Dashboard
- Lint/Type/Tests/Sec: present (promotion pending for some gates)
- Observability: /metrics and histograms present (api_server.py sha=9e8ca6db32717b42a053880777bcf24018f0ab7eb2a57940b9fd334d982e0fd9)
- Container: non-root + healthcheck present (Dockerfile sha=3504e4a1a9a2c2b83ef9b3c4a138745653bcc8cbd29f2c812fe1e2e68438f44b)
- Determinism: canonical writer + snapshot present (json_canonical.py sha=b6875cc74a05119e8c905f5925a71d44bc27915980c68148cabf7f74b3a0da1c)
- Event-driven deep checks: significance trigger and semgrep wired (ci.yml sha=d9b727bd10aa7ff3ca3da5d5d1b5ac4290dc8d7d37cc1713a88e1b83e2184686)

### Go/No-Go Recommendation
- Recommendation: CONDITIONAL (AMBER) — Fix priority items in remediation plan, then GO
