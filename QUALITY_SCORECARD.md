Title: Quality Scorecard — Baseline
Last updated: 2025-09-02

Scores (0–100) — Initial qualitative baseline
- Correctness: 85 — All app tests pass locally; determinism snapshots present.
- Test coverage & quality: 75 — Coverage reported; mutation/advisory/nightly planned.
- Performance: 70 — Perf benches exist (Q11/Q12); broader profiling pending.
- Security: 70 — Bandit/pip-audit advisory; SBOM/Trivy weekly workflows configured.
- Maintainability: 80 — Type-check clean on app; ruff enforced; modular memory router.
- Documentation quality: 85 — Roadmap/TODO/architecture and new guild docs in place.
- Operational health: 75 — CI workflows robust; nightly/weekly schedulers enabled; metrics endpoint present.
- Accessibility & UX: 60 — Planned audits; basic UI docs present.

Notes
- Improve coverage and mutation testing; add perf budgets on hot paths; expand security gates to enforced after stability.

