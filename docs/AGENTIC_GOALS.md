# Agentic Goals, Behaviors, and Strategy — 12–18 Month Plan
Last updated: 2025-09-02

Purpose: Set outcome-driven long-term goals and the agentic behaviors, techniques, and metrics needed to reach them. This complements docs/ROADMAP.md (tracks/gates) and docs/AGENTIC_ARCHITECTURE.md (roles/loops/safety).

Long-Term Goals (12–18 months)
- Reliability: ≥85% win-rate on scoped repo tasks; <1% revert rate (rolling 90 days).
- Quality: Core coverage ≥90%; type errors = 0 on target modules; determinism gates enforced.
- Autonomy: Tier-2 auto-merge for low-risk classes with fully green CI and rollback guarantees.
- Velocity: Median time-to-green PR ≤15 minutes on core; advisory benches finish ≤5 minutes.
- Security/Privacy: Zero high/critical on main (weekly); DPIA approved; SBOM attached to releases.
- Performance/Cost: Perf budgets with ≤10% P95 regressions; unit cost tracked (CI minutes/feature, $/1k items).

Six-Month Targets (Gate B → Gate D path)
- Gate B: mypy + tests enforced on core paths; coverage no-regression guard active.
- Q11/Q12: determinism + validators decisions adopted per ADR; snapshot tests and validator choice documented.
- Observability: JSON structured logs with correlation IDs; latency histograms (P50/P95/P99) in place.
- Research-to-Production (R2P): 3+ POCs adopted with ADRs, adapters, and flags.

Autonomy Tier Objectives
- T0/T1 (now): All edits on branches; human review; bot posts plan/diff/test evidence automatically.
- T2 (low-risk): Auto-merge for docs/format/chore and targeted refactors, gated by fully green CI and policy checks.
- Escalation: Kill-switch label/ENV; break-glass requires waiver; auto-rollback on regression triggers.

Agentic Behaviors & Capabilities Needed
- Planner: Multi-step plan with acceptance criteria; plan-repair on failures; small reversible diffs.
- Builder: Patch-level edits; test and docs updates; safe tool use (allowlists, path guards).
- Verifier: Run lint/type/tests/security/schema deterministically; attach artifacts and short summaries.
- Critic: Diff risk analysis, cross-file impact, self-critique (Reflexion-style) with actionable next steps.
- Strategy Router: Context-aware selection among strategies (test-first, scaffold+fix, refactor-first) via bandit.
- Memory: Task/episode memory + project memory (index of docs/code/commits); cite evidence in PRs.
- Safety/Cost: Rate limits, API budgets, secrets policy; fail-closed behavior; guardrails for destructive ops.

Techniques & Strategies (Evidence-Based)
- Reasoning/Acting: ReAct for stepwise planning; Reflexion/self-critique after failures; ToT for hard planning with strict compute budgets.
- Verification: Chain-of-verification — re-run gates after edits; self-consistency on critical reasoning (sample n, majority vote) within budgets.
- Code Tactics: Skeleton generation + iterative repairs; search/replace with tests; spec-first for APIs; snapshot tests for determinism.
- Strategy Selection: Thompson Sampling/UCB over strategy arms by task class; decay old rewards; features include diff size, file types, failure modes.
- Evals: Small curated task set per strategy; nightly evals to ratchet gates.

Metrics & Gates
- Reliability: win-rate, revert rate, flake rate, MTTR.
- Quality: coverage %, type errors, mutation score, static findings.
- Performance: P50/P95/P99 latency, runtime budgets, memory peaks.
- Cost: CI minutes per PR, $/1k items (external APIs).
- Promotion rules: as in docs/QUALITY_GATES.md (7-day stability, no open waivers).

Phased Plan
1) Foundations (0–8 weeks):
   - Unify tool config; pre-commit; determinism snapshots; container smoke; project memory (search index).
   - Add plan/diff/test evidence PR comments; basic reward logging.
2) Hardening (8–16 weeks):
   - Enforce Gate B on core; enable strategy router; nightly eval dashboards; observability histograms.
3) T2 Low-Risk Autonomy (16–28 weeks):
   - Auto-merge for docs/format/chore; add rollback plan + revert bots; tighten budgets and alerts.
4) Scale & Optimize (28+ weeks):
   - Cost telemetry and budgets; managed runtime adapters; advanced NeSy pilots in shadow.

Risks & Mitigations
- Hallucinated plans or unsafe edits → strict allowlists, dry-runs, revert bots, and coverage/type gates.
- Flaky tests → quarantine and nightly retries; invest in deterministic fixtures.
- Vendor/API drift → adapters + parity tests; flags default OFF; canaries for changes.

Next Actions (Local-First)
- Emit PR plan/diff/test artifacts locally; attach to commits/PRs when CI is available.
- Finish coverage no-regression and type surface report; drive core to ≥90%.
- Track strategy outcomes in `agent/outcomes/`; weekly summary artifact.
