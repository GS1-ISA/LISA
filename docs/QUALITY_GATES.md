# Quality Gates and Acceptance Thresholds
Last updated: 2025-09-10

Gating Levels
- Advisory: job runs, failures do not block merges.
- Enforced: failures block merges.

Initial PR CI (current status)
- Lint/format (ruff): enforced.
- Determinism: enforced (deterministic, offline test). Cross‑OS matrix runs daily (advisory).
- Typecheck (mypy): advisory → enforced after 7 clean runs on target modules.
- Tests + coverage: advisory; core coverage gate (≥80%) promotes after stability; broader ≥90% tracked nightly.
- Security (bandit, pip‑audit, gitleaks): advisory → enforced once baseline issues triaged.
- Complexity (radon): advisory with budget (most functions < 10).

## Source Code Governance

All Python source files (`**/*.py`) within the `src/`, `scripts/`, and `agent/` directories are governed by the following standard quality gates as defined in the `ci.yml` workflow:

- **Linting**: Must pass `ruff check`.
- **Formatting**: Must pass `ruff format --check`.
- **Type Checking**: Must pass `mypy` with no errors (once the gate is enforced).
- **Testing**: Must be covered by `pytest` unit or integration tests where applicable. Core logic should strive for >90% coverage.
- **Security**: Must pass `bandit` and `pip-audit` scans with no high/critical vulnerabilities.

## Test File Governance

All test files (`**/tests/**/*.py`) are considered part of the project's quality assurance framework. They are executed via `pytest` in the CI pipeline and must adhere to the same linting and formatting standards as source code.

## Configuration and Artifact Governance

Project configuration files (`.yml`, `.toml`, `.yaml`, `Dockerfile`, etc.) are governed by the principle of "working as configured." They must be parsable and are validated by the CI jobs that consume them (e.g., the `docker build` and `commitlint` jobs).

All GitHub workflow files (`.github/workflows/*.yml`) are governed by the `CI_WORKFLOWS.md` document.

Nightly
- Mutation (mutmut) curated targets; promote to gate after stability; aim ≥70% score.
- Perf: pytest‑benchmark + latency histogram; promote p95 budget once stable; fail if >10% regression vs baseline (post‑promotion).
- Memory coherence: advisory drift gate; promote to enforced after stability window; include scorecard.

Weekly
- CrossHair: advisory report; human triage.
- SBOM + Trivy: zero high/critical; treat as break-glass gate.

Dependencies & Audit Policy
- Dependency manifests: `requirements.txt`, `requirements-dev.txt`, and any `pyproject.toml` files.
- pip-audit runs in PR CI (advisory → enforced) against these manifests; remediation is required for high/critical.
- SBOM (syft) generated weekly; Trivy scans track CVEs; zero high/critical on `main` is the promotion condition for security gates.

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

Additional PR Gates
- Memory coherence: advisory drift gate + log snapshot; promote after stability window.
- Docs build: Sphinx build (advisory), enforced after stability.
- Container smoke: on significant changes, build image and curl `/metrics` (advisory), promote after stability.
- PR Metric Guard: enforced — requires a metric‑delta sentence in PR body.
- Import Discipline: advisory — disallow direct imports of `src.agent_core` from orchestrator/llm except via adapter.

Determinism Policy
- Canonical behavior validated by deterministic tests (offline path); cross‑OS matrix runs daily (advisory).
- ADR‑0003 governs optional orjson path via `CANONICAL_USE_ORJSON=1` (parity required before defaulting).
