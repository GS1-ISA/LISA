Title: Master TODO — Agentic Monorepo Program (All Plans)
Last updated: 2025-09-02

Status Legend: [ ] pending  [~] in-progress  [x] done  [!] blocked

See also: docs/ULTIMATE_PLAN.md, docs/AGENTIC_ARCHITECTURE.md, docs/AGENTIC_GOALS.md, docs/ADOPTION_PLAN.md, docs/QUALITY_GATES.md, docs/TODO_NeSy.md

00) Knowledge Gaps Research (Phase 0.5)
- [ ] Create docs/RESEARCH_KNOWLEDGE_GAPS.md scaffold with 30 research questions (agentic loops, NeSy, LLMOps, data quality/governance, security/privacy, observability/SRE, performance, UX, CI/CD, DevEx)
- [ ] Define evaluation rubric (Impact, Ease of integration, Maturity, Alignment, Cost/FinOps) and scoring worksheet
- [ ] Compile candidate tools/services/frameworks/repos with licensing and costs (e.g., agent frameworks, LLM orchestration, data validators, observability, CI tooling)
- [ ] Prioritize top 10 by score; select 5 for time‑boxed micro‑POCs (≤1 day each)
- [ ] Run micro‑POCs; capture metrics (accuracy/precision, latency, dev time saved, cost); write concise reports
- [ ] Decisions: adopt/hold/reject; draft ADRs for adopted items and integrate via adapters/feature flags
- [ ] Update ROADMAP/TODO and backlog with accepted integrations and deprecations
Acceptance: 30 questions documented; rubric applied; ≥5 POC reports with metrics; ≥3 ADRs accepted; no new core dependencies without adapters and feature flags; projected ROI documented.

- [x] Refine research questions to v2 with per-question approach (docs/RESEARCH_KNOWLEDGE_GAPS.md)
- [x] Add curated source list (docs/RESEARCH_SOURCES.md) and cross-link from RESEARCH_OPERATIONS.md

Metadata (single-owner model applies to all)
- Owner: Project (You + Agent)
- Critical Path: mark [CP] where applicable
- Blocked by: <list>
- Blocks: <list>
- Issues: <links when created>

01) Research Operations (R2P)
- [ ] Add Research Operations guide (docs/RESEARCH_OPERATIONS.md) with R2P pipeline, evidence ladder, vetting checklist
- [ ] Create search ledger template and require logging queries/sources for each POC
- [ ] Add replication step to POCs (second run/env) and document variance
- [ ] Define promotion thresholds and 7‑day shadow stability rule
- [ ] Add retrospective template and link to reward priors updates
Acceptance: Each research effort includes a ledger, POC protocol, replication record, decision, ADR (if adopted), adapter+flag integration, and retrospective.

02) Definition of Done (DoD) & Change Policy
- [x] Create docs/DEFINITION_OF_DONE.md with checklists per change type (code, data, config, docs)
- [x] Add PR template referencing DoD and requiring: tests updated, type clean, lint clean, docs updated, determinism verified, perf/security checks passed, rollback noted
- [ ] CI: add coverage “no-regression” check (coverage must not drop > 0.5% on core); type coverage trend artifact; perf budget guard on marked benchmarks
- [ ] CI: verify CHANGELOG or docs touched for user-facing changes (best-effort)
Acceptance: DoD doc used in PRs; CI enforces coverage and perf budgets; PRs failing DoD are blocked.

0) Meta & Governance
- [ ] Create ownership map and CODEOWNERS
- [ ] Add TECH_DEBT.md format and review cadence
- [ ] Record ADRs for major decisions (tooling, safety, autonomy)
Acceptance: Owners listed per area; ADRs linked from README; tech-debt review on calendar.

1) Monorepo Unification
- [CP] Critical Path
- Blocked by: 0, 2
- Blocks: 2, 4, 5, 6
- [ ] Approve target layout: apps/superapp, packages/{isa_c_full,isa_c_mapping,agent_core}, artifacts, infra, docs
- [ ] Write migration map (from current folders to targets)
- [ ] Root README and CONTRIBUTING updated
Acceptance: Migration doc enumerates every move; superapp smoke runs post-move.

