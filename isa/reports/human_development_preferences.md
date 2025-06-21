# Human Development Preferences in the ISA Project

This report outlines the key preferences and principles that guide the human (and agent) development experience within the ISA project, derived from the global instructions enforced across all Roo development modes. These preferences aim to ensure efficiency, clarity, consistency, traceability, and reliability throughout the development lifecycle.

## 1. Automation

The project strongly emphasizes automation to reduce manual effort, minimize human error, and ensure consistent execution of critical processes.

*   **Automated Environment Validation**: Ensuring `.venv` is active and `.env` files are loaded before execution (Instruction 1).
*   **Automated Context Restoration**: Reloading critical configuration and context files before major actions (Instruction 3).
*   **Automated Post-Edit Validation**: Running `isa_validator.py` after any `Code` or `Architect` action (Instruction 10).
*   **Automated System-Wide Summarization**: Invoking `isa_summarizer.py` when multiple files are touched (Instruction 11).
*   **Automated Task Requeuing**: Using the Boomerang pipeline for incomplete, unclear, or failed tasks (Instruction 12).
*   **Automated Debugger Escalation**: Routing input/output to `isa_debugger` if uncertainty or validation failures occur (Instruction 13).
*   **Automated API Key Validation**: Running `validate_llm_keys.py` before ISA activation (Instruction 14).
*   **Automated Snapshot and Version Bumping**: Creating snapshots and updating `version_tracker.json` after milestones (Instruction 15).
*   **Automated Rollback**: Reverting to the last file-based snapshot on validation failure (Instruction 16).
*   **Automated Dashboard Updates**: Updating `status_dashboard.md` and `roo_health_report.json` after config changes (Instruction 18).

## 2. Clarity and Consistency

A high degree of clarity and consistency is preferred to ensure predictability, reduce ambiguity, and streamline collaboration.

*   **Standardized Prompt Behavior**: Inheriting all prompt behavior from `isa/prompts/unified_autopilot.json` (Instruction 2) and avoiding prompt drift (Instruction 19).
*   **Explicit Prompt Structure**: All prompts must contain `task_intent`, `expected_outcome`, `output_type`, and `fallback_mode` (Instruction 6).
*   **Disciplined Path Management**: Adhering to preferred file locations and avoiding writes to the root directory (Instruction 7).
*   **Documentation Awareness**: Suggesting edits to governance and architecture documentation when mode, file structure, or project organization changes (Instruction 9).
*   **Comprehensive Logging**: Ensuring all operations are logged with active mode, affected files, task description, validator outcome, and milestone impact (Instruction 17).
*   **Centralized Status Reporting**: Updating a dashboard after configuration changes for clear system health overview (Instruction 18).

## 3. Traceability

Every action and change must be fully traceable to maintain an auditable history and facilitate debugging and understanding of system evolution.

*   **Traceable Edits Only**: All file modifications must use `write_to_file` or `apply_diff` (Instruction 4).
*   **Mandatory Post-Edit Logging**: Every modified or added file must trigger updates to `CHANGELOG.md`, `isa/logs/agent_task_history.json`, and `isa/versions/version_tracker.json` (Instruction 5).
*   **Version Checkpoints**: Creating snapshots and version bumps after milestones (Instruction 15).

## 4. Knowledge Sharing

Information is actively managed and shared to ensure all developers (human and agent) have access to necessary context and insights.

*   **Documentation Awareness**: Proactively suggesting updates to key documentation files (`governance.md`, `isa_manifest.yaml`, `ISA_Roo_Definitive_Architecture_v1.md`) when relevant changes occur (Instruction 9).
*   **System-Wide Change Summaries**: Generating summaries for changes affecting multiple files to provide high-level overviews (Instruction 11).
*   **Centralized Status Dashboard**: Maintaining an updated dashboard for configuration changes and system health (Instruction 18).

## 5. Efficiency/Streamlining

The development process is designed to be efficient, minimizing friction and optimizing workflows.

*   **Context Restoration**: Preventing rework by ensuring up-to-date context before major changes (Instruction 3).
*   **Respecting `.rooignore`**: Avoiding unnecessary processing or access to excluded files (Instruction 8).
*   **Graceful Handling of Incomplete Tasks**: Using Boomerang to manage and requeue tasks that are unclear or lack expected outcomes, preventing dead ends (Instruction 12).
*   **Automated Debugger Escalation**: Streamlining troubleshooting by automatically routing issues to the debugger (Instruction 13).

## 6. Safety/Reliability

Robust safety and reliability measures are embedded to ensure system stability, prevent errors, and enable quick recovery.

*   **Runtime Environment Validation**: Ensuring a correct and stable execution environment (Instruction 1).
*   **Controlled Edits**: Enforcing traceable edits and prohibiting undocumented modifications (Instruction 4).
*   **Path Discipline**: Preventing accidental writes to critical system areas (Instruction 7).
*   **Exclusion of Ignored Files**: Preventing unintended interactions with files specified in `.rooignore` (Instruction 8).
*   **Automated Validation**: Running `isa_validator.py` post-edit to ensure consistency and prevent errors (Instruction 10).
*   **API Key Validation**: Ensuring all necessary API keys are present before operation (Instruction 14).
*   **Automated Rollback**: Providing a mechanism to revert to a stable state upon validation failure (Instruction 16).
*   **Prompt Consistency**: Avoiding prompt drift to maintain predictable and reliable agent behavior (Instruction 19).

This structured approach ensures that the ISA project maintains a high standard of development quality, efficiency, and maintainability for both human and AI agents.