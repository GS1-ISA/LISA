# Plan for Refining Custom Mode Definitions

This plan outlines the necessary modifications to `isa/config/roo_mode_map.json` and `isa/roo_modes.md` to integrate the new `KnowledgeGraphMode` and ensure consistency across the ISA project's mode definitions.

## 1. Changes to `isa/config/roo_mode_map.json`

The `isa/config/roo_mode_map.json` file will be updated to include the `KnowledgeGraphMode` and to standardize the naming conventions for existing modes.

### 1.1. Adding `KnowledgeGraphMode`

A new mode entry will be added to the `modes` array in `isa/config/roo_mode_map.json`.

*   **Slug**: `knowledgeGraph`
*   **Name**: `🧠 KnowledgeGraph`
*   **Model**: `gemini-2.5-flash`
*   **Thinking Budget**: `-1`
*   **Description**: "To provide a dedicated interface for agents to interact with the Neo4j Knowledge Graph, enabling structured storage, retrieval, and manipulation of knowledge for advanced reasoning, contextual understanding, and data-driven decision-making within the ISA system."

**Rationale**:
*   **Slug and Name**: The slug `knowledgeGraph` follows the camelCase convention used for other modes, and the name `🧠 KnowledgeGraph` provides a clear, descriptive, and emoji-enhanced identifier.
*   **Model**: `gemini-2.5-flash` is chosen for its efficiency and capability in handling structured data interactions, which is crucial for database operations.
*   **Thinking Budget**: A value of `-1` indicates no specific thinking budget limit, allowing for flexible execution of varied graph operations, which can range from simple lookups to complex queries.
*   **Description**: This description directly reflects the core purpose and scope defined in the `KnowledgeGraphMode Design Document`.

### 1.2. Adjustments to Existing Modes' Configurations

To ensure consistency and adhere to the PascalCase naming convention noted in `isa/roo_modes.md`, the slugs for `researchMode` and `validatorMode` will be updated.

*   **`researchMode`**:
    *   **Old Slug**: `researchMode`
    *   **New Slug**: `ResearchMode`
*   **`validatorMode`**:
    *   **Old Slug**: `validatorMode`
    *   **New Slug**: `ValidatorMode`

**Rationale**:
*   **Consistency**: This change aligns the slugs in `roo_mode_map.json` with the PascalCase naming convention indicated in `isa/roo_modes.md`, improving overall consistency and readability across the mode definitions.

## 2. Changes to `isa/roo_modes.md`

The `isa/roo_modes.md` file will be updated to document the new `KnowledgeGraphMode` and to clarify existing mode descriptions, including updating placeholder LLM assignments.

### 2.1. Documenting `KnowledgeGraphMode`

A new section will be added to `isa/roo_modes.md` to describe the `KnowledgeGraphMode`.

*   **Heading**: `### KnowledgeGraph Mode`
*   **Purpose**: "To provide a dedicated interface for agents to interact with the Neo4j Knowledge Graph, enabling structured storage, retrieval, and manipulation of knowledge for advanced reasoning, contextual understanding, and data-driven decision-making within the ISA system."
*   **Assigned LLM**: `gemini-2.5-flash`
*   **Key Responsibilities**: "CRUD operations on nodes and relationships, executing Cypher queries, structured knowledge retrieval, input/output validation, security safeguards for KG interactions."

**Rationale**:
*   **Comprehensive Documentation**: This new section provides a clear and concise overview of the `KnowledgeGraphMode`'s role, its assigned model, and its primary functions, making it easily understandable for any agent or human reviewing the mode definitions. The details are directly extracted from the `KnowledgeGraphMode Design Document`.

### 2.2. Updates to Existing Mode Descriptions for Clarity or Consistency

Several updates will be made to existing entries in `isa/roo_modes.md`:

*   **Update "Assigned LLM" Placeholders**: All instances of `[To be specified]` for "Assigned LLM" will be replaced with the actual model names from `isa/config/roo_mode_map.json`.
    *   `Orchestrator Mode`: `claude-3.5-sonnet`
    *   `Architect Mode`: `gemini-2.5-flash`
    *   `Code Mode`: `claude-3.5-sonnet`
    *   `Debug Mode`: `gemini-2.5-flash`
    *   `Ask Mode`: `gemini-2.5-flash-lite-preview-06-17`
    *   `Claude Browser Mode v2.0`: This mode is not explicitly listed in `roo_mode_map.json` with a slug `claude-browser-mode-v2-0`, but its description matches `ResearchMode`'s purpose. I will assume `ResearchMode` is the equivalent and assign `claude-3.5-sonnet`. If `Claude Browser Mode v2.0` is a distinct mode, it should be added to `roo_mode_map.json` first. For now, I will update the `ResearchMode` entry.
    *   `Research Mode`: `claude-3.5-sonnet`
    *   `Validator Mode`: `claude-3.5-sonnet`
*   **Rename `Research Mode` and `Validator Mode` Headings**: The headings for `Research Mode` and `Validator Mode` will be updated to reflect the PascalCase naming convention, removing the `(*To be renamed to PascalCase*)` note.
    *   **Old**: `### Research Mode (ROO-MODE-RESEARCH - *To be renamed to PascalCase*)`
    *   **New**: `### ResearchMode`
    *   **Old**: `### Validator Mode (ROO-MODE-VALIDATOR - *To be renamed to PascalCase*)`
    *   **New**: `### ValidatorMode`

**Rationale**:
*   **Accuracy**: Populating the "Assigned LLM" fields ensures that `isa/roo_modes.md` accurately reflects the current model assignments, providing up-to-date information for developers and agents.
*   **Clarity and Consistency**: Renaming the headings to PascalCase removes the temporary note and aligns the documentation with the intended naming convention, improving the overall clarity and professionalism of the `roo_modes.md` file.

## 3. Rationale

The proposed changes are driven by the need to formally integrate the `KnowledgeGraphMode` into the ISA system's operational framework and to enhance the consistency and accuracy of existing mode definitions. By updating both the configuration (`roo_mode_map.json`) and the documentation (`roo_modes.md`), we ensure that:

1.  **Functional Integration**: The `KnowledgeGraphMode` is properly registered and configured, allowing the orchestrator and other agents to delegate tasks related to knowledge graph interactions.
2.  **System Cohesion**: Standardizing naming conventions (e.g., PascalCase for mode slugs and headings) improves the overall readability and maintainability of the system's configuration and documentation.
3.  **Transparency**: Accurate documentation of assigned LLMs and mode responsibilities provides clear guidance for understanding the capabilities and limitations of each agent mode.

This plan ensures that the ISA system's mode definitions are robust, consistent, and ready to leverage the new `KnowledgeGraphMode` effectively.

## Next Steps

Once this plan is reviewed and approved, I will switch to `code` mode to implement these changes in the specified files.
