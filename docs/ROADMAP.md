Title: Program Roadmap — Tracks, Phases, and Gates

Purpose: Provide a holistic roadmap for building a self-improving, production-grade agentic platform and ESG/ISA_C data system. Organized by tracks and phased milestones with gates.

Phases
- Phase 0 — Discovery: tool choices, risks, success metrics, ADRs
- Phase 0.5 — Knowledge Gaps Research: formulate 30 research questions; evaluate external tools/methods/services/repos that could accelerate development and quality; time‑boxed micro‑POCs; adopt high‑ROI items
- Phase 1 — Foundations: repo unification, builds, quality gates (initial), agent roles
- Phase 2 — Alpha: typing, tests, mapping matrix, NeSy pilots (shadow mode)
- Phase 3 — Beta Hardening: determinism, performance, observability, security gates
- Phase 4 — GA Readiness: CI/CD, packaging, docs, SLOs, privacy & compliance
- Phase 5 — Scale & Optimize: cost controls, resilience, automation, vendor adapters

Track A — Product & UX
- Outcomes: Clear value stories, usable flows, accessible UI, measurable user success.
- Phase 0–1: UX heuristics, base flows; define personas, journeys, and success KPIs.
- Phase 2–3: A11y (WCAG 2.1 AA), content style, error messages; telemetry on UX frictions.
- Phase 4–5: Usability tests; i18n readiness; UX quality gates in PR review.
Refs: docs/TODO.md

Track B — Data & Domain (ISA_C, ESG, GDSN)
- Outcomes: Authoritative schemas, mapping matrix, data quality gates.
- Phase 1–2: Mapping matrix, schema validation; golden datasets.
- Phase 3: Deterministic outputs, snapshot tests; Great Expectations suites.
- Phase 4–5: Data catalog/lineage, documented ownership and retention.
Refs: docs/TODO.md; docs/ULTIMATE_PLAN.md

Track C — NeSy & Reasoning
- Outcomes: Explainable gap detection and compliance reasoning.
- Phase 2: ESG‑BERT + rules, LNN MVP; SenticNet optional.
- Phase 3: Nightly evals; promote stable gates (LNN) to PR CI.
- Phase 4–5: DeepProbLog pilot; research (NeurASP, DON) offline.
Refs: docs/TODO_NeSy.md

Track D — Agentic System
- Outcomes: Planner/Builder/Verifier/Critic with safety and rewards.
- Phase 1: Roles, safety policies, dry-run job.
- Phase 2–3: Reward logs, bandit strategies; eval suite; Tier‑1 autonomy.
- Phase 4–5: SLOs, alerting; guarded Tier‑2 for low-risk edits.
Refs: docs/AGENTIC_ARCHITECTURE.md; docs/AGENTIC_GOALS.md; docs/TODO.md

Track E — Architecture & Platform
- Outcomes: Clean monorepo, packages, infra, hermetic builds.
- Phase 1: Target layout, root pyproject, locks, Makefile.
- Phase 3–4: Docker images, compose demo; artifacts signing roadmap.
 - Containerization & Orchestration: Baseline Docker (non-root, healthcheck), docker-compose demo; K8s readiness (readiness/liveness probes, config via env, statelessness, HPA considerations).
 - Phase 5: Adapter layer for managed runtimes (e.g., DeepSeek).
 - Targeted Refactor: API layering (routers/services), proper entrypoint; health/readiness probes; centralized config.
Refs: docs/ULTIMATE_PLAN.md; docs/TODO.md

Track R — Knowledge Gaps & Ecosystem Research
- Outcomes: Identify critical knowledge gaps, external capabilities, and integrations that maximize ROI without bloat.
- Phase 0.5: Produce 30 research questions (agentic loops, NeSy, LLMOps, data quality/governance, privacy/security, observability/SRE, performance, UX, CI/CD); build evaluation rubric (Impact, Ease, Maturity, Alignment, Cost); shortlist tools/services/frameworks/repos; run 3–5 micro‑POCs.
- Phase 2–3: Adopt and integrate the best candidates behind adapters/feature flags; write ADRs; retire lower‑value options.
- Phase 4–5: Continuous scanning with quarterly reviews; ensure parity tests and vendor lock‑in protections.
Refs: docs/TODO.md (Knowledge Gaps Research); docs/RESEARCH_KNOWLEDGE_GAPS.md

Track F — Quality Engineering
- Outcomes: Style/lint/type gates, high coverage, mutation/fuzz in nightly.
- Phase 1: ruff enforced; mypy/tests advisory.
- Phase 2–3: ≥90% coverage; flip type/tests to enforced; nightly mutation ≥70%.
- Phase 4–5: Formal checks (CrossHair) curated weekly; complexity budgets.
 - Test Performance: xdist parallelization; flaky test triage; quarantine list for nightlies.
 - Process: Definition of Done + PR template enforced on PRs.
Refs: docs/QUALITY_GATES.md; docs/TODO.md

Track G — Security & Compliance
- Outcomes: Secure code, deps, artifacts; clear policies and triage.
- Phase 1: bandit/pip-audit/gitleaks advisory in CI.
- Phase 3: Trivy/SBOM weekly; zero high/critical to promote to gates.
- Phase 4–5: Threat modeling (STRIDE), pen-test readiness, SOC2‑style controls.
Refs: docs/TODO.md

Track H — Privacy & Responsible AI
- Outcomes: DPIA, data minimization, PII tagging, Responsible AI guardrails.
- Phase 2: Data classification, retention policy draft, audit logging design.
- Phase 3–4: DPIA; DSR (access/delete) playbooks; bias/abuse evals.
- Phase 5: Automated privacy tests in CI (redaction checks), transparency docs.
Refs: docs/TODO.md

