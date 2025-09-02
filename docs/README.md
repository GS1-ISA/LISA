Title: Documentation Overview — Quick Links and Maps
Last updated: 2025-09-02

Quick Links
- Roadmap: docs/ROADMAP.md
- Agentic Architecture: docs/AGENTIC_ARCHITECTURE.md
- Agentic Goals: docs/AGENTIC_GOALS.md
- Adoption Plan: docs/ADOPTION_PLAN.md
- Agentic Scorecard: docs/AGENTIC_SCORECARD.md
- Quality Gates: docs/QUALITY_GATES.md
- CI Workflows: docs/CI_WORKFLOWS.md
- Research Ops: docs/RESEARCH_OPERATIONS.md
- Knowledge Gaps: docs/RESEARCH_KNOWLEDGE_GAPS.md
- ADRs: docs/ADR
- Audit: docs/audit
- Full Index: docs/INDEX.md

Maintainers
- Update timestamps: `python3 scripts/auto_doc_update.py`
- Build index: `make index && python3 scripts/gen_docs_index.py`
- Lint references: `make docs-lint` (see `docs/audit/docs_ref_report.md`)
- Healthcheck: `make healthcheck` (see `docs/audit/healthcheck.md`)


Additional Ops Docs
- TECH_DEBT: docs/TECH_DEBT.md
- Migration Map: docs/MONOREPO_MIGRATION_MAP.csv
- Data Quality Plan: docs/data_quality/EXPECTATIONS_PLAN.md
