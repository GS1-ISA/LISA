# Ultimate Agentic Development Plan — Checklists and Acceptance Criteria
Last updated: 2025-09-02

Purpose: Deliver a self-improving, high-quality, reproducible monorepo and agent system. This document encodes atomic checklists, acceptance criteria, success metrics, and review gates.

Scope: Applies to repository unification, build/deps, quality gates, security, CI/CD, agentic loops, and release operations.

Status Legend: [ ] pending  [~] in-progress  [x] completed

1) Inception and Governance
- [x] Define toolchain and policies (uv, ruff, mypy, pytest, semgrep, bandit, pip-audit, gitleaks, trivy)
- [x] Create ADR stubs for tooling and safety
- [ ] Document reward model and autonomy tiers
Acceptance:
- Clear ADRs exist for tooling and safety with owners and rationale.
- Reward model draft includes positive/negative signals and normalization.

2) Monorepo Unification (Plan Only in this commit)
- [ ] Target layout defined: apps/superapp, packages/isa_c_full, packages/isa_c_mapping, packages/agent_core, artifacts, infra, docs
- [ ] Migration map from current folders to targets
- [ ] Root README and CONTRIBUTING outline the structure
Acceptance:
- Migration document lists every move and import change.
- Superapp runs smoke test post-migration.

3) Build System & Dependencies
- [ ] Root pyproject for shared tool config (no package build yet)
- [ ] uv lock strategy and constraints policy documented
- [ ] Deps report script planned (not executed here)
Acceptance:
- One authoritative lock tool and constraints policy; no duplicate managers.

4) Style & Lint
- [x] Consolidate on ruff for lint+format in CI
- [x] Pre-commit hooks planned with ruff and mypy
- [ ] Enforce formatting in CI on PRs
Acceptance:
- `ruff check` and `ruff format --check` pass on default branch.

5) Typing & Schemas
- [ ] mypy gate (strict on libraries) configured in CI
- [ ] Type coverage metric collected in CI
- [ ] JSON Schemas for agent traces and plans planned
Acceptance:
- mypy runs in CI; type coverage threshold recorded.

6) Testing Strategy
- [ ] Unit/integration/property tests run on PRs
- [ ] Mutation/fuzz/benchmarks scheduled nightly
- [ ] CrossHair targeted weekly (pure mappers)
Acceptance:
- Coverage >= 90% gate (core), nightly mutation score >= 70% reported.

7) Mapping Correctness
- [ ] Mapping matrix generation job planned (CSV/HTML)
- [ ] CI check for gaps/collisions planned
Acceptance:
- No critical unmapped fields without waiver.

8) Determinism
- [ ] Canonical JSON writer policy documented
- [ ] Snapshot tests policy documented
Acceptance:
- Byte-for-byte stable snapshots for canonical outputs.

9) Performance & Parallelism
- [ ] Baseline profiling job planned (cProfile/py-spy)
- [ ] Perf budgets in CI (regression guard) planned
- [ ] Parallel runner & content-hash cache planned
Acceptance:
- >=30% target speedup on workload; CI fails on budget regressions.

10) Observability
- [ ] Structured logging schema plan (correlation IDs)
- [ ] Prometheus metrics and Grafana dashboard plan
Acceptance:
- Metrics for throughput, latency, error classes; dashboard JSON stored.

11) Security & Supply Chain
- [x] SAST/SCA tools selected (bandit, pip-audit, gitleaks, trivy)
- [ ] SBOM generation scheduled in CI (syft)
- [ ] OpenSSF Scorecard job planned
Acceptance:
- No high/critical findings; SBOM artifact per release.

12) CI/CD
- [x] PR CI workflow skeleton added
- [x] Nightly/weekly jobs skeletons added
- [ ] Release workflow and changelog automation planned
Acceptance:
- CI green on default; scheduled jobs publish artifacts.

13) Developer Experience
- [ ] Makefile (root) stubs with agent-aware tasks planned
- [ ] Devcontainer and VS Code tasks planned
Acceptance:
- New dev can run one-command demo and CI dry run in <=5 minutes.

14) Data Quality
- [ ] Expectation suites plan (Great Expectations or pydantic-core)
- [ ] CI gate on data quality planned
Acceptance:
- >=99% pass for critical expectations.

15) Packaging & Runtime
- [ ] Wheel packaging plan for packages/isa_c_full and packages/isa_c_mapping
- [ ] Docker image plan for apps/superapp (non-root, healthcheck)
Acceptance:
- docker compose demo brings up end-to-end stack.

16) Agentic Architecture — Roles and Safety
- [x] Document planner, builder, verifier, critic, reward aggregator, meta-learner
- [x] Policy engine and safety guardrails (allowlists, rate limits) documented
- [ ] Autonomy tiers and promotion gates documented
Acceptance:
- Policies and autonomy tiers are explicit; kill-switch defined.

17) Agent Learning & Rewards
- [x] Initial reward model outlined
- [ ] Bandit strategy set enumerated and evaluators planned
- [ ] Replay log schema defined (JSONL)
Acceptance:
- Agent eval win-rate targets defined; logs schema validated.

18) SLOs & Alerting
- [ ] SLOs for agent success, revert rate, latency
- [ ] Alert routes (Slack/PagerDuty) planned
Acceptance:
- Alert tests pass in CI; burn-rate panels configured.

19) Cutover Plan
- [ ] Tiered autonomy rollout (T0→T2) with gates
- [ ] Rollback playbooks and repro pack policy
Acceptance:
- Post-merge reverts <1% 30-day rolling; repro packs attached on failures.

20) Managed Runtime Migration
- [ ] Adapter abstraction for LLM/tooling (DeepSeek-ready)
- [ ] Parity tests for plan/diff consistency across engines
Acceptance:
- No regression in eval win-rate when switching engines.

Appendix A — Success Metrics
- DORA: on-demand deploys; <1 day lead time; ≤15% CFR; <1h MTTR
- Tests: ≥90% cov (core); mutation ≥70% nightly; <1% flaky
- Types: ≥90% type coverage (libs strict)
- Security: 0 high/critical; OSSF ≥8.0; signed artifacts
- Perf: ≥30% speedup; CI perf budgets enforced
- Data: ≥99% expectations; zero unapproved schema drifts
- Agent: Tier-1 win-rate ≥70%; Tier-2 ≥85% low-risk; <1% revert