2) Build System & Dependencies
- [CP] Critical Path
- Blocked by: 1
- Blocks: 4, 5, 6, 13
- [ ] Root pyproject with shared tool config (ruff, mypy)
- [ ] Choose/lock with uv; define constraints policy
- [ ] Deps report script (graph + unused)
Acceptance: Single lock tool; reproducible install; no duplicate managers.

3) Config & Secrets
- [ ] Typed settings via pydantic-settings
- [ ] .env.example and .env schema; secrets policy
- [ ] Gitleaks in CI
Acceptance: Startup validates config; secrets scan clean on main.

4) Style & Lint (Consolidated)
- [CP] Critical Path (to Gate A)
- Blocked by: 2
- Blocks: 13
- [x] Ruff for lint+format+imports (CI enforced)
- [ ] Pre-commit ruff hooks installed project-wide
- [ ] Remove redundant formatters from CI (black/isort)
Acceptance: ruff check/format pass in CI; editors consistent.

5) Typing & Schemas
- [CP] Critical Path (to Gate B)
- Blocked by: 2
- Blocks: 6, 13
- [ ] mypy as CI gate (strict on libraries)
- [ ] Type coverage metric reported in CI
- [ ] JSON Schemas for agent traces/plans
Acceptance: mypy green; type coverage threshold recorded and tracked.

6) Tests & Coverage
- [CP] Critical Path (to Gate B)
- Blocked by: 2
- Blocks: 8, 9, 13
- [ ] Unit/integration/property tests on PRs
- [ ] Coverage ≥90% for core mapping; thresholds in CI
- [ ] Nightly: mutation (mutmut), fuzz (atheris), perf benchmarks
Acceptance: PR gate at ≥90% core; nightly mutation score ≥70% reported.

6a) Memory Coherence & Audits (New)
- [x] Add MemoryEventLogger and JSONL log; snapshot log as CI artifact
- [x] Advisory memory coherence gate (drift check) in PR CI
- [ ] Privacy: add deletion events and audit test (expected counts, reasons)
- [ ] Stability: promote coherence gate to enforced after 7 green days
Acceptance: Memory logs present on PRs; drift within threshold; deletions audited; gate promotion criteria documented.

7) Mapping Correctness Matrix
- [CP] Critical Path (to Gate B)
- Blocked by: 6
- Blocks: 15, 22
- [ ] Generate matrix (field → source, transform, ESRS link)
- [ ] CI check for unmapped/collisions; waivers tracked
Acceptance: No critical unmapped; matrix artifact published.

8) Determinism & Reproducibility
- [CP] Critical Path
- Blocked by: 6
- Blocks: 9, 13
- [x] Canonical JSON writer (sorted keys, UTF‑8, newline)
- [~] Snapshot tests for canonical outputs
- [~] Determinism snapshot CI job (advisory)
Acceptance: Byte-for-byte identical reruns; snapshot suite stable.

9) Performance & Parallelism
- [CP] Critical Path (to Gate C)
- Blocked by: 6, 8
- Blocks: 10, 11, 13
- [ ] Baseline profiling (cProfile/py-spy) captured as artifacts
- [ ] Optimize I/O (streaming/chunking), vectorize heavy ops
- [ ] Parallel runner with safe concurrency limits
Acceptance: ≥30% speedup on target workload; no correctness changes under parallel.

9a) Performance Enhancements Backlog (Deep Dives)
- [ ] JSON performance: adopt orjson for dumps and critical loads where safe; canonical writer backed by orjson
- [ ] Validation speed: precompile JSON Schemas via fastjsonschema; use Pydantic v2 compiled validators
- [ ] Dataframes: prototype Polars for heavy transforms; fallback to pandas where simpler
- [ ] Joins/aggregation: add optional DuckDB path for large joins; compare perf and memory
- [ ] Caching: content-hash + LRU caches for pure functions; HTTP caching (ETag/If-None-Match)
- [ ] I/O streaming: stream CSV/JSONL and compressed inputs; avoid materializing large intermediates
- [ ] Async I/O: httpx (async) for external calls with connection pooling and timeouts
- [ ] Concurrency: safe multiprocessing for CPU-bound; asyncio for I/O-bound; document limits
- [ ] Test speed: pytest-xdist for parallel tests; split slow tests to nightly
- [ ] Memory: tracemalloc and objgraph snapshots for hot paths; fix top leaks
Acceptance: Each adopted item shows measured improvement (≥15% speed or memory) without correctness regressions; documented in docs/results.md.

