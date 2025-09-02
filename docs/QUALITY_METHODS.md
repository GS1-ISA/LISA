Title: Quality Methods & Consistency Charter
Last updated: 2025-09-02

Objective: Use consistent, evidence‑based quality methods across code, data, docs, and processes.

Core Methods
- Determinism: Canonical JSON writer + snapshot tests; cross‑OS matrix for parity.
- Gates: Lint (enforced), Types/Tests/Security (advisory → enforced after 7 green days), Memory Coherence, Docs build, Container smoke.
- Observability: Prometheus histograms (/metrics), structured logs with correlation IDs, optional OTel.
- Memory: Router + logs; coherence drift guard; nap‑time learning; privacy deletion audits; log snapshot artifacts.
- Coherence: Repo‑wide artefact graph; orphans/dead‑ends; terminology and traceability matrix; scorecard.
- Research‑to‑Production: Search ledger, POC protocol, replication, ADRs, adapters + flags.
- Orchestrator‑Only Policy: Enforce `ISA_FORBID_DIRECT_LLM=1` in environments that must not call LLMs directly; refactor app flows to use orchestrator layer.

Process
- PRs follow DoD; CI artifacts (coverage, type counts, coherence, memory logs) attached.
- Promotion: Any advisory check flips to enforced only after stable green (7‑day rule) with no active waivers.
- Documents: Auto‑update timestamps; docs lint; MkDocs build on PR (advisory) and nightly.

References
- docs/QUALITY_GATES.md — thresholds and promotion rules
- docs/CI_WORKFLOWS.md — pipelines and schedules
- docs/agents/MEMORY_ARCHITECTURE.md — memory policy
- docs/agents/ORCHESTRATION_ARCHITECTURE.md — orchestrator policy
- COHERENCE_SCORECARD.md — graph KPIs
