Title: Agentic Architecture — Roles, Loops, Safety, Rewards
Last updated: 2025-09-02

Overview: The system operates as a continuous feedback loop. Agents plan, act, observe, critique, and learn, with strict safety and quality gates.

Roles
- Planner: Builds/updates explicit task plans. Inputs: repo state, memory. Outputs: steps + tools.
- Builder: Applies patches, runs shells/tests, edits docs. Constrained by policies.
- Verifier: Executes gates (lint/type/tests/schema/security/data quality).
- Critic: Reviews diffs/outcomes; emits structured feedback and follow-ups.
- Reward Aggregator: Scores outcomes: tests, coverage, perf, reverts, approvals.
- Meta-Learner: Bayesian bandit over strategies (test-first, scaffold+fix, refactor-first). Updates from rewards.
 - Council Simulations: Internal advisors (Architect, Tester, Security, Performance, User) on high-impact changes.

Safety Policies
- Allowlist tools/actions; file/path guards; rate limits; network off by default.
- Ephemeral branches; auto-merge only if CI fully green.
- Auto-revert on regression; attach repro packs.
- Kill-switch via environment flag + repo label.

Memory & Tracing
- Append-only JSONL for events (plan, action, result, reward, memory store/retrieve) via `MemoryEventLogger` (agent/memory/memory_log.jsonl). Snapshot uploaded in CI.
- Memory Router: detects context type (short/long/structured), builds context from KG + vector + adapters (LangChain buffer, structured facts, external stubs for Zep, MemEngine, A‑MEM, AWS, MCP). See `docs/agents/MEMORY_ARCHITECTURE.md`.
- Nap‑time learning: after idle windows, summarize recent logs into long‑term KG (`NapTimeLearner`).
- Coherence Guard: advisory drift check over recent summaries; CI prints warnings when drift exceeds threshold.
- Summaries for retrieval; link traces to commits and CI runs.
 - Project memory sources: docs index (docs/audit/search_index.jsonl), audit reports, ADRs, outcomes logs.

Observability (Metrics + Tracing)
- Metrics: Prometheus `/metrics` exposes request counters and latency histograms (ISA_SuperApp/src/api_server.py). One‑command Prometheus+Grafana lives under `infra/monitoring/`.
- Tracing (optional): Enable OpenTelemetry with `OTEL_ENABLED=1`. FastAPI and outgoing requests are auto‑instrumented; Jaeger compose under `infra/otel/`. Logs include `trace_id` and `span_id` for correlation.
- Spans: Assistant flows emit spans for `assistant.rebuild_index`, `assistant.retrieve`, and `assistant.reason` to accelerate debugging and performance tuning.

Autonomy Tiers
- T0: Read-only advice (default).
- T1: Branch writes; human reviews merge.
- T2: Auto-merge for low-risk classes behind policy gates.

Operational Principle — Lead Developer Mode
- Default operating mode is proactive: the agent selects and executes the next best task without asking for direction.
- Exceptions: explicit kill-switch, destructive actions outside allowlists, compliance/privacy red flags, or repeated unexplained failures.
- When blocked by missing context, the agent researches (search index, docs, code, tests) and continues; only then, if truly ambiguous, request minimal clarification.

Reward Model (Initial)
- Positive: tests pass (+3), coverage up (+1/2%), perf budget met (+2), docs updated (+1), approval (+2).
- Negative: tests fail (−3), type/lint fail (−2), revert (−4), perf regression (−2), security/data-quality fail (−3).
- Normalize by task difficulty and runtime; decay old data.

Evaluation Targets
- Win-rate ≥70% (T1); ≥85% for T2 low-risk set; reverts <1%.
 - Coverage ≥90% core; type errors 0 on target modules; determinism enforced.

Operational Loop (Agent ↔ CI)
- Planner proposes plan + diff; posts structured PR comment (plan, rationale, risk, test plan).
- Verifier runs the same CI gates locally (lint, type, tests, schema, security) and uploads artifacts.
- Critic summarizes CI outcomes and suggests improvements; logs saved as artifacts.
- Reward Aggregator computes reward from CI signals (tests, coverage delta, perf budgets, security findings, revert rate).
- Autonomy: all edits land on branches; T2 auto-merge only with fully green CI and within defined policy scope.

Gate Promotion Loop
- Stability counters: each gate (tests, coverage, mypy, semgrep, determinism) increments a "green day" on successful runs. After ≥7 consecutive greens, the gate flips from advisory → enforced.
- Baselines: coverage and repository size baselines are persisted under `docs/audit/`; PRs compute deltas (advisory now) and will enforce budgets post‑stability.

PR Artifact Flow
- Before opening a PR, the agent generates `agent/outcomes/PR_NOTES.md` containing Plan/Diff/Evidence and attaches health/artifact summaries.
- Outcomes from tasks are logged under `agent/outcomes/*.jsonl`; weekly summaries are rendered to `docs/audit/agent_outcomes_summary.md` to drive strategy learning.

Strategy Selection
- A Thompson Sampling router chooses among strategies (e.g., test‑first, scaffold+repair, refactor‑then‑feature) and updates rewards based on outcomes (tests, coverage delta, type errors).
- Over time, win‑rate increases and the router exploits higher‑reward strategies while keeping limited exploration.

Kill-Switch & Rollback Triggers
- Kill-switch: disable agent writes via ENV `AGENT_WRITE=0` and repo label `agent-blocked`.
- Auto-rollback triggers: revert rate >1% rolling, anomaly spikes in CI failures, or policy violations; agent auto-creates a revert PR with repro pack.

See Also
- docs/agents/CODEGENESIS.md — operating manual (identity, behaviors, procedures)
- docs/AGENTIC_GOALS.md — long-term goals and phased plan
 - docs/agents/ORCHESTRATION_ARCHITECTURE.md — orchestrator stack & interop
 - docs/QUALITY_METHODS.md — quality and gate policies (incl. orchestrator-only guard via `ISA_FORBID_DIRECT_LLM`)
- docs/agents/ORCHESTRATION_ARCHITECTURE.md — end‑to‑end orchestrator stack (LangGraph, AutoGen, RAG, MCP)
