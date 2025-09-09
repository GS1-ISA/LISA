# Adoption Plan — Agentic Enhancements (Step-by-Step, With Acceptance)
Last updated: 2025-09-02

Scope: This plan turns the scorecard and goals into a concrete, phased adoption path that we can execute locally-first and then promote to CI/gates when stable.

Phases & Milestones
1) Foundations (Week 0–2)
   - Outcomes Logging: Log per-task outcomes (strategy, status, coverage delta, type errors, duration) to `agent/outcomes/*.jsonl`.
   - Docs Integrity: Lint docs references and internal links; produce `docs/audit/docs_ref_report.md`.
   - PR Evidence Notes: Generate Plan/Diff/Evidence markdown at `agent/outcomes/PR_NOTES.md` for branch updates.
   - Determinism: Keep canonical JSON snapshot tests in advisories; document adoption notes (ADR-0003) — done.
   - Benchmarks (Q11/Q12): Update results and ADR adoption notes — done; retest on demand.
   Acceptance: Scripts exist, run locally via Make tasks; reports generated; determinism benches updated.

2) Hardening (Week 2–6)
   - Strategy Router: Implement minimal bandit (epsilon-greedy/Thompson later) over strategies; log rewards from outcomes.
   - Observability: Instrument critical paths with spans (OpenTelemetry optional), keep Prometheus metrics; ensure correlation IDs propagate.
   - Gates (prep): Add coverage no-regression and type surface summaries; time promotions after stability.
   - Memory: Add reuse hooks to pull similar past fixes from outcomes and docs index (`docs/audit/search_index.jsonl`).
   Acceptance: Strategy selected per task; weekly outcomes summary generated; spans visible when OTel present; Make targets exist.

3) Promotion (Week 6–10)
   - Flip Gates: Promote tests/coverage/type/semgrep to enforced for core paths after 7 green days; promote determinism + container smoke.
   - R2P: Run cross-OS determinism matrix (Q11) and validator benches on real schemas (Q12); update ADRs if behavior changes.
   - Council Simulation: Add internal checks (Architect/Tester/Security/Perf/User) on high-impact diffs; produce a short advisory comment block in PR notes.
   Acceptance: Gates enforced; zero regressions in 7-day window; council summaries appear for large diffs.

4) T2 Low-Risk Autonomy (Week 10+)
   - Auto-merge for docs/format/chore/refactors within guardrails; maintain revert bots and repro packs.
   - Security & Supply Chain: Enforce zero high/critical; attach SBOM to releases; waiver expiries surfaced.
   Acceptance: T2 class defined and proven safe with <1% revert rate; release artifacts include SBOM.

Implementation Tracks (What I will add)
- Outcomes Logger & Summary (scripts): CLI to append JSONL records; weekly summary to `docs/audit/agent_outcomes_summary.md`.
- Docs Linter (script): Verify Title and refs/link existence; write `docs/audit/docs_ref_report.md`.
- PR Notes Generator (script): Diff stats + evidence placeholders; write `agent/outcomes/PR_NOTES.md`.
- Strategy Router (skeleton): Simple arm stats and epsilon-greedy; update from outcomes.
- Make Targets: `outcomes-summary`, `docs-lint`, `pr-notes`.

Risk & Rollback
- Scripts do not alter code paths; low blast radius. If any report causes noise, disable via Make target while iterating.
