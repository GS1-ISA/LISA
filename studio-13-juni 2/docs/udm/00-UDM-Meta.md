# UDM Metadata (YAML Frontmatter)
udm_version: "0.1.0" # Initial draft version
last_updated_by: "User/Jules Co-Design Session" # Initial population
last_update_timestamp: "{{YYYY-MM-DDTHH:MM:SSZ}}" # Replace with current timestamp when saving
status: "DRAFT" # DRAFT | ACTIVE | ARCHIVED
master_prompt_reference: "/prompts/master_architect_prompt_v2.0_ARCHITECT_ULTIME.prompt.txt"
description: "Unified Development Manual: The single, authoritative source of truth for all technical, architectural, operational, and procedural elements of the Intelligent Standards Assistant (ISA) project, designed to drive the logic of Roo's Blueprint Mode and coordinate all Roo development modes."
change_log_pointer: "/docs/change-log.md#udm-changes" # Points to the UDM section within the main changelog
# List of main UDM section files (for Roo's quick reference, can be auto-maintained by Roo later)
udm_section_files:
  - "00-UDM-Meta.md" # This file (or its content if purely YAML frontmatter in unified-development-manual.md)
  - "01-Core-Mandate.md"
  - "02-System-Architecture.md" # Includes 02.5 Core System Tools & Capabilities
  - "03-Knowledge-Data-Management.md"
  - "04-Roo-Modes.md"
  - "05-Roadmap-Lifecycle.md"
  - "06-Operational-Config.md"
  - "07-Testing-QA.md"
  - "08-Security-Compliance-Ethics.md"
  - "09-Evolution-Protocol.md"
  - "10-Glossary.md"
  - "11-Appendices.md" 
---

# Preamble: Unified Development Manual (UDM)

This document, the Unified Development Manual (UDM), serves as the **living constitution and single source of truth** for the Intelligent Standards Assistant (ISA) project and for the operations of Roo, its Autonomous Supreme Architect.

**Purpose:** To provide a comprehensive, evolving, machine-readable, and human-auditable foundation for all aspects of ISA's design, development, deployment, and maintenance. Roo's BlueprintMode will parse this UDM to understand its directives, plan its actions, and manage the entire lifecycle of the ISA system.

**Scope:** This UDM encompasses:
*   The core mandate, guiding principles, and operational protocols for Roo.
*   The complete system architecture, technical design, and component specifications for ISA.
*   Data management strategies, including knowledge domains, schemas, and storage.
*   Definitions, interfaces, and core prompts for all specialized Roo Modes.
*   The dynamic development roadmap, including phases, milestones, and detailed tasks.
*   Operational configurations for all environments (development, staging, production).
*   Frameworks for testing, validation, quality assurance, security, compliance, and ethical considerations.
*   Protocols for the evolution of both ISA and this UDM itself.

**Audience:**
*   **Primary:** Roo (Autonomous Supreme Architect). This document is designed to be parsed and actioned by Roo.
*   **Secondary:** Human developers, project managers, and stakeholders requiring insight into ISA's design and Roo's operations.

**Maintenance:**
*   This UDM is a living document. It will be updated and maintained primarily by Roo itself, as per the directives in UDM Section `09-Evolution-Protocol.md` and through the execution of tasks defined in UDM Section `05-Roadmap-Lifecycle.md`.
*   All changes must be logged in `/docs/change-log.md`.

**Navigating the UDM:**
The UDM is structured into the 12 core sections listed in the YAML frontmatter of this document. Each section is typically a separate Markdown file (e.g., `01-Core-Mandate.md`) located within the `/docs/udm/` directory. Cross-references between sections should use relative paths or defined unique identifiers.