10) Caching
- [ ] Content-hash caches for expensive steps (disk-backed)
- [ ] Invalidation strategy documented
Acceptance: Cache hits reduce repeat runtime; correctness unchanged.

11) Observability
- Blocked by: 9
- Blocks: 18, 19
 - [~] Structured JSON logging (correlation IDs)
 - [~] Prometheus metrics (/metrics); minimal Grafana dashboard JSON
 - [ ] Optional OpenTelemetry spans on pipelines
 Acceptance: Golden signals visible; trace-log correlation works.

11b) Memory Observability (New)
- [x] Memory logs snapshot artifact
- [ ] Dashboard panel for memory events rate and drift (Grafana)
Acceptance: Memory event rate visible; spikes investigated; drift alerts advisory.

11a) Observability Enhancements
- [ ] Low-overhead structured logging via orjson; add sampling for noisy categories
- [ ] Standardize metrics types: counters and histograms (latency P50/P95/P99) with exemplars
- [ ] Request-scoped correlation/tracing IDs propagated across tasks
Acceptance: Logging overhead <5%; key histograms visible; correlation IDs present in logs and metrics exemplars.

12) Security & Supply Chain
- [CP] Critical Path (to Gate D)
- Blocked by: 2
- Blocks: 13, 20
- [ ] Bandit, pip-audit, gitleaks in CI (advisory → gates)
- [ ] SBOM generation (syft) and Trivy container scan weekly
- [ ] Vulnerability triage workflow documented
Acceptance: Zero high/critical on main; SBOM attached to releases.

13) CI/CD
- [CP] Critical Path
- Blocked by: 2, 4, 5, 6
- Blocks: 20, 21
- [x] PR CI skeleton (ruff enforced; others advisory)
- [x] Nightly and weekly workflows in place
- [ ] Release workflow (semver, changelog, signed artifacts)
 - [x] Significance-triggered deep checks wired in CI (Semgrep, extended tests)
 - [x] Memory coherence gate enforced + memory logs snapshot uploaded
 - [x] Combined coverage across app + packages (advisory) and baseline on main
 - [x] Agent Check workflow (on-demand) added
 - [~] Docs build gate (advisory)
 - [~] Container build + /metrics smoke (advisory, significance)
Acceptance: Green CI; release produces wheels/images and notes.

14) Orchestration & Interop (LangGraph, AutoGen, Runtimes, MCP)
- [ ] packages/orchestrator: LangGraph graphs (plan→tool→reflect; long jobs)
- [ ] packages/agents/autogen: AutoGen teams + Studio configs; promotion pipeline to LangGraph
- [ ] packages/llm: runtime layer (OpenAI Responses, Bedrock Agents) with one interface + parity tests
- [ ] packages/dspy: DSPy modules for top tasks; training/compile scripts + artifacts
- [ ] infra/rag: Pinecone ingestion/embeddings/indexers/retrievers; eval notebooks; golden datasets
- [ ] infra/mcp: MCP client + servers (FS, Git, Build, GS1); secure defaults; smoke tests in CI
- [x] SuperApp policy: forbid direct LLM calls (guard flag) + minimal orchestrator facade behind flag with unit test
Acceptance: Runtime parity ≥95% on evals; MCP smoke green 7 days; PRs include traces/evidence; orchestrator-only policy verified by tests.

14) Developer Experience
- [x] Makefile tasks (setup, lint, fix, typecheck, test)
- [x] Devcontainer + VS Code tasks (added)
- [ ] 5‑minute onboarding guide and one-command demo
Acceptance: New dev completes demo in ≤5 minutes locally.

