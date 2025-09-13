# Program Roadmap — Tracks, Phases, and Gates

Last updated: 2025-09-10

Purpose: Provide a holistic roadmap for building a self-improving, production-grade agentic platform and ESG/ISA_C data system. Organized by tracks and phased milestones with gates.

See also: ISA_VISION_OUTCOMES.md for the concise vision, outcomes, and KPIs guiding this roadmap.

Operational Plan — Phases A–D (Solo‑Dev, Measurable)

- Phase A (0–2 weeks) — Establish hard baselines and hygiene
  - Determinism: add macOS+Ubuntu snapshot matrix; attach artifacts; flip to gate after first pass is green.
  - Docs hygiene: Sphinx build job (advisory) with curated toctrees; zero “not in toctree” warnings.
  - Agent parity: write parity test list for Planner/Researcher/Synthesizer; add thin adapters; no removals yet.
  - Coverage/Mutation: reach ≥80% line and ≥60% mutation on core targets (agent_core/orchestrator) with curated mutmut set (advisory).
  - Security/SBOM: weekly Syft+Trivy jobs; keep bandit/pip‑audit 0 high severity.
  - Performance: add pytest‑benchmark for core flow; record p95; set budget advisory (<400 ms on M1).
  - Cost telemetry: emit monthly spend artifact; 80% budget alert (advisory).
  - Risk loop: maintain meta inventory + single top‑risk issue with ETA; session JSONL log appended.

- Phase B (2–4 weeks) — Unify Agent and promote checks
  - Collapse Agent implementations into `src/agent_core`; keep adapters in `src/llm` and `src/orchestrator`; remove duplicates post‑parity.
  - Promote docs build and coverage/mutation to gates after 7 clean runs; maintain determinism gate.

- Phase C (1–3 months) — Performance, Cost, R2P, Privacy
  - Meet performance budget (p95 < 400 ms, 3‑run median stable ±5%); add cost alerts; enforce R2P (ADR+adapter+flag) presence on adoption PRs; add privacy DSR tests.

- Phase D (3–6 months) — Formal, Edge, Observability, Governance
  - Hypothesis property tests for canonical writer/adapters; offline mode smoke; metrics histograms + perf budget enforcement; CODEOWNERS and waiver expiry.

Automation & Autonomy (Always-On)

- Meta Audit: weekly job generates `meta_inventory.md` + `meta_risk_xray.md` and maintains a single “Top Risk (auto)” issue.
- PR Discipline: template enforces a one-line metric delta; CI collects determinism/docs/perf/coverage/mutation artifacts.
- Stubs by Default: CI uses stub modes and adapters to keep runs offline; network-only checks live in nightly/weekly workflows.

Detailed Roadmap — Short / Medium / Long Term

Short Term (0–4 weeks)
- Gates & CI
  - Enforce determinism (DONE); daily determinism matrix (advisory).
  - Promote Docs build → enforced after 7 clean runs.
  - Promote Core coverage (agent_core, orchestrator) ≥ 80% → enforced after 7 clean runs; track ≥ 90% nightly.
  - Curated mutation: expand planner/researcher/synthesizer targets; publish score; gate after stability.
  - PR Metric Guard: enforced (requires metric‑delta sentence).
  - Import discipline: advisory guard to prevent direct agent_core imports from orchestrator/llm (adapter only).
  - CI speed-ups: pip cache, xdist, cancel in‑progress (DONE).
- Agent Architecture
  - Offline parity tests for Planner/Researcher/Synthesizer (DONE).
  - Orchestrator → agent_core adapter (DONE); exercise env switch nightly (stub mode) and de‑risk consolidation.
- Performance & Telemetry
  - Latency histogram artifact in CI; trend p95; prepare gating.
  - Perf bench via pytest‑benchmark; maintain baseline.
- Research & Knowledge
  - Ingest ISA goals PDFs locally (make pdf-index) and via manual workflow; keep Sphinx clean.
  - Seed research memory with PDF index (advisory only).
- Docs
  - ISA_VISION_OUTCOMES.md (DONE); cross-links in Charter/Roadmap/Index.
  - Onboarding references OODA meta‑prompt; Makefile utilities documented.

Acceptance (Short Term)
- Determinism enforced; docs build and core coverage clean runs ≥ 7; mutation score visible; perf_histogram.json artifacts present; PDF index artifact available; nightly adapter test green.

Medium Term (1–3 months)
- Consolidation
  - Route orchestrator/llm call‑sites through adapter; remove duplicates post‑parity.
  - Enforce adapter path via import‑guard; add static checks in PRs.
