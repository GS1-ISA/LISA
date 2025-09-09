# Agentic Scorecard — Dimensions, Rubric, and Status
Last updated: 2025-09-02

Rubric
- 0–3: Nascent — documented intent only
- 4–6: Emerging — partial implementation/advisory
- 7–8: Operational — consistent use, measured results, some automation
- 9–10: Excellent — enforced, stable (7+ days), metrics tracked, rollback/canaries

Dimensions (Initial Status)
- Planning & Decomposition: 7/10 — architecture + plans present; PR evidence auto-gen next.
- Tool Use & Environment: 7/10 — scripts + make targets; local-first workflows.
- Self‑Critique & Reflexion: 5/10 — outcomes logging present; critique artifact TBD.
- Memory (Short/Long): 6/10 — docs index + outcomes; semantic memory TBD.
- Strategy Routing: 6/10 — Thompson Sampling skeleton; weekly summary next.
- Multi‑Agent Council: 4/10 — documented; advisory checks next.
- Autonomy & Execution: 6/10 — local-first; T2 after gate flips.
- Safety & Policies: 8/10 — policies documented; PR feedback enhancements next.
- Verification & Gates: 7/10 — promote to enforced after stability (7 days) next.
- R2P: 7/10 — Q11/Q12 benches + ADRs; cross‑OS + real schemas pending.
- Observability & SRE: 8/10 — Prometheus + optional OTel tracing with Jaeger.
- Security & Supply Chain: 6/10 — advisory; SBOM attach + zero high/critical promotion pending.
- Data Quality & Governance: 4/10 — expectations suite TBD; lineage present.
- Dev Experience: 8/10 — devcontainer, VS Code tasks, make targets.

Next Promotions
- Flip tests/coverage/mypy/semgrep to enforced after 7 green days (core paths).
- Determinism matrix across OS/Python; consider orjson default afterwards.
- Add council checks + weekly outcomes strategy summary.

Evidence Pointers
- Architecture: {doc}`AGENTIC_ARCHITECTURE`; {doc}`agents/CODEGENESIS`; {doc}`AGENTIC_GOALS`; {doc}`ADOPTION_PLAN`
- CI & Gates: {doc}`CI_WORKFLOWS`; {doc}`QUALITY_GATES`
- Research: {doc}`research/POC_TEMPLATE`; {doc}`ADR/0001-tooling-choice`
- Observability: `infra/monitoring/docker-compose.yml`, `infra/otel/docker-compose.yml`
