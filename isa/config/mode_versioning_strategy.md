# Roocode Mode Versioning and Prompt Management Strategy

This document outlines the strategy for versioning Roocode modes, managing prompt updates, and introducing support for A/B testing of prompt engineering strategies.

## 1. Mode Versioning

Each Roocode mode (e.g., `ARCHITECT`, `CODER`) will implicitly be versioned through the overall system version tracked in `isa/versions/version_tracker.json`. Major architectural changes to a mode's role, core logic, or LLM assignment will trigger a minor version bump of the overall system.

## 2. Prompt Versioning

System prompts for each mode will be explicitly versioned to allow for granular tracking, rollback, and A/B testing.

*   **Naming Convention:** Prompt files will follow the convention: `isa/prompts/roo_mode_[slug]_prompt_v[MAJOR].[MINOR].prompt.txt`
    *   Example: `isa/prompts/roo_mode_architect_prompt_v1.0.prompt.txt`
*   **Versioning Rules:**
    *   **Major Version (`vX.0`):** Significant changes to a mode's core directives, persona, or introduction of new advanced prompt engineering techniques (e.g., CoT, Self-Refine, Confidence Calibration).
    *   **Minor Version (`vX.Y`):** Small refinements, clarity improvements, or addition/removal of few-shot examples without altering the core strategy.
*   **Deployment:** When a new prompt version is finalized, the `roo_mode_map.json` entry for that mode will be updated to point to the new prompt file path. Old prompt files will be moved to `isa/prompts/archive/`.

## 3. Prompt A/B Testing

To empirically determine the most effective prompt engineering strategies, a mechanism for A/B testing will be implemented.

*   **Mechanism:**
    1.  Define two (or more) versions of a mode's prompt (e.g., `v1.0` and `v1.1`).
    2.  The `ORCHESTRATOR` (or a dedicated `TRIGGER` mode) will be configured to randomly (or based on a specific policy) select which prompt version to load for a given mode instance.
    3.  Task execution logs will record which prompt version was used for each task.
    4.  A `VALIDATOR` or `AUDITOR` mode will analyze the outputs (e.g., code quality, research synthesis quality, task completion rate) associated with each prompt version.
    5.  Results will be aggregated and analyzed to identify the superior prompt version.
*   **Configuration:** A new field in `roo_mode_map.json` (e.g., `activePromptVersions: ["v1.0", "v1.1"]`) could indicate which prompt versions are active for A/B testing.

## 4. Mode Deprecation Logic

A formal process for deprecating and archiving modes is crucial to maintain a clean and efficient architecture.

*   **Identification:** `ARCHITECT` or `AUDITOR` identifies modes that are redundant, obsolete, or have been fully absorbed by new/enhanced modes. This can be triggered by architectural reviews or performance audits.
*   **Integration/Migration:**
    *   If a mode's functionality is fully absorbed (e.g., `ROO-MODE-ANALYZE-CONFIG` into `AUDITOR`), its specific directives, prompt elements, and any unique tools are migrated to the new mode's prompt and definition.
    *   Ensure no loss of functionality or context during migration.
*   **Soft Deprecation:**
    *   The mode's entry in `roo_mode_map.json` is marked with a `deprecated: true` flag and a `supersededBy: [new_mode_slug]` field.
    *   The `ORCHESTRATOR` is configured to issue a warning if it attempts to delegate a task to a deprecated mode, suggesting the `supersededBy` alternative.
*   **Hard Deprecation/Archival:**
    *   After a defined grace period (e.g., 3 months of soft deprecation), the mode's definition is moved from `roo_mode_map.json` to a historical archive file (e.g., `isa/config/archive/roo_mode_map_archive.json`).
    *   Its associated prompt files are moved from `isa/prompts/` to `isa/prompts/archive/`.
    *   All references to the deprecated mode in the UDM and other documentation are updated or removed.
*   **Documentation Update:** All deprecation actions are meticulously logged in `CHANGELOG.md` and `isa/logs/agent_task_history.json`. `isa/versions/version_tracker.json` is updated. `ISA_Roo_Definitive_Architecture_v1.md` and `isa/context/governance.md` are updated to reflect the current, active mode set.

This strategy ensures that the Roocode mode architecture remains agile, well-documented, and continuously optimized.