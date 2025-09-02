Title: Audit Report — Executive Summary
Last updated: 2025-09-02
## Audit Report — Executive Summary

- Rules: 1410 | PASS: 138 ✅ | WARN: 10 ⚠️ | FAIL: 1262 ❌
- Overall Rule Confidence: 10.2 %
- CI Gates: Present 15, Enforced 5, Advisory 10
- Inventory size: 3020 files

### Dashboard
- Lint/Type/Tests/Sec: present (promotion pending for some gates)
- Observability: /metrics and histograms present (api_server.py sha=490daef0d2a40bd000f3478adb65ada54e6ccd8421c361b2f64b4d1a0715f147)
- Container: non-root + healthcheck present (Dockerfile sha=3504e4a1a9a2c2b83ef9b3c4a138745653bcc8cbd29f2c812fe1e2e68438f44b)
- Determinism: canonical writer + snapshot present (json_canonical.py sha=b6875cc74a05119e8c905f5925a71d44bc27915980c68148cabf7f74b3a0da1c)
- Event-driven deep checks: significance trigger and semgrep wired (ci.yml sha=bec7b6e544106921ab9a91acfd124747239bba57a6967d8dfce6624fb073668f)

### Go/No-Go Recommendation
- Recommendation: CONDITIONAL (AMBER) — Fix priority items in remediation plan, then GO