- Gates
  - Docs build: enforced.
  - Core coverage ≥ 80%: enforced; nightly reports ≥ 90% on core.
  - Mutation: promote curated threshold (e.g., ≥ 60%) to enforced for core modules.
  - Memory coherence: promote drift gate after 7 green PRs; include scorecard link.
  - Performance: enforce p95 < 400 ms budget on core paths; fail on >10% regression.
- Research→Production (R2P)
  - Define adopt/hold/reject checklist (ADR + adapter + flag + parity tests) and add CI checks.
  - Pilot “GDSN Agent” vertical: ESG→GDSN mapping for a seeded retailer dataset; include acceptance tests.
- Ontology & KG
  - Establish initial GS1 ontology schema and loading pipeline; attach provenance.
- Governance & Process
  - CODEOWNERS minimal set live; waiver-expiry convention documented and observed.

Acceptance (Medium Term)
- Adapter consolidation complete; direct imports prevented; docs/coverage/mutation/memory/perf gates enforced; GDSN Agent pilot tests pass; R2P checks active.

Long Term (3–6 / 6–12 months)
- Formal & Safety
  - Property-based tests (Hypothesis) for canonical writer/adapters; curate ghost‑code assertions on invariants.
  - Targeted CrossHair checks on pure mapping utilities.
- Offline & Edge
  - Offline mode proven (no external inference); document toggles and costs; smoke tests in CI.
- Scale & Adoption
  - Sector pilots expanded (circular textiles, retail ESG); mapping coverage/quality KPIs reported.
  - Standards workflows: co‑authoring/publisher lints; (advisory → enforced) publishing checks.
- Supply Chain & Security
  - SBOM + Trivy weekly; zero high/critical on default branch; supply‑chain attestations on release.
- Observability & SLOs
  - Dashboards for latency histograms and memory coherence; SLOs and burn‑rate alerts; runbooks.
- Releases
  - Release process (release‑please) producing wheels/images and notes; changelog increments gates’ status changes.

Acceptance (Long Term)
- Stable, self‑improving platform with enforced gates; pilots generating measurable wins; releases and security posture mature; offline path documented and tested.

Scoring Rubric (objective)

- Determinism: 9.25 = identical snapshot hashes across macOS+Ubuntu for last 7 PRs; artifacts attached; gate enforced.
- Coverage/Mutation: 9.25 = line ≥ 80%, mutation ≥ 60% on core; enforced.
- Docs Hygiene: 9.25 = zero Sphinx warnings on last 7 builds; gate ready.
- Security/Supply Chain: 9.25 = 0 high‑sev (bandit+pip‑audit) and 2 weekly SBOM+Trivy runs clean.
- Performance: 9.25 = p95 < 400 ms on M1; 3‑run median stable ±5%.
- Cost/FinOps: 9.25 = <$50/mo with 80% alert tested in CI.
- Architecture Coherence: 9.25 = single Agent source of truth + adapters; parity suite green; duplicates removed.
- Memory Coherence: 9.25 = drift ≤ 5% for last 7 PRs; gate ready.
- Dependency Hygiene: 9.25 = one manager + lock; dep report artifact weekly; net new deps ≤2/month.
- Bloat Control: 9.25 = repo growth ≤2%/week for 4 weeks; LFS policy enforced.
- Observability: 9.25 = structured logs + metrics histograms; perf budget check active in CI.

Verification

- CI artifacts serve as the sole source of truth (determinism snapshots, coverage/mutation, Sphinx logs, SBOM/Trivy, perf p95, cost reports, memory drift).
- Gates promoted only after 7 consecutive clean runs; waivers must include expiry.

Phases

- Phase 0 — Discovery: tool choices, risks, success metrics, ADRs

- Phase 0.5 — Knowledge Gaps Research: formulate 30 research questions; evaluate external tools/methods/services/repos that could accelerate development and quality; time‑boxed micro‑POCs; adopt high‑ROI items

- Phase 1 — Foundations: repo unification, builds, quality gates (initial), agent roles

- Phase 2 — Alpha: typing, tests, mapping matrix, NeSy pilots (shadow mode)

- Phase 3 — Beta Hardening: determinism, performance, observability, security gates

- Phase 4 — GA Readiness: CI/CD, packaging, docs, SLOs, privacy & compliance

- Phase 5 — Scale & Optimize: cost controls, resilience, automation, vendor adapters

Immediate Milestones (High Priority)

- Deliver `docs/AI_PROJECT_CHARTER.md` — governance, scope, RACI, responsible-AI summary (owner: eng-lead)

