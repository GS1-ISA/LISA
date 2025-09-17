# Implementation Plan (30/60/90 day priorities)

## Objective

Execute the immediate governance and infra tasks so Roadmap and TODO reflect deliverables and the team can start integration work.

## Top-Level Checklist

- [ ] Deliver AI Project Charter ({doc}`AI_PROJECT_CHARTER`) — owner: eng-lead — Acceptance: charter reviewed by core team, linked from README

- [ ] Deliver Vector Store Schema ({doc}`VECTOR_STORE_SCHEMA`) — owner: data-engineer — Acceptance: ingestion manifests conform to schema, example produced

- [ ] Deliver Model Card ({doc}`model_cards/EXAMPLE`) — owner: data-science — Acceptance: model card committed and linked to experiments

- [ ] Deliver Data Catalog stub (data/data_catalog.yaml) — owner: data-engineer — Acceptance: dataset entries for vector index and golden datasets present

## 30 days (Sprint 1)

- Owners: eng-lead, data-engineer, data-science

- Tasks:

  - Finalize and review the three docs above; assign follow-up owners for enforcement in CI

  - Create 4 GitHub issues (charter, vector-schema, model-card, data-catalog) and link to TODO.md

  - Add a lightweight CI check that ensures docs/VECTOR_STORE_SCHEMA.md exists and data/data_catalog.yaml parses (advisory)

Acceptance: Issues created; PRs opened for any doc fixes; advisory CI passes.

## 60 days (Sprint 2)

- Tasks:

  - Implement ingestion manifest example under data/ingestion_manifests/ for isa_docs_v1

  - Wire a basic ingestion smoke script that validates chunking and embeddings against VECTOR_STORE_SCHEMA

  - Create the first example model card from template (done) and add experiment metadata for evaluator-v1

Acceptance: Ingestion manifest present; smoke script runs locally; model experiment metadata linked.

## 90 days (Sprint 3)

- Tasks:

  - Promote advisory checks to gates after 7 consecutive nightly runs (if stable)

  - Add replication / determinism checks for embeddings and canonical writer

  - Integrate model card checks into PR template for model changes

Acceptance: Gate promotion criteria documented and met; CI artifacts produced.

## Risks & Mitigations

- Risk: CI churn from new doc checks. Mitigation: start advisory, roll to enforced only after stability window.

- Risk: Ownership unknown. Mitigation: assign owners in CODEOWNERS and create issues.

## Next Steps (I'm going to do next unless you object)

1) Create issues for the four top-priority items and link them in TODO.md (requires GitHub API — ask if you want me to open them).

2) Add an ingestion manifest example (next sprint) and a smoke validation script.

## Requirements coverage

- Update Roadmap/TODO: Done (links added)

- Produce step-by-step implementation plan: Done (this file)

- Add data catalog and example model card: Done (stubs added)

## Status

Ready for review. Please tell me if you want me to open GitHub issues and/or wire the advisory CI check next.
