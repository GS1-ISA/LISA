# AI Project Charter

Intelligent Standards Assistant (ISA) - Charter

Last updated: 2025-09-04

## Purpose

This AI Project Charter summarizes scope, objectives, success metrics, stakeholders, and a Responsible-AI risk assessment for the Intelligent Standards Assistant (ISA) program represented in this repository. It is a living document intended to be referenced by project sponsors, engineers, and reviewers.

## Scope (In / Out)

### In scope

- Search, retrieval, summarization and QA assistance over standards and organizational policies.
- Structured, auditable answers with clickable citations to source material.

### Out of scope

- Legally binding advice or case-specific legal interpretations.
- Irreversible changes to production systems without explicit human waiver.

## Objectives & Success Criteria

- Reduce average time-to-find relevant standards content by 50% for core user scenarios (pilot metric).
- Achieve a human-evaluated answer relevance score ≥ 4.5/5 on an internal evaluation set for covered standards.
- Maintain a PR revert rate < 1% (rolling 90 days) when agents operate at T1/T2 autonomy tiers.

## Stakeholders & RACI

- Project Sponsor: Product Leadership
- Responsible: Engineering Team (repo owners)
- Accountable: Program / Release Manager
- Consulted: Legal & Compliance, Security, Data Stewards
- Informed: SRE, Support, End Users

## Responsible-AI Risk Assessment (summary)

- **Data Privacy:** PII must not be persisted in model training artifacts; incoming queries with PII must be redacted before long-term logging. Owner: Data Steward.
- **Algorithmic Bias:** Periodic fairness audits on curated slices; record results in model cards and audit reports. Owner: Data Science.
- **Explainability & Provenance:** All generated answers must include source citations and provenance metadata; models and indexes must be versioned.
- **Misuse Risk:** Surface clear disclaimers (e.g., "Not legal advice") for compliance/legal topics and link to primary sources.

## Maintenance & Review Cadence

- Charter review: quarterly or on significant scope change.
- Responsible-AI risk section: reviewed on each model/dataset change and after high-severity incidents.

## References

- [AGENTIC_ARCHITECTURE.md](AGENTIC_ARCHITECTURE.md)
- [AGENTIC_GOALS.md](AGENTIC_GOALS.md)
- [QUALITY_GATES.md](QUALITY_GATES.md)
