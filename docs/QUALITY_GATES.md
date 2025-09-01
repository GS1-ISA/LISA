Title: Quality Gates and Acceptance Thresholds

Gating Levels
- Advisory: job runs, failures do not block merges.
- Enforced: failures block merges.

Initial PR CI (advisory → enforced when stable)
- Lint/format (ruff): enforced immediately.
- Typecheck (mypy): advisory → enforced once green for 7 consecutive days.
- Tests + coverage: advisory → enforced at ≥90% coverage (core modules).
- Security (bandit, pip-audit, gitleaks): advisory → enforced once baseline issues triaged.
- Complexity (radon): advisory with budget (most functions < 10).

Nightly
- Mutation (mutmut) target ≥70% score.
- Perf budgets: fail job if >10% regression in P95 runtime.

Weekly
- CrossHair: advisory report; human triage.
- SBOM + Trivy: zero high/critical; treat as break-glass gate.

Promotion Rules
- Flip a check to enforced only after it runs green for a sustained period or has waivers documented in TECH_DEBT.md.

Gate‑Flip Conditions (Advisory → Enforced)
- Typing (mypy): 7 consecutive nightly runs with 0 errors on target modules; TECH_DEBT.md contains no open typing waivers for those modules.
- Tests + Coverage: 7 consecutive nightly runs with core coverage ≥90%, flakiness <1% (rolling 30 days); green on PR CI for a week.
- Security: No high/critical findings for 7 consecutive runs (Bandit, pip‑audit, Trivy); all secrets scans clean.
- Performance Budgets: No more than 10% P95 runtime regression vs baseline across 7 consecutive runs; budget guard enabled on PRs after this.
- LNN Validator: 100% seeded violation detection; 0 false positives on green fixtures for 7 consecutive runs; then promote to PR CI gate.

Reporting Cadence
- Weekly artifact containing: coverage, type error count, mutation score, perf P95, security findings, revert rate, and any waivers.

Break‑Glass Procedure
- For urgent fixes that must bypass gates, use a dedicated "break‑glass" label and PR template section explaining impact, risk, and rollback.
- Conditions: production outage, urgent security fix, or regulator‑mandated change with deadline.
- Requirements: all tests/linters must still run; post‑merge follow‑up issue to restore gate compliance within 72 hours.

Waiver Policy
- Waivers must be documented in TECH_DEBT.md with owner, reason, scope, and expiry date (≤30 days by default).
- CI posts a reminder when a waiver is within 7 days of expiry; expired waivers fail merges until renewed or resolved.


Additional PR Gates (Advisory → Enforced)
- Determinism snapshots: run snapshot tests for canonical JSON; flip to enforced after 7 green days.
- Docs build: build MkDocs site (if present); start advisory, then enforce.
- Container smoke: on significant changes, build Docker image and curl `/metrics`; enforce after stability.
