# Plan to Standardize Naming Conventions and Refactor Redundant Directories

## Executive Summary

This plan outlines the steps to address inconsistent naming conventions and redundant directories within the ISA project, as identified in the `project_review_report.md`. The core of this plan involves establishing a single, authoritative `isa/` root directory, consolidating existing redundant project structures, standardizing mode naming conventions, and creating essential missing documentation. These changes will significantly improve project clarity, maintainability, and adherence to established governance principles.

## Goals

1.  **Establish Authoritative `isa/` Root**: Create a new, clean `isa/` directory at the workspace root to serve as the single source of truth for the project.
2.  **Consolidate Redundant Directories**: Migrate relevant and non-redundant files from existing `isa/` related directories into the new authoritative `isa/` root.
3.  **Standardize Mode Naming**: Apply a consistent naming convention (PascalCase) to all modes within `isa/config/roo_mode_map.json`.
4.  **Create Missing Core Files**: Generate `isa_manifest.yaml` and `isa/roo_modes.md` with initial, structured content.
5.  **Update Documentation**: Ensure `CHANGELOG.md`, `isa/logs/agent_task_history.json`, and `isa/versions/version_tracker.json` are updated to reflect these structural changes.

## Detailed Plan

### Phase 1: Preparation and New Root Establishment

**Step 1.1: Create the New Authoritative `isa/` Directory**
*   **Action**: Create a new directory named `isa/` at the workspace root (`/Users/frisowempe/Desktop/isa_workspace/isa/`). This will be the new, clean project root.
*   **Rationale**: Provides a clear, unambiguous starting point for the consolidated project structure.