- Deliver `docs/VECTOR_STORE_SCHEMA.md` — canonical vector metadata, chunking, provenance (owner: data-engineer)

- Deliver `docs/model_cards/TEMPLATE.md` + one example model card (owner: data-science)

- Deliver `data/data_catalog.yaml` (lightweight catalog linked to VECTOR_STORE_SCHEMA) (owner: data-engineer)

Prioritized Next Steps (30/60/90 days)

30 days (Sprint 1) — Foundations & Governance

- Deliver `docs/AI_PROJECT_CHARTER.md` (owner: eng-lead)
  - Acceptance: charter reviewed; linked from README; Responsible-AI summary included.

- Deliver `docs/VECTOR_STORE_SCHEMA.md` and ingestion manifest (owner: data-engineer)
  - Acceptance: manifest validates; smoke-run via `scripts/research/run_poc.py` passes locally.

- Deliver `docs/model_cards/TEMPLATE.md` + example (owner: data-science)
  - Acceptance: example committed; experiment metadata references it.

60 days (Sprint 2) — Integration & Tests

- Ingestion & smoke validation [owner: data-engineer]
  - Acceptance: unit test verifies artifacts produced by `run_poc.py`.

- Memory/Reward wiring for research events [owner: eng-lead]
  - Acceptance: research run emits memory event with agreed schema; reward stub records metric.

90 days (Sprint 3) — Promote & Harden

- Promote advisory checks to gated CI for docs/schema/POC smoke-run after 7 nights [owner: infra]
  - Acceptance: 7-night stability; gates flipped; waivers documented.

- Repo hygiene and CI: run ruff/format and enforce MD lint to reduce churn [owner: eng-lead]
  - Acceptance: reduced MD lint warnings in PRs; pre-commit configured.

Live Risk Focus (kept to one active top‑risk)

