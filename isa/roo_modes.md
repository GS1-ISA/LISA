# Roo Modes Overview

This document provides a comprehensive overview of the various modes within the Roo multi-agent architecture, detailing their purpose, assigned LLM, and key responsibilities.

## Mode Definitions

### Orchestrator Mode
*   **Purpose**: Manages and coordinates the overall task execution, breaking down complex goals into subtasks and delegating them to appropriate modes.
*   **Assigned LLM**: `claude-3.5-sonnet`
*   **Key Responsibilities**: Task decomposition, subtask delegation, progress tracking, result synthesis, inter-mode communication.

### Architect Mode
*   **Purpose**: Focuses on planning, designing, and strategizing solutions, creating technical specifications, and brainstorming architectural approaches.
*   **Assigned LLM**: `gemini-2.5-flash`
*   **Key Responsibilities**: System design, architectural planning, technical specification creation, problem breakdown, solution brainstorming.

### Code Mode
*   **Purpose**: Responsible for writing, modifying, and refactoring code across various programming languages and frameworks.
*   **Assigned LLM**: `claude-3.5-sonnet`
*   **Key Responsibilities**: Feature implementation, bug fixing, code improvement, file creation/modification.

### Debug Mode
*   **Purpose**: Specializes in troubleshooting issues, investigating errors, diagnosing problems, and identifying root causes.
*   **Assigned LLM**: `gemini-2.5-flash`
*   **Key Responsibilities**: Systematic debugging, error analysis, logging, stack trace analysis, root cause identification.

### Ask Mode
*   **Purpose**: Provides explanations, documentation, and answers to technical questions, focusing on understanding concepts and existing code.
*   **Assigned LLM**: `gemini-2.5-flash-lite-preview-06-17`
*   **Key Responsibilities**: Information retrieval, concept explanation, code analysis, recommendation generation.

### Claude Browser Mode v2.0
*   **Purpose**: Executes browser-based tasks, performs web research, and gathers information from online sources.
*   **Assigned LLM**: `claude-3.5-sonnet`
*   **Key Responsibilities**: Browser automation, web scraping, online research, error resolution intelligence, knowledge base maintenance.

### ResearchMode
*   **Purpose**: Conducts in-depth research on specific topics, gathering and synthesizing information from various sources.
*   **Assigned LLM**: `claude-3.5-sonnet`
*   **Key Responsibilities**: Information gathering, data synthesis, knowledge acquisition.

### ValidatorMode
*   **Purpose**: Ensures consistency and adherence to project standards by running validation scripts and reporting outcomes.
*   **Assigned LLM**: `claude-3.5-sonnet`
*   **Key Responsibilities**: Code validation, consistency checks, quality assurance.

### KnowledgeGraph Mode
*   **Purpose**: To provide a dedicated interface for agents to interact with the Neo4j Knowledge Graph, enabling structured storage, retrieval, and manipulation of knowledge for advanced reasoning, contextual understanding, and data-driven decision-making within the ISA system.
*   **Assigned LLM**: `gemini-2.5-flash`
*   **Key Responsibilities**: CRUD operations on nodes and relationships, executing Cypher queries, structured knowledge retrieval, input/output validation, security safeguards for KG interactions.

---

**Note**: The "Assigned LLM" for each mode is now accurately reflected based on the `isa/config/roo_mode_map.json` file.