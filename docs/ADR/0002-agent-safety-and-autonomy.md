# ADR 0002 — Agent Safety, Policies, and Autonomy Tiers
Last updated: 2025-09-02

Context
- The agent edits code and runs tools; safety must be explicit and enforceable.

Decision
- Policy engine with allowlists for commands and file paths, rate limits, and network scopes.
- All edits occur on ephemeral branches; merges require fully green CI (T1).
- Auto-merge (T2) permitted for low-risk classes after sustained SLO success.
- Auto-revert upon regression; attach repro packs; kill-switch available.

Kill-Switch & Triggers (Details)
- Kill-switch mechanisms: environment flag (`AGENT_WRITE=0`), repository label (`agent-blocked`), and CI job gate that blocks agent write steps when set.
- Rollback triggers: rolling revert rate >1%, sudden spike in CI failures on agent-authored PRs (>2x baseline), or policy breach (security/data-quality gate failures). On triggers, agent proposes a revert PR and notifies maintainers.

Autonomy Promotion & Review
- Promotion criteria: Tier advancement only after 4 consecutive weeks meeting autonomy SLOs (win-rate, reverts, latency), with no critical incidents.
- Review cadence: monthly autonomy review; incidents are postmortemed with action items.

Consequences
- Lower risk of destructive actions; auditable trails; controlled autonomy growth.

Status: Accepted