- Agent concept duplication (Issue #14) — consolidate into `src/agent_core` with adapters; parity suite drives removals post‑green.

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
Track MC — Memory & Context

- Outcomes: Durable, auditable memory across short/long/structured contexts; adapters behind flags; coherent recall.
- Phase 1: Memory router + event logs; vector/KG retrieval enrichment; advisory coherence gate in CI.
- Phase 2: Adapters for Zep temporal KG, MemEngine, A‑MEM, AWS patterns (behind flags); privacy deletion audits; MCP protocol exploration.
- Phase 3: Nap‑time learning promotion; memory drift thresholds tuned; flip coherence gate to enforced after 7 green days.
- Phase 4–5: Cost/latency budgets for memory ops; retention policy + DPIA alignment; unified memory dashboards.
Refs: docs/agents/MEMORY_ARCHITECTURE.md; docs/QUALITY_GATES.md

Track D — Agentic System

- Outcomes: Planner/Builder/Verifier/Critic with safety and rewards.
- Phase 1: Roles, safety policies, dry-run job.
- Phase 2–3: Reward logs, bandit strategies; eval suite; Tier‑1 autonomy.
- Phase 3: Proactive refactoring (Critic identifies and improves maintainability).
- Phase 4: Tree-of-Thoughts planning and execution; Autonomous Tool Creation (agent writes/tests/adds new tools).
- Phase 4–5: SLOs, alerting; guarded Tier‑2 for low-risk edits.
Refs: docs/AGENTIC_ARCHITECTURE.md; docs/AGENTIC_GOALS.md; docs/TODO.md

Track OI — Orchestration & Interop (LangGraph, AutoGen, Runtimes, MCP)

- Outcomes: State‑of‑the‑art orchestrator with portable runtimes and standardized tool access.
- Phase 1: packages/orchestrator LangGraph graphs (minimal graph runner complete); feature‑flagged SuperApp /ask path invoking orchestrator; packages/llm runtime layer; CI stubs.
- Phase 2–3: MCP client/servers (FS/Git/Build/GS1); parity tests OpenAI Responses vs Bedrock Agents; AutoGen → LangGraph promotion.
- Phase 3: Dynamic Multi-Agent Collaboration (orchestrator spawns specialized sub-agent teams).
- Phase 4–5: CI gates for orchestrator; no direct LLM calls in app; traces + evidence attached to PRs.
Refs: docs/agents/ORCHESTRATION_ARCHITECTURE.md; docs/interop/MCP.md; docs/llm/RUNTIME_LAYER.md

Track DG — Diplomacy Guild (Regulatory Intelligence)

- Outcomes: Proactive regulatory foresight; data‑backed advocacy; Intelligence‑as‑a‑Service for members.
- Phase 1: Automated monitoring (multilingual), role dashboards, alerting.
- Phase 2: NLP summaries; horizon scanning; stakeholder graph; RI→SG integration.
- Phase 3: Member portal rollout; sector packs; revenue model and support ops.
Refs: docs/guilds/DIPLOMACY_STANDARDS_GUILDS.md

Track SG — Standards Guild (Automated GSMP)

- Outcomes: AI‑augmented lifecycle; faster time‑to‑market; higher quality and transparency.
- Phase 1: Workshop (co‑authoring) + Forum (digital balloting) MVPs.
- Phase 2: Opportunity Engine + Copilot; automated validation/publisher; SG↔RI loop.
- Phase 3: Publication pipeline hardening; contributor UX; analytics & dashboards.
Refs: docs/guilds/DIPLOMACY_STANDARDS_GUILDS.md

Track E — Architecture & Platform

- Outcomes: Clean monorepo, packages, infra, hermetic builds.
- Phase 1: Target layout, root pyproject, locks, Makefile.

- Phase 3–4: Docker images, compose demo; artifacts signing roadmap.

- Containerization & Orchestration: Baseline Docker (non-root, healthcheck), docker-compose demo; K8s readiness (readiness/liveness probes, config via env, statelessness, HPA considerations).

- Phase 5: Adapter layer for managed runtimes (e.g., DeepSeek).

- Targeted Refactor: API layering (routers/services), proper entrypoint; health/readiness probes; centralized config.

 Refs: docs/ULTIMATE_PLAN.md; docs/TODO.md

Track R — Knowledge Gaps & Ecosystem Research

- Outcomes: An autonomous multi-agent system capable of performing research to identify critical knowledge gaps, evaluate external capabilities, and accelerate project development.
- Phase 1 (MVP): Implement a foundational `ResearcherAgent` with web-search tools and a persistent RAG memory store. Deliverable: `make research-mvp`.
- Phase 2 (Collaboration): Develop a multi-agent "Research Crew" (`Planner`, `Researcher`, `Synthesizer`) orchestrated by LangGraph to produce structured, high-quality research reports.
- Phase 3 (Formalization): Integrate the research capability into project MLOps with automated evaluation, formal documentation, and dedicated `make` targets (`make research-run`, `make research-eval`).
- Phase 4–5: Continuous improvement of the research agent's capabilities, including autonomous evaluation of new tools and frameworks.
Refs: docs/RESEARCH_KNOWLEDGE_GAPS.md, docs/agents/RESEARCH_AGENT.md

Track F — Quality Engineering

- Outcomes: Style/lint/type gates, high coverage, mutation/fuzz in nightly.
- Phase 1: ruff enforced; mypy/tests advisory.
- Phase 2: Formalize Test-Driven Development (TDD) as a rewarded agent strategy.
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
- Phase 3: Cognitive Visualizer (agent generates `reasoning_graph.mermaid` for explainability).
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
Refs: docs/CI_WORKFLOWS.md

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
- Phase 2: Cost telemetry (LLM/API calls, storage), unit economics; FinOps Governor POC (pre-execution cost estimates).
- Phase 3: Enforce FinOps Governor budgets on PRs.
- Phase 3–4: Budgets/alerts; caching to reduce spend; weekly reports.
- Phase 5: Optimization backlog; contract/vendor renegotiations.
Refs: docs/TODO.md

Track P — Risk, Governance & Legal

- Outcomes: ADRs, CODEOWNERS, tech‑debt ledger; licensing & export compliance.
- Phase 1: ADRs, CODEOWNERS, TECH_DEBT.md; license scan.
- Phase 3–4: DPIA/DSR alignment; legal review of third‑party terms.
- Phase 5: Periodic audits; policy automation.
Refs: docs/ADR

Milestone Gates (Examples)

- Gate A: ruff enforced; PR CI green; monorepo ready.
- Gate B: coverage ≥90% (core), mypy enforced, mapping matrix complete.
- Gate C: ≥30% perf gain; LNN validator promoted to PR CI.
- Gate D: security zero high/critical; SBOM and Trivy weekly green.
- Gate M: memory coherence gate stable 7 days; nap‑time summarization active; privacy deletion audit passing.
- Gate OI: runtime parity ≥95% on eval tasks; MCP smoke green 7 days; orchestrator-only call policy enforced; AutoGen flows promoted to LangGraph.
- Gate DG: RI coverage/time‑to‑alert thresholds met for 7 consecutive days; horizon scanning “wins” logged; member pilot NPS ≥ target.
- Gate SG: P50 cycle‑time ↓ ≥50% on pilot set; dissent resolution SLA met; zero critical validation defects across 7 consecutive runs.
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
