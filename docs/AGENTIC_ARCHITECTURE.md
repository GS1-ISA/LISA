# Agentic Architecture — Roles, Loops, Safety, Rewards
Last updated: 2025-09-02

Overview: The agent's behavior is configured by the `.agent/policy.yaml` file. Agents plan, act, observe, critique, and learn, with strict safety and quality gates.

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

Current Implementation Snapshot (this repository)
- Entry point (CLI): `run_research_crew.py` — wires together the agents, memory, and docs provider; prints a Markdown report.
- Orchestrator: `src/orchestrator/research_graph.py` — executes Planner → Researcher (loop per task) → Synthesizer.
- Agents:
  - Planner: `src/agent_core/agents/planner.py` — decomposes a query; may consult docs via `DocsProvider`.
  - Researcher: `src/agent_core/agents/researcher.py` — uses `WebResearchTool` and `RAGMemory` to gather evidence.
  - Synthesizer: `src/agent_core/agents/synthesizer.py` — composes a final Markdown report from memory.
- Memory: `src/agent_core/memory/rag_store.py` — ChromaDB persistent store under `storage/vector_store/...` using SentenceTransformers embeddings.
- Tools: `src/tools/web_research.py` — DuckDuckGo search + `httpx` fetch + BeautifulSoup extraction with file cache.
- Docs Provider: `src/docs_provider/src/docs_provider/context7.py` with `get_provider()` factory. Controlled by env (`CONTEXT7_ENABLED`, `CONTEXT7_*`).
- Observability: Docker compose files for Prometheus/Grafana and Jaeger live under `infra/monitoring` and `infra/otel`. No FastAPI app is included in this repo variant; container smoke checks are advisory.

How to run
```bash
make setup
python run_research_crew.py --query "your topic here"
```

Testing scope
- Tests live under: `src/**/tests`, `infra/rag/tests`, and `scripts/research/tests`.
- CI runs ruff, mypy (advisory), and pytest across these packages. See `docs/CI_WORKFLOWS.md`.

## Agent State Persistence and Task Management

To ensure continuity and prevent redundant work across agent sessions and different agents, the system formalizes how agents manage and persist their internal state regarding task progress and completion:

- **Task Progress Tracking:** Agents are expected to update `docs/TODO.md` to reflect the current status of assigned tasks (e.g., "in progress," "completed," "blocked"). This document serves as the primary, human-readable source of truth for task completion.
- **Outcome Logging:** Detailed outcomes of agent actions and completed sub-tasks are logged under `agent/outcomes/`. These logs provide a granular record of work performed, which can be used for auditing, debugging, and informing future agent decisions.
- **Leveraging Project Memory:** Agents should regularly consult the project's memory sources (including the repository index and outcome logs) to ascertain the current state of the codebase and previously completed work before initiating new actions. This minimizes the risk of duplicating effort.

Observability (Metrics + Tracing)
- Metrics: Prometheus `/metrics` endpoint is available in the API‑first variant (FastAPI app). In this repository variant, Prometheus+Grafana compose files live under `infra/monitoring/` for local experiments.
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

Adapter Boundaries & Env Flags
- Orchestrator → agent_core delegation happens via an adapter to preserve boundaries and keep CI offline by default.
- Env flags:
  - `ORCHESTRATOR_USE_AGENT_CORE=1` — route orchestrator runner to agent_core via adapter.
  - `ADAPTER_STUB_MODE=1` — force adapter to stub (no network, no heavy deps) for CI/nightly.
- Import discipline: orchestrator/llm must not import `src.agent_core` directly; CI runs an advisory import guard.

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
- docs/agents/RESEARCH_AGENT.md — The Autonomous Research Agent implementation.

---

### v2 Architectural Enhancements (Proposed)

To evolve the system into a world-class adaptive engineering partner, the following enhancements are proposed for the next design iteration.

1.  **Tree-of-Thoughts Planning & Execution**:
    - The `Planner` will be enhanced to propose multiple distinct solution paths (a "thought tree").
    - The `Builder` will explore these paths in parallel, with the `Verifier` and `Critic` scoring each branch. The highest-scoring, valid solution is selected.

2.  **Dynamic Multi-Agent Collaboration**:
    - For complex tasks, the primary agent will act as an orchestrator, spawning a temporary team of specialized sub-agents (e.g., `CoderAgent`, `TestAgent`, `DocsAgent`) that collaborate to produce a complete solution.

3.  **Autonomous Tool Creation**:
    - The agent will be empowered to identify repetitive sub-tasks, write new Python functions as tools, generate tests to validate them, and add them to a dedicated `packages/agent_tools` library for future use.

4.  **FinOps Governor**:
    - A new component that provides pre-execution cost estimation (tokens, compute) for proposed plans. It enforces budgets defined in `docs/COST_TELEMETRY.md` and prunes overly expensive branches in a Tree-of-Thoughts exploration, making the agent economically aware.

5.  **Cognitive Visualizer**:
    - For complex tasks, the agent will generate a `reasoning_graph.mermaid` artifact. This graph will visually represent its decision-making process (e.g., the Tree of Thoughts exploration), dramatically improving explainability.

6.  **Formalized TDD & Proactive Refactoring**:
    - A "Test-First" strategy will be heavily rewarded by the `Meta-Learner`, requiring the agent to generate a failing test before writing implementation code.
    - The `Critic` will be empowered to identify and proactively refactor complex code to improve long-term maintainability.
