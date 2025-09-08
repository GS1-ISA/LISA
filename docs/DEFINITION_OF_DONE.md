Title: Definition of Done (DoD) — Project-Wide
Last updated: 2025-09-02

Purpose: Ensure every change ships with quality, performance, safety, and documentation, aligned with the agentic, evidence-first philosophy.

Applies To: All PRs and changes (code, data, config, docs). The PR template references this checklist.

Core DoD (All Changes)
- [ ] Lint clean (ruff) and formatted
- [ ] Typecheck clean (mypy) or waivers documented in TECH_DEBT.md
- [ ] Tests updated/added; PR CI test job green (advisory until gates flip)
- [ ] Determinism preserved (snapshots/canonical outputs, where applicable)
- [ ] Security checks reviewed (Bandit/pip-audit output; zero high/critical on main)
- [ ] Docs updated (README/CHANGELOG/runbooks as relevant)
- [ ] Rollback notes and risk in PR description; no destructive migrations without plan
- [ ] Adapters/feature flags used for new integrations; defaults safe (OFF)

Code Changes (Backend/API)
- [ ] Guard tests for public surface/routers; behavior unchanged unless specified
- [ ] Observability: structured logs with correlation IDs; metrics for critical paths
- [ ] Config via typed settings; no secrets in code; .env.example updated
- [ ] Performance impact considered; if marked critical, include benchmark delta and perf budget status

Data/Mapping Changes
- [ ] Schema/mapping matrix updated; data quality checks pass (no new critical failures)
- [ ] Snapshot/golden outputs updated intentionally; review includes diff of canonical outputs
- [ ] Large datasets handled via LFS/DVC or artifacts (no repo bloat)

Docs/Process Changes
- [ ] Docs build; links and examples tested
- [ ] PR template/DoD alignment verified
- [ ] Autonomy: changes follow Lead Developer mode (act without asking); escalation only per policy triggers

Research/NeSy Changes
- [ ] R2P artifacts attached: search ledger, POC protocol, replication notes
- [ ] Decision (Adopt/Hold/Reject) recorded; ADR if adopted; adapter+flag integration
- [ ] Shadow A/B plan for 7-day stability documented before gating

Acceptance
- PR passes all applicable checkboxes above; any exceptions documented with reason and timeline in TECH_DEBT.md; CI artifacts (coverage/type) uploaded.