15) Data Quality
- [ ] Great Expectations or pydantic-core suites for inputs
- [ ] CI gate for data quality with actionable errors
Acceptance: ≥99% pass on critical expectations; failures block merges.

16) Packaging & Runtime
- Blocked by: 13
- Blocks: 20
- [ ] Wheels for packages/{isa_c_full,isa_c_mapping} with CLI entries
 - [ ] Docker image for apps/superapp (non-root, healthcheck)
 - [ ] docker-compose demo stack under infra/; K8s readiness doc (probes, statelessness, HPA)
 Acceptance: docker compose up runs end-to-end demo locally.
- [~] CI container smoke test (build + curl /metrics) added (advisory)

16a) API & Services Refactor (Targeted)
- [ ] Split FastAPI app into routers/services; remove in-process uvicorn spawn; add proper CLI entrypoint
- [ ] Health/readiness probes and graceful shutdown; config centralized (pydantic-settings)
- [ ] Static/assets served via ASGI static middleware; add CSP header checks in tests
Acceptance: Behavior identical under guard tests; cold start and latency unchanged or improved; clean shutdown verified.

17a) Agentic Practices & Automation (New)
- [x] Lead Developer Autonomy policy documented (act without asking; research-first; escalation triggers)
- [x] Outcomes logging + weekly summary reports (local-first)
- [x] Docs reference linter and index (search_index) for cross-link integrity
- [x] PR Notes generator (Plan/Diff/Evidence) for branch updates
- [~] Strategy router skeleton (epsilon-greedy) with reward updates from outcomes
Acceptance: Artifacts present under agent/outcomes and docs/audit; strategy selection logged; promotion to CI when GH is stable.

17) Agentic Architecture & Safety
- Blocked by: 1, 2
- Blocks: 18, 20
- [x] Roles, safety policies, autonomy tiers documented
 - [ ] Implement policy engine (allowlists, rate limits, kill-switch)
 - [ ] Agent PR dry-run job (plan/diff comment) in CI; document PR comment schema and artifact paths
 Acceptance: All agent edits via branches; CI green required for merges; kill-switch documented.

18) Agent Learning & Rewards
- Blocked by: 17
- Blocks: 19
- [x] Initial reward model drafted
- [ ] Bandit strategy set defined; replay logs schema
- [ ] Eval suite of low-risk tasks with win-rate tracking
Acceptance: Tier‑1 win-rate ≥70% on eval; logs schema validated.

19) SLOs & Alerting
- Blocked by: 11, 18
- Blocks: 20
- [ ] SLOs for agent success, revert rate, planning latency
- [ ] Alerts wired (Slack) for budget breaches
Acceptance: Alert tests verified; burn-rate panels exist.

20) Cutover & Handover
- [CP] Critical Path (to Gate E)
- Blocked by: 13, 16, 19
- Blocks: —
- [ ] Tiered autonomy rollout (T0→T2) playbook
- [ ] Rollback & repro pack automation
Acceptance: Revert rate <1% rolling; repro packs attached on failure.

21) Managed Runtime Migration
- [ ] Adapter abstraction for LLM/tooling (DeepSeek-ready)
- [ ] Parity tests (plan/diff consistency) across engines
Acceptance: No regression in eval win-rate; latency/cost tracked.

22) NeSy Roadmap Integration (link: docs/TODO_NeSy.md)
- [ ] Foundations: adapter interface, flags, eval harness
- [ ] ESG‑BERT + rules MVP (NOW)
- [ ] LNN rule validator (NOW)
- [ ] SenticNet client (NOW optional)
- [ ] Pilots: ESGSenticNet, DeepProbLog, Weave.AI
- [ ] Research: NeurASP, DON
Acceptance: Each adapter promoted only after meeting metrics for 7 consecutive days.