**Step 1.2: Create Foundational `isa_manifest.yaml`**
*   **Action**: Create the `isa_manifest.yaml` file inside the new `isa/` directory. This file will contain initial metadata, versioning, and critical file paths.
*   **Rationale**: Addresses a critical missing piece for project traceability and adherence to global instructions (Rule #3 and #9).

**Step 1.3: Create `isa/roo_modes.md`**
*   **Action**: Create the `isa/roo_modes.md` file inside the new `isa/` directory. This document will serve as a placeholder for detailed mode documentation.
*   **Rationale**: Addresses missing documentation crucial for understanding the multi-agent architecture (Rule #3).

### Phase 2: Consolidation and Migration

**Step 2.1: Identify and Prioritize Existing `isa/` Related Directories**
*   **Action**: Review the existing `isa/` related directories (e.g., `github-ISA-FullStack-Synced/`, `ISA_Future_Phases_Complete 2/`, `ISA_Phase4_SyncPack/`, etc.) to identify the most up-to-date and relevant content for migration. This will likely involve manual inspection or a more detailed content comparison.
*   **Rationale**: Prevents accidental loss of valuable work and ensures only current, necessary files are migrated.

**Step 2.2: Migrate Core `isa/` Content**
*   **Action**: Move the contents of the *current* `isa/` directory (e.g., `isa/context/ISA_Roadmap.md`, `isa/config/roo_mode_map.json`, `isa/core/`, `isa/reports/`, etc.) into the newly created authoritative `isa/` directory.
*   **Rationale**: Preserves existing, valid project structure and content under the new root.

**Step 2.3: Consolidate Relevant Files from Redundant Directories**
*   **Action**: Systematically copy or move relevant, non-redundant files and subdirectories from the identified redundant project roots (e.g., `github-ISA-FullStack-Synced/`, `ISA_Future_Phases_Complete 2/`, `ISA_Phase4_SyncPack/`) into the appropriate locations within the new authoritative `isa/` directory. This step will require careful manual review to avoid duplicating or overwriting files.
*   **Rationale**: Eliminates redundancy, streamlines project navigation, and prevents potential conflicts.

**Step 2.4: Archive Redundant Directories**
*   **Action**: After successful migration and verification, move the old, redundant `isa/` related directories to an `archive/` directory at the workspace root. Do NOT delete them immediately.
*   **Rationale**: Provides a safety net for recovery if any critical files were missed during migration.

### Phase 3: Standardization and Refinement

**Step 3.1: Standardize Mode Naming in `roo_mode_map.json`**
*   **Action**: Read `isa/config/roo_mode_map.json` from the new `isa/` directory. Modify mode names and slugs to follow a consistent PascalCase convention (e.g., `ROO-MODE-RESEARCH` becomes `ResearchMode`, `Orchestrator` remains `Orchestrator`).
*   **Rationale**: Improves readability, maintainability, and consistency across mode definitions.

**Step 3.2: Populate `isa/roo_modes.md`**
*   **Action**: Add initial content to `isa/roo_modes.md`, outlining each mode's purpose, assigned LLM, and key responsibilities, based on the updated `roo_mode_map.json` and general project understanding.
*   **Rationale**: Provides essential documentation for understanding the multi-agent architecture.

### Phase 4: Post-Refactoring Updates and Verification

**Step 4.1: Update Project Documentation**
*   **Action**: Update `CHANGELOG.md`, `isa/logs/agent_task_history.json`, and `isa/versions/version_tracker.json` to reflect the significant structural changes and file movements.
*   **Rationale**: Ensures traceability and adherence to global instructions (Rule #5, #15, #17).

**Step 4.2: Run `isa_validator.py`**
*   **Action**: Execute `isa_validator.py` to ensure consistency after the structural changes.
*   **Rationale**: Adherence to global instructions (Rule #10).

**Step 4.3: Invoke `isa_summarizer.py`**
*   **Action**: Since multiple files will be touched, invoke `isa_summarizer.py` to summarize the system-wide changes.
*   **Rationale**: Adherence to global instructions (Rule #11).

**Step 4.4: Suggest Documentation Awareness Updates**
*   **Action**: Suggest edits to `isa/context/governance.md` and `ISA_Roo_Definitive_Architecture_v1.md` to reflect the new directory structure and naming conventions.
*   **Rationale**: Adherence to global instructions (Rule #9).

## Follow-up Tasks (for User Collaboration)

*   **Detail "TBD" Sections in `ISA_Roadmap.md`**: Collaborate with stakeholders to define concrete timelines, Firebase actions, ISA features, Firebase priorities, and metrics for Phases 4-18 in `isa/context/ISA_Roadmap.md`.
*   **Review and Enhance Core Documentation**: Expand the "Data Flow and Interactions" and "Future Architectural Considerations" sections in `isa/context/ISA_Roo_Definitive_Architecture_v1.md`. Ensure `isa/context/governance.md` is comprehensive and up-to-date with all operational principles.

## Diagram: Project Refactoring Flow

```mermaid
graph TD
    A[Start: Project Review Report] --> B{User Confirms New ISA Root};
    B -- Yes --> C[Phase 1: Preparation & New Root Establishment];

    C --> C1[Create New isa/ Directory];
    C --> C2[Create isa/isa_manifest.yaml];
    C --> C3[Create isa/roo_modes.md];

    C --> D[Phase 2: Consolidation & Migration];
    D --> D1[Identify & Prioritize Existing Redundant Dirs];
    D --> D2[Migrate Core isa/ Content to New Root];
    D --> D3[Consolidate Relevant Files from Redundant Dirs];
    D --> D4[Archive Old Redundant Directories];

    D --> E[Phase 3: Standardization & Refinement];
    E --> E1[Standardize Mode Naming in isa/config/roo_mode_map.json];
    E --> E2[Populate isa/roo_modes.md];

    E --> F[Phase 4: Post-Refactoring Updates & Verification];
    F --> F1[Update CHANGELOG.md, agent_task_history.json, version_tracker.json];
    F --> F2[Run isa_validator.py];
    F --> F3[Invoke isa_summarizer.py];
    F --> F4[Suggest Documentation Awareness Updates];

    F --> G[End: Refactoring Plan Complete];