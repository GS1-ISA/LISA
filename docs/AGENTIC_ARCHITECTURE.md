Title: Agentic Architecture — Roles, Loops, Safety, Rewards

Overview: The system operates as a continuous feedback loop. Agents plan, act, observe, critique, and learn, with strict safety and quality gates.

Roles
- Planner: Builds/updates explicit task plans. Inputs: repo state, memory. Outputs: steps + tools.
- Builder: Applies patches, runs shells/tests, edits docs. Constrained by policies.
- Verifier: Executes gates (lint/type/tests/schema/security/data quality).
- Critic: Reviews diffs/outcomes; emits structured feedback and follow-ups.
- Reward Aggregator: Scores outcomes: tests, coverage, perf, reverts, approvals.
- Meta-Learner: Bayesian bandit over strategies (test-first, scaffold+fix, refactor-first). Updates from rewards.

Safety Policies
- Allowlist tools/actions; file/path guards; rate limits; network off by default.
- Ephemeral branches; auto-merge only if CI fully green.
- Auto-revert on regression; attach repro packs.
- Kill-switch via environment flag + repo label.

Memory & Tracing
- Append-only JSONL for events (plan, action, result, reward). Schemas validated in CI.
- Summaries for retrieval; link traces to commits and CI runs.

Autonomy Tiers
- T0: Read-only advice (default).
- T1: Branch writes; human reviews merge.
- T2: Auto-merge for low-risk classes behind policy gates.

Reward Model (Initial)
- Positive: tests pass (+3), coverage up (+1/2%), perf budget met (+2), docs updated (+1), approval (+2).
- Negative: tests fail (−3), type/lint fail (−2), revert (−4), perf regression (−2), security/data-quality fail (−3).
- Normalize by task difficulty and runtime; decay old data.

Evaluation Targets
- Win-rate ≥70% (T1); ≥85% for T2 low-risk set; reverts <1%.

Operational Loop (Agent ↔ CI)
- Planner proposes plan + diff; posts structured PR comment (plan, rationale, risk, test plan).
- Verifier runs the same CI gates locally (lint, type, tests, schema, security) and uploads artifacts.
- Critic summarizes CI outcomes and suggests improvements; logs saved as artifacts.
- Reward Aggregator computes reward from CI signals (tests, coverage delta, perf budgets, security findings, revert rate).
- Autonomy: all edits land on branches; T2 auto-merge only with fully green CI and within defined policy scope.

Kill-Switch & Rollback Triggers
- Kill-switch: disable agent writes via ENV `AGENT_WRITE=0` and repo label `agent-blocked`.
- Auto-rollback triggers: revert rate >1% rolling, anomaly spikes in CI failures, or policy violations; agent auto-creates a revert PR with repro pack.
