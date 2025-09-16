# Documentation Overview — Quick Links and Maps
Last updated: 2025-09-02

## Quick Links
- Roadmap: docs/ROADMAP.md
- Agentic Architecture: docs/AGENTIC_ARCHITECTURE.md
- CLI Quickstart: README.md (Run the Research Crew)
- Orchestration & Interop: docs/agents/ORCHESTRATION_ARCHITECTURE.md
- Memory Architecture: docs/agents/MEMORY_ARCHITECTURE.md
- Diplomacy & Standards Guilds: docs/guilds/DIPLOMACY_STANDARDS_GUILDS.md
- Quality Methods: docs/QUALITY_METHODS.md
- Ops Runbook (Memory DSR): docs/ops/memory_privacy_dsr.md
- Security Policy: SECURITY.md
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
- Integration Prompts: docs/agents/INTEGRATION_PROMPTS.md

## Maintainers
- Update timestamps: `python3 scripts/auto_doc_update.py`
- Build index: `make index && python3 scripts/gen_docs_index.py`
- Lint references: `make docs-lint` (see `docs/audit/docs_ref_report.md`)
- Healthcheck: `make healthcheck` (see `docs/audit/healthcheck.md`)

## Notes
- This repository supports both CLI and API access; FastAPI server is available and running on http://localhost:8001
- Container workflows can now access `/metrics` endpoint for monitoring
- See README.md for server setup and API documentation

## Additional Ops Docs
- TECH_DEBT: docs/TECH_DEBT.md
- Migration Map: docs/MONOREPO_MIGRATION_MAP.csv
- Data Quality Plan: docs/data_quality/EXPECTATIONS_PLAN.md