Track I — Observability & SRE
- Outcomes: Golden signals, dashboards, SLOs + error budgets.
- Phase 2–3: Structured logs, Prometheus metrics (/metrics), basic Grafana. Implement now for request count/error/latency histograms with exemplars and correlation IDs.
- Phase 4: SLOs and burn-rate alerts; runbooks and incident drills.
- Phase 5: Tracing on critical paths; chaos drills, load/capacity modeling.
 - Enhancements: orjson logging, histogram metrics with exemplars, correlation IDs throughout.
Refs: docs/TODO.md

Track J — Performance & Capacity
- Outcomes: Determinism, speedups, predictable scaling.
- Phase 2–3: Baselines, ≥30% speedup; caching and parallelism.
 - Deep Enhancements:
   - JSON: orjson for dumps and canonical writer; evaluate fastjsonschema and Pydantic v2 compiled validators.
   - Benchmarks to date: Q11 shows orjson ~13.5× faster with parity; Q12 shows Pydantic v2 faster for simple schema (retest on real schemas).
   - Data: Polars prototypes for heavy transforms; optional DuckDB for large joins.
   - I/O: streaming CSV/JSONL and compressed inputs; avoid large intermediates.
   - Concurrency: safe multiprocessing for CPU-bound, asyncio/httpx for I/O-bound; document limits.
   - Tests: pytest-xdist for parallelization; move slow suites to nightly.
   - Memory: tracemalloc snapshots; fix top leaks; monitor RSS.
 - Phase 4–5: Capacity planning, load tests, cost/perf budgets.
Refs: docs/ULTIMATE_PLAN.md; docs/TODO.md

Track K — CI/CD & Release Engineering
- Outcomes: Reliable pipelines, releases, provenance.
- Phase 1: PR CI + scheduled jobs.
- Phase 3–4: Release automation (semver/changelog); signed artifacts roadmap.
- Phase 5: Preview envs per PR; SLSA controls.
Refs: .github/workflows/*; docs/CI_WORKFLOWS.md; docs/TODO.md

Track L — DevEx & Tooling
- Outcomes: 5‑minute onboarding, smooth local dev.
- Phase 1: Makefile, pre-commit.
- Phase 3–4: Devcontainer, VS Code tasks; one‑command demo.
- Phase 5: Templates, contribution analytics.
Refs: docs/TODO.md

Track M — MLOps/LLMOps
- Outcomes: Reproducible prompts/models, evals, and rollout.
- Phase 2: Prompt/version registry, eval harness for LLM changes.
- Phase 3–4: Canary evals, rollback; safety filters/tests.
- Phase 5: Model registry integration, drift monitoring.
Refs: docs/TODO.md

Track N — Data Governance
- Outcomes: Catalog, lineage, ownership, retention, and quality.
- Phase 2–3: Ownership/stewardship, PII tagging, lineage capture (run IDs, input/output hashes; consider OpenLineage).
- Phase 4–5: Catalog UI (or export), policy checks in CI.
Refs: docs/TODO.md

Track O — Cost & FinOps
- Outcomes: Budgeting and efficiency across compute/API/storage.
- Phase 2: Cost telemetry (LLM/API calls, storage), unit economics.
- Phase 3–4: Budgets/alerts; caching to reduce spend; weekly reports.
- Phase 5: Optimization backlog; contract/vendor renegotiations.
Refs: docs/TODO.md

Track P — Risk, Governance & Legal
- Outcomes: ADRs, CODEOWNERS, tech‑debt ledger; licensing & export compliance.
- Phase 1: ADRs, CODEOWNERS, TECH_DEBT.md; license scan.
- Phase 3–4: DPIA/DSR alignment; legal review of third‑party terms.
- Phase 5: Periodic audits; policy automation.
Refs: docs/ADR/*; docs/TODO.md

Milestone Gates (Examples)
- Gate A: ruff enforced; PR CI green; monorepo ready.
- Gate B: coverage ≥90% (core), mypy enforced, mapping matrix complete.
- Gate C: ≥30% perf gain; LNN validator promoted to PR CI.
- Gate D: security zero high/critical; SBOM and Trivy weekly green.
- Gate E: GA readiness — SLOs, privacy DPIA, release automation completed.

Critical Path & Gate-Flip Conditions
- CP-1 (to Gate A): Monorepo target layout approved → Migration map finalized → ruff enforced in CI.
- CP-2 (to Gate B): Tests stabilized (core coverage ≥90%) → mypy green on target modules → flip mypy/tests to enforced.
- CP-3 (to Gate C): Baseline perf + optimizations landed (≥30% runtime reduction) → perf budget guard on PR.
- CP-4 (to Gate D): Security baseline triaged → no high/critical in Bandit/pip-audit/Trivy → flip to enforced.
- CP-5 (to Gate E): DPIA approved; SLOs/alerts verified; release workflow emits signed artifacts.

Gate Promotion Rule
- A check flips from advisory to enforced only after 7 consecutive green nightly runs meeting thresholds, and no open waivers in TECH_DEBT.md.

Impact Horizon Notes
- Short term (weeks 1–2): Developer velocity gains (ruff/pre-commit/Makefile), CI stability, research questions framed (Phase 0.5).
- Medium term (weeks 3–6): Quality gates (typing/tests/security) enforced, deterministic outputs, performance uplift, NeSy MVPs in shadow.
- Long term (weeks 7+): SLO-driven operations, cost controls, managed runtime adapters, gradual autonomy tier promotion.
