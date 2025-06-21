# 🕒 ISA Validation & Integration Test Schedule

This file defines the recurring automated validation logic across ISA Phase 14–18.

## 🔁 Cycle Schedule
- **Daily** – Light integrity checks (schema alignment, version diffs)
- **Weekly (Monday 07:00 UTC)** – Full multi-agent simulation run
- **Monthly (1st of Month)** – Governance drift audit and roadmap alignment review
- **Event-triggered** – On any commit to `PhaseXX/`, trigger simulation + validation pipeline

## 🛠️ Responsible Agents
- `SchemaValidatorAgent`
- `LangGraphDriftWatcher`
- `AutoRefactorValidator`
- `RooSyncTracker`

## 🗂️ Artifacts
- All logs stored in `/simulation_logs/integration_tests/YYYY_MM_DD.json`
- Updates pushed to `/VERSION.yaml` + `/docs/governance/ISA_Governance_Strategy.md`
- Summary delivered in `/docs/overview.md` dashboard

_Last generated on 2025-06-14_
