# ISA Project Governance

This document outlines the governance principles and operational guidelines for the Intelligent Standards Assistant (ISA) project, including its mode architecture, versioning, and prompt management strategies.

## Roocode Mode Architecture (v2.1)

The Roocode Mode Architecture v2.1 introduces a refined set of specialized AI agents, each with a clear mission and optimized LLM assignment, designed to enhance the ISA project's autonomy, resilience, and intelligence.

**Mode Matrix (v2.1 Proposed):**

| Slug | Name | Model | Thinking Budget | Role Summary | Tools | Prompt Style |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `orchestrator` | 🪃 Orchestrator | `claude-3.5-sonnet` | 1000 | Central command, task decomposition, workflow management, delegation. | `new_task`, `attempt_completion` | Guided Planning, State Tracking |
| `architect` | 🏗️ Architect | `gemini-2.5-flash` (Dynamic) | -1 | Strategic planning, system design, problem breakdown, technical specification. | `read_file`, `search_files`, `list_code_definition_names` | CoT, Multi-Perspective Analysis, Confidence Calibration |
| `code` | 💻 Code | `claude-3.5-sonnet` | 5000 | Production-level code generation, refactoring, file updates. | `read_file`, `apply_diff`, `write_to_file`, `insert_content`, `search_and_replace` | Self-Refine, Inline Test Cases, Artifacts |
| `ask` | ❓ Ask | `gemini-2.5-flash-lite-preview-06-17` | 1000 | Quick lookups, simple queries, basic explanations. | `read_file`, `search_files` | Direct Answer, Summarization |
| `debug` | 🪲 Debug | `gemini-2.5-flash` | -1 | Root cause analysis, error investigation, problem diagnosis. | `read_file`, `search_files`, `execute_command` | Analytical Problem-Solving, Hypothesis Testing |
| `research` | ROO-MODE-RESEARCH | `claude-3.5-sonnet` | -1 | External/internal document research, synthesis, conflict identification. | `use_mcp_tool` (browser), `read_file`, `search_files` | Confidence Calibration, Source Verification |
| `validator` | ROO-MODE-VALIDATOR | `claude-3.5-sonnet` | 5000 | Rigorous validation against specs, rules, quality gates. | `read_file`, `search_files` | Rule-Based, Structured Reporting |
| `synthesizer` | ROO-MODE-SYNTHESIZER | `claude-3.5-sonnet` | 5000 | Integrate and synthesize diverse outputs into coherent final products/reports. | `read_file` | Narrative Coherence, Nuance Preservation |
| `auditor` | ROO-MODE-AUDITOR | `gemini-2.5-flash` | 5000 | Proactive Guardian/Inspector: compliance review, tech debt, versioning, inter-agent message monitoring, heartbeat checks. | `list_files`, `search_files`, `read_file` | Proactive Monitoring, Compliance Checklists |
| `brainstormer` | ROO-MODE-BRAINSTORMER | `gemini-2.5-flash` | 5000 | Creative solutions, naming, interface ideas, impasses. | N/A | Divergent Thinking, Controlled Hallucination, Multi-Perspective Analysis |
| `human-input` | ROO-MODE-HUMAN-INPUT | `N/A` | 0 | Interface for human input, approval, clarification, injection. | N/A | Clear Prompting, Contextual Resumption |
| `dependency-monitor` | Dependency Monitor | `gemini-2.5-flash` | 1000 | Checks CI/build, lint, and package health. | `execute_command` (for build/lint tools), `read_file` (package.json) | Status Reporting, Anomaly Detection |
| `devops-gcp` | DevOps/GCP Mode | `gemini-2.5-flash` | -1 | Manages Firebase/GCP deployments, emulators, and credential rotation. | `execute_command` (Firebase CLI, gcloud CLI) | Secure Operations, State Management |
| `key-rotation` | Key Rotation Mode | `gemini-2.5-flash` | 500 | Handles LLM API key rotation and management. | `execute_command` (secret manager tools) | Secure Operations, Scheduled Tasks |
| `memory-sync` | Memory Sync Mode | `gemini-2.5-flash` | -1 | Syncs session state and embeddings into long-term memory bank. | `write_to_file`, `use_mcp_tool` (vector DB) | Data Consistency, Knowledge Graph Integration |
| `reject` | Reject Mode | `gemini-2.5-flash-lite-preview-06-17` | 100 | Safe fallback response mode ("I can't do that"). | N/A | Clear Communication, Loop Prevention |
| `trigger` | Trigger Mode | `gemini-2.5-flash-lite-preview-06-17` | 100 | Initiates model switching based on task complexity or resource quotas. | N/A (internal logic) | Rule-Based, Threshold Monitoring |

## Mode Deprecation Logic

As defined in `isa/config/mode_versioning_strategy.md`, the deprecation process involves:
1.  **Identification:** `ARCHITECT` or `AUDITOR` identifies redundant/obsolete modes.
2.  **Integration/Migration:** Functionality is absorbed by new/enhanced modes.
3.  **Soft Deprecation:** Mode is marked `deprecated: true` and `supersededBy` in `roo_mode_map.json`. `ORCHESTRATOR` issues warnings.
4.  **Hard Deprecation/Archival:** After a grace period, mode definition and prompts are moved to `isa/config/archive/` and `isa/prompts/archive/` respectively. All UDM references are updated.

## Versioning and Prompt Design Strategies

As defined in `isa/config/mode_versioning_strategy.md`:
*   **Mode Versioning:** Implicitly tied to overall system version (`isa/versions/version_tracker.json`).
*   **Prompt Versioning:** Explicitly versioned (e.g., `roo_mode_[slug]_prompt_v[MAJOR].[MINOR].prompt.txt`) for granular tracking and rollback.
*   **Prompt A/B Testing:** `ORCHESTRATOR` (or `TRIGGER` mode) dynamically selects prompt versions, with `VALIDATOR`/`AUDITOR` analyzing outcomes.

## Branching Strategy and Pull Request Process

The ISA project adheres to a **GitHub Flow** branching strategy. All contributions must follow the guidelines outlined in [`CONTRIBUTING.md`](CONTRIBUTING.md), which details:

*   **Branching:** Feature branches off `main`.
*   **Pull Requests:** Mandatory for all merges, utilizing `PULL_REQUEST_TEMPLATE.md`.
*   **Code Ownership:** Enforced via `.github/CODEOWNERS`.
*   **Branch Protection:** Critical branches (`main`) require status checks and code owner approvals.

## Tool Mappings and LLM Roles per Mode

Detailed tool mappings and LLM roles are integrated into the Mode Matrix above. Key LLM assignments are:
*   **Claude 3.5 Sonnet:** `ORCHESTRATOR`, `RESEARCH`, `CODER`, `VALIDATOR`, `SYNTHESIZER` (for nuanced tasks).
*   **Gemini 2.5 Flash:** `ARCHITECT` (for structured planning), `DEBUGGER`, `AUDITOR`, `BRAINSTORMER`, and new utility modes.
*   **Dynamic LLM Selection:** `ARCHITECT` can dynamically switch between Gemini and Claude based on task nature, orchestrated by `ORCHESTRATOR`.