32) Memory Ecosystem (Adapters & Flags)
- [x] Router + logs + tests
- [ ] Zep adapter behind flag (temporal KG)
- [ ] MemEngine adapter behind flag
- [ ] A‑MEM adapter behind flag
- [ ] AWS memory‑augmented patterns (S3/Dynamo) behind flag
- [ ] MCP protocol for tool/context access (explore)
- [ ] LangChain memory modules (buffer/summary/vector) parity tests
Acceptance: Each adapter ships with parity tests, audit logs, and CI stability prior to enabling in PR path.

33) Diplomacy Guild (Regulatory Intelligence)
- [ ] Source registry and ingestion (official portals, regulators, legislative DBs) with multilingual coverage
- [ ] NLP summaries and requirement extraction; accuracy sampling process
- [ ] Horizon scanning models + evidence logging (predictions → outcomes)
- [ ] Stakeholder/engagement graph; link to advocacy playbooks
- [ ] Role dashboards + alerts; sector briefs; portal widgets for members
- [ ] Intelligence‑as‑a‑Service packaging (tiers, SLAs, pricing); billing integration stub
Acceptance: Coverage/time‑to‑alert meets thresholds; prediction wins logged; member pilot NPS ≥ target; audit trails present.

34) Standards Guild (Automated GSMP)
- [ ] Workshop: secure co‑authoring with version history and threaded comments
- [ ] Forum: AI comment triage; structured dissent resolution; digital balloting
- [ ] Opportunity Engine: proactive work item detection from RI + market/tech signals
- [ ] Publisher: automated validation/linting; multi‑format outputs; cross‑standard checks
- [ ] Contributor analytics; publication latency dashboard; UX hardening
Acceptance: P50 lifecycle time ↓ ≥50% on pilot; dissent resolution SLA met; zero critical validation defects across 7 consecutive runs.

23) Quality Gates Promotion
- [ ] Flip mypy/tests/security to enforced after stability window
- [ ] Set coverage/type thresholds in CI and document waivers
Acceptance: Gates enforced with minimal flakiness; waivers tracked in TECH_DEBT.md.

24) Privacy & Legal
- [ ] Data classification (PII, sensitive, public); tag flows
- [ ] DPIA and threat model for data processing
- [ ] DSR playbooks (access/delete/export) and retention policy
- [ ] Redaction/anonymization utilities with tests
Acceptance: DPIA approved; DSR flows tested on fixtures; privacy checks added to CI where applicable.

25) Data Governance
 - [ ] Ownership/stewardship matrix for datasets and schemas
 - [ ] Lineage capture for pipelines (run IDs, input/output content hashes; consider OpenLineage)
 - [ ] Data versioning policy for golden datasets (Git LFS/DVC) without repo bloat
 - [ ] Data catalog export (even if lightweight JSON)
 Acceptance: Owners documented; lineage visible for key outputs; catalog artifact updated in CI.

26) MLOps/LLMOps
- [ ] Prompt/model registry (versioned prompts; eval harness)
- [ ] Safety filters and red-team tests for prompts
- [ ] Canary and rollback procedures for LLM changes
Acceptance: All prompt/model changes go through eval suite; rollback documented and tested.

27) Accessibility & Internationalization
- [ ] A11y audit (WCAG 2.1 AA) and key fixes in web UI
- [ ] i18n hooks and string externalization policy
Acceptance: No critical A11y violations on key pages; i18n ready for first locale.

28) Cost & FinOps
 - [ ] Cost telemetry (LLM/API/storage/compute) and unit economics; CI runtime minutes captured as artifact
 - [ ] Budgets and alerts; caching policies to reduce spend
 - [ ] Weekly cost report artifacts
 Acceptance: Costs tracked per feature; budget alerts active; trend down with caching.

29) Incident Response & DR
- [ ] Runbooks for common failures; on-call rotation plan
- [ ] Backups, restore drills, RPO/RTO targets
- [ ] Post-incident review template and cadence
Acceptance: Restore drill meets RTO/RPO; postmortem template used in dry run.

30) Vendor & Integrations
- [ ] Evaluation criteria and procurement checks (DeepSeek, Weave, SenticNet)
- [ ] Abstraction layer to avoid lock-in; contract/licensing review
Acceptance: Integrations behind adapters; parity tests; licensing documented.

