# Roo Modes Overview

This document provides a comprehensive overview of the various modes within the Roo multi-agent architecture, detailing their purpose, assigned LLM, and key responsibilities.

## Mode Definitions

### Orchestrator Mode
*   **Purpose**: Manages and coordinates the overall task execution, breaking down complex goals into subtasks and delegating them to appropriate modes.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: Task decomposition, subtask delegation, progress tracking, result synthesis, inter-mode communication.

### Architect Mode
*   **Purpose**: Focuses on planning, designing, and strategizing solutions, creating technical specifications, and brainstorming architectural approaches.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: System design, architectural planning, technical specification creation, problem breakdown, solution brainstorming.

### Code Mode
*   **Purpose**: Responsible for writing, modifying, and refactoring code across various programming languages and frameworks.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: Feature implementation, bug fixing, code improvement, file creation/modification.

### Debug Mode
*   **Purpose**: Specializes in troubleshooting issues, investigating errors, diagnosing problems, and identifying root causes.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: Systematic debugging, error analysis, logging, stack trace analysis, root cause identification.

### Ask Mode
*   **Purpose**: Provides explanations, documentation, and answers to technical questions, focusing on understanding concepts and existing code.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: Information retrieval, concept explanation, code analysis, recommendation generation.

### Claude Browser Mode v2.0
*   **Purpose**: Executes browser-based tasks, performs web research, and gathers information from online sources.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: Browser automation, web scraping, online research, error resolution intelligence, knowledge base maintenance.

### Research Mode (ROO-MODE-RESEARCH - *To be renamed to PascalCase*)
*   **Purpose**: Conducts in-depth research on specific topics, gathering and synthesizing information from various sources.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: Information gathering, data synthesis, knowledge acquisition.

### Validator Mode (ROO-MODE-VALIDATOR - *To be renamed to PascalCase*)
*   **Purpose**: Ensures consistency and adherence to project standards by running validation scripts and reporting outcomes.
*   **Assigned LLM**: [To be specified]
*   **Key Responsibilities**: Code validation, consistency checks, quality assurance.

---

**Note**: The "Assigned LLM" for each mode is currently a placeholder and should be updated with the specific LLM model assigned to each mode in the `isa/config/roo_mode_map.json` file.