31) Documentation & Knowledge
- [ ] MkDocs site structure; decision log and runbooks
- [ ] Onboarding: 5-minute quickstart, one-command demo
- [ ] Architecture diagrams (current/target) updated per milestone
Acceptance: Docs CI builds; new engineer completes onboarding in ≤5 minutes.

35) Governance & Hygiene (New)
- [x] CODEOWNERS added (granular)
- [x] Issue templates (bug/feature) added
- [x] SECURITY.md policy present
- [x] Dependabot for pip (app) and GitHub Actions
Acceptance: Automated hygiene PRs land weekly; ownership clear in PRs; security report path documented.

36) Coverage & Reporting (New)
- [x] .coveragerc added to omit tests and stdlib; branch coverage enabled
- [x] Combined coverage across app + packages (XML) uploaded per PR
- [x] Combined coverage baseline saved on main; advisory no-regression check
Acceptance: Coverage trends meaningful; ready to promote to enforced gate once stable.

37) Research & Web Data (Online Research / Scraping) (New)
- [ ] Add research toolkit: `httpx`/`requests` with retry/backoff, timeout, structured logging
- [ ] Robots/Politeness: parse robots.txt, set `User-Agent`, enforce crawl-delay, rate-limit + concurrency guard
- [ ] Extractors: `beautifulsoup4`/`lxml` content extraction (readability-like), boilerplate removal, encoding normalization (UTF‑8)
- [ ] Dynamic sites (optional): Playwright-driven fetch behind a feature flag; default OFF in CI and PRs
- [ ] Compliance: capture Terms/robots snapshot; do‑not‑scrape allow/deny lists; audit log (URL, ts, status, bytes, reason)
- [ ] Caching & Repro: on-disk cache keyed by URL+headers; content hash (SHA‑256); offline replay fixtures for tests
- [ ] Storage & Schema: content-addressable store for HTML/text; metadata schema (url, fetched_at, mime, size, sha256, robots_rules)
- [ ] Indexing & Memory: summarize + embed harvested docs; add to VectorIndex + KG with provenance
- [ ] R2P Integration: auto-populate Search Ledger entries from research sessions (queries, sources, grades)
- [ ] CI: offline tests using recorded fixtures; no live network on PR; nightly job allowed for approved seed domains
Acceptance: Deterministic offline replay of harvested pages with ≥95% extraction success on a seed set; robots/terms respected; per-request audit logs present; summaries/index entries linked with provenance.

38) Web Research Tooling & Benchmarks (New)
- [ ] Sourcegraph/Cody integration (or local sg/rg fallback) for semantic/code example search; document privacy & rate limits
- [ ] Example-centric search (Blueprint/Codota patterns) — process doc with prompt templates; store results as research ledgers with citations
- [ ] Agent tool benchmarks: evaluate Cursor/Copilot Agent/Claude Code on curated PR set; log productivity metrics
- [ ] Evaluation frameworks: adopt a small SWE‑bench/DevBench subset in nightly with fixtures; publish pass/fail and failure classes
- [ ] Static/code health: expand Semgrep rulesets; optionally add CodeScene advisory reports
- [ ] Onboarding assistants: VS Code explainers (GPTutor‑style) added to onboarding docs; measure time‑to‑ramp
Acceptance: Evidence artifacts per run (summaries, ledgers, benchmark results) uploaded in CI; decisions recorded (Adopt/Hold/Reject) with ADRs for adopted tooling.

Next 3 PRs (Focused)
- PR1 — Research Connector 2 (Federal Register):
  - Normalize fixture JSON; index into VectorIndex and KG with provenance; add offline tests; prepare nightly allowlist for API.
- PR2 — Orchestrator App Flow (Flagged):
  - Feature‑flagged /ask flow via GraphRunner; add explicit integration test; keep default OFF on PR CI.
- PR3 — RAG Eval v1:
  - Curated 3–5 queries; run offline over research_index.json; produce artifact with top hit IDs; define promotion metrics (accuracy lift, latency).
