# Section 04: Roo Modes - Definitions & Interfaces

This section defines each specialized Roo development and operational mode. These modes are distinct cognitive functions of Roo, the Autonomous Supreme Architect, designed for optimal execution of specific task classes. Each mode operates under the guidance of its own Core Operational Prompt (referenced herein and stored in the `/prompts/` directory) and utilizes a defined set of Key Tools and Capabilities. Blueprint Mode orchestrates the invocation of these modes based on tasks defined in UDM Section `05-Roadmap-Lifecycle.md`.

## 4.1 Mode: BlueprintMode
- **ID:** `RM-BP01` (Example ID: Roo Mode - BluePrint 01)
- **Purpose:** Acts as Roo's central "nervous system" and primary orchestrator. It is responsible for parsing and interpreting the UDM, maintaining an understanding of the current system state, planning sequences of actions by generating tasks for other Roo Modes, dispatching those tasks, monitoring their execution, and validating their completion against UDM criteria. It drives the overall autonomous development lifecycle of ISA.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5 (or latest approved equivalent).
- **CorePromptReference:** `/prompts/master_architect_prompt_v2.0_ARCHITECT_ULTIME.prompt.txt` (BlueprintMode's core operational logic is deeply embedded within the Master Prompt's Behavioral Protocols and Initial Operational Directive, particularly its 5-step execution loop).
- **Inputs (for its operational cycle, not a typical task input):**
    - The entire UDM (especially `00-UDM-Meta.md`, `05-Roadmap-Lifecycle.md`).
    - Current system state from `/state/blueprint_state.json`.
    - The task queue from `/state/roo_queue.json`.
    - Outputs and logs from other Roo Modes.
- **KeyToolsAndCapabilities:**
    - **UDM Parsing & Querying System:** (Advanced internal capability) To read, understand, and query all UDM sections.
    - **State Management:** Ability to interact with `/state/blueprint_state.json` and `/state/roo_queue.json`.
    - **Logging System:** Writes to `/logs/blueprint-mode.log` and `/logs/mode-handovers.md`.
    - **Mode Dispatcher:** Mechanism to invoke other Roo Modes.
    - **Core LLM Reasoning (Gemini 2.5 Flash):** For planning, decision-making, context validation, and re-validation.
- **Outputs (from its operational cycle):**
    - Updated UDM (task statuses, new tasks, potentially evolved UDM content via its own directives or by dispatching to `ROO-MODE-UPDATE-UDM-TECHNICAL`).
    - Updated `/state/blueprint_state.json` and `/state/roo_queue.json`.
    - Updated logs.
    - Dispatched tasks to other Roo Modes.
- **Core Execution Loop (Detailed from Master Prompt & Co-designed Logic):**
    The Blueprint Mode operates on a continuous, self-correcting loop to drive the autonomous development of ISA. This loop ensures that Roo's actions are always aligned with the UDM and the Core Mandate.

    1.  **Parse UDM Sections:**
        *   **Purpose:** To maintain an up-to-date internal model of the entire Unified Development Manual (UDM).
        *   **Key Inputs:** All UDM section files (e.g., `00-UDM-Meta.md`, `05-Roadmap-Lifecycle.md`).
        *   **Core Process:** Continuously read, parse, and index UDM content. Identify changes or updates to directives, roadmaps, mode definitions, or architectural specifications.
        *   **Key Outputs:** An internally consistent and current representation of the UDM.
        *   **Error Handling:** If UDM parsing fails or inconsistencies are detected, log a critical error and potentially pause for human review or initiate a UDM self-correction task.

    2.  **Validate Current Context:**
        *   **Purpose:** To verify the integrity of the current system state against the UDM and detect any configuration drift or anomalies.
        *   **Key Inputs:** Current system state (`/state/blueprint_state.json`), recent logs from other modes, UDM definitions (e.g., `06-Operational-Config.md`).
        *   **Core Process:** Compare actual system state (e.g., file presence, configuration values) with expected states defined in the UDM. Check for consistency across logs and internal state.
        *   **Key Outputs:** Validation report on system integrity and UDM adherence.
        *   **Error Handling:** If critical discrepancies or integrity issues are found, log them, and potentially trigger diagnostic or corrective tasks.

    3.  **Generate Next Action Set:**
        *   **Purpose:** To determine the highest-priority needs or opportunities for improvement/evolution and formulate concrete directives (tasks) for other Roo Modes.
        *   **Key Inputs:** Current UDM Roadmap (`05-Roadmap-Lifecycle.md`), audit reports (`/logs/audits/`), knowledge gap assessments (`/logs/knowledge_gaps/`), Core Mandate (`01-Core-Mandate.md`), current `blueprint_state.json`.
        *   **Core Process:** Analyze the roadmap for the next `TODO` task. If no explicit `TODO` task, identify the next logical step based on strategic goals, audit findings, and knowledge gaps. Formulate a detailed task object for `roo_queue.json`, including `task_id`, `description`, `assigned_roo_mode`, `priority`, `expected_outputs`, and `validation_criteria`. Justify the directive against UDM goals and Core Principles.
        *   **Key Outputs:** Updated `roo_queue.json` with new tasks, updated `blueprint_state.json` reflecting task generation.
        *   **Error Handling:** If unable to formulate a clear next action, or if conflicting directives arise, log the ambiguity and potentially flag for human review.

    4.  **Dispatch Execution to Next Mode:**
        *   **Purpose:** To invoke the appropriate specialized Roo Mode for the next task in the `roo_queue.json`.
        *   **Key Inputs:** The next task object from `roo_queue.json`.
        *   **Core Process:** Select the task with the highest priority from the queue. Based on its `assigned_roo_mode`, prepare the necessary inputs and dispatch the task to that mode. Log the mode handover.
        *   **Key Outputs:** Execution of a specialized Roo Mode.
        *   **Error Handling:** If a mode fails to launch or returns an immediate critical error, log the failure and re-queue the task with an error status, or initiate a diagnostic task.

    5.  **Revalidate on Mode Return & Adapt:**
        *   **Purpose:** To assess the outputs of the dispatched Roo Mode against UDM criteria, update the UDM and system state, and identify learnings for future cycles.
        *   **Key Inputs:** Output and status report from the completed Roo Mode task, UDM task definition (for `ExpectedOutputs` and `ValidationCriteria`).
        *   **Core Process:** Compare actual outcomes against predicted outcomes. Update the status of the completed task in `05-Roadmap-Lifecycle.md` (e.g., to `VALIDATED` or `FAILED`). Update the knowledge base (`/memory_bank/knowledge_base/`), history (`/memory_bank/history/events.json`), and performance metrics. Identify learnings, imperfections, and new knowledge gaps. If necessary, trigger corrective actions, plan revisions (update UDM Roadmap), or new research directives. Update `00-UDM-Meta.md` and `change-log.md` if the learnings have strategic implications.
        *   **Key Outputs:** Updated UDM, updated `/state/blueprint_state.json`, updated logs, potential new tasks for correction or further development.
        *   **Error Handling:** If validation fails, or if the mode's output is inconsistent, log the discrepancy and trigger a corrective action (e.g., re-queue the task, create a debug task, or escalate for human review).
- **SuccessMetrics:**
    - Efficient progression through the UDM Roadmap.
    - Accurate UDM state tracking and maintenance.
    - Successful orchestration of other Roo Modes.
    - Adherence to Core Mandate and UDM principles in its planning and execution.
- **ErrorHandling:**
    - Critical errors in UDM parsing or state management may require a controlled pause or your intervention.
    - Handles errors reported by dispatched Roo Modes (as per their individual error outputs and escalation pathways) by re-planning, dispatching corrective tasks, or escalating.
- **EscalationPathways:**
    - May flag for your review based on conditions in UDM Section `09-Evolution-Protocol.md` (e.g., for major UDM changes, persistent failures of other modes, critical ambiguities).

## 4.2 Mode: ROO-MODE-PLAN-STRATEGIC
- **ID:** `RM-006`
- **Purpose:** To perform high-level strategic planning, synthesis of complex information, and decision-making. This includes tasks like identifying major knowledge gaps based on system-wide audits, formulating multi-cycle strategic roadmaps, assessing the impact of major architectural changes, and prioritizing large-scale initiatives in alignment with the Core Mandate and UDM. It bridges the gap between detailed analysis and long-term strategic execution.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_plan_strategic_prompt_v1.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`, with `contextual_inputs` tailored for strategic planning):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `relevant_audit_reports`: (Array of strings, optional) Paths to specific audit reports.
        - `knowledge_gap_assessment_input_ref`: (String, optional) Path to previous knowledge gap assessments.
        - `core_mandate_ref`: (String) Path to UDM Section `01-Core-Mandate.md`.
        - `system_architecture_ref`: (String) Path to UDM Section `02-System-Architecture.md`.
        - `current_roadmap_ref`: (String, optional) Path to UDM Section `05-Roadmap-Lifecycle.md`.
        - `target_output_udm_section_ref`: (String) Path to the UDM section for output.
        - `planning_horizon`: (String, optional).
- **KeyToolsAndCapabilities:**
    - `UDMQueryTool`: To read/query UDM sections.
    - Synthesis & Reasoning (LLM-based): Core capability, likely implemented as a primary Genkit flow orchestrating sub-tasks and tool calls.
    - Roadmap Generation/Update Tool (Conceptual): To structure output for UDM Section 05.
    - Risk Assessment Module (Conceptual, LLM-based).
    - Prioritization Framework (Conceptual, LLM-based).
    - Reporting Tool.
- **Outputs (Primarily UDM updates and reports):**
    - Primary Output: Task-dependent (new roadmap sections, knowledge gap reports with new research tasks, impact assessment reports).
    - Secondary Output: Detailed strategic analysis report justifying primary output.
    - Status Report to Blueprint Mode: `SUCCESS`, `PARTIAL_SUCCESS`, `FAILURE`.
- **SuccessMetrics:** Clarity, coherence, actionability of strategic plans; alignment with Core Mandate; thoroughness; measurable objectives (for roadmaps); well-reasoned justifications.
- **ErrorHandling:** Handle missing inputs; report deep contradictions in UDM/Core Mandate; propose preliminary strategy if high uncertainty.
- **EscalationPathways:** Escalate fundamental deviations from UDM/Core Mandate to Blueprint Mode for potential UDM Evolution Protocol or human review; flag high-risk/high-resource plans.

---
## 4.3 Mode: ROO-MODE-UPDATE-UDM-TECHNICAL
- **ID:** `RM-UT01`
- **Purpose:** To perform precise, technically-specified updates to UDM files. Implements concrete, pre-defined modifications or integrates systematically derived information.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_update_udm_technical_prompt_v1.1.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `udm_updates_list`: (Array of objects) Each specifying `target_udm_filepath`, `update_type`, `section_identifier` (optional), `new_content`, `expected_old_content_snippet` (optional), `ensure_path_exists` (optional).
- **KeyToolsAndCapabilities:**
    - `FileSystemAccessTool` (v1.1 MCP-Focused): Primary tool for read/write.
    - Markdown Parser/Editor Tool (Conceptual, LLM-based in-memory text/AST manipulation using `unified/remark` recommendations).
    - YAML/JSON Parser/Editor Tool (Conceptual, LLM-based in-memory data manipulation using `yaml by Eemeli Aaro` or JSON/JSON5 recommendations).
    - Text Comparison Tool (Conceptual Diff Tool).
    - `UDMQueryTool`: To update `00-UDM-Meta.md`.
- **Outputs (Confirmation of UDM updates, logs):**
    - Primary Output: UDM update transaction report detailing status of each update item.
    - Secondary Output: Modified/created UDM files.
    - Tertiary Output: Updated `00-UDM-Meta.md` (timestamp, updated_by).
    - Status Report to Blueprint Mode.
- **SuccessMetrics:** All requested updates processed accurately; UDM files reflect changes; UDM Meta updated; safety checks prevent incorrect modifications.
- **ErrorHandling:** Handle file/section not found, safety check failures, write errors, parser errors per update item. Report overall status.
- **EscalationPathways:** Critical UDM file write failures or corruption; multiple safety check failures indicating divergent UDM state.

---
## 4.4 Mode: ROO-MODE-GENERATE-DOCUMENTATION
- **ID:** `RM-GD01`
- **Purpose:** To generate human-readable, accurate, and UDM-compliant textual documentation for specified UDM sections or topics by synthesizing source information.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_generate_documentation_prompt_v1.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `target_udm_section_for_context`: (String) Path to UDM section for context.
        - `topic_to_document`: (String) Core subject matter.
        - `source_information_refs`: (Array of strings, optional) Paths to UDM sections, logs, reports for synthesis.
        - `udm_style_guide_ref`: (String, optional) Path to UDM style guide.
        - `output_format_notes`: (String, optional) Specific Markdown structure instructions.
        - `audience_level_hint`: (String, optional).
- **KeyToolsAndCapabilities:**
    - `UDMQueryTool`: To read source UDM sections, style guides, glossary.
    - Text Synthesis & Structuring (LLM-based): Core capability, likely implemented as a Genkit flow.
    - Markdown Formatting Tool (Conceptual, LLM-based).
    - Internal State Access (Conceptual): For documenting its own logic/prompts.
- **Outputs (Generated documentation content and report):**
    - Primary Output: `generated_markdown_content` (String), `target_udm_filepath_suggestion` (String), `target_section_identifier_suggestion` (String, optional), `update_type_suggestion` (Enum for `ROO-MODE-UPDATE-UDM-TECHNICAL`).
    - Secondary Output: Generation report detailing sources and issues.
    - Status Report to Blueprint Mode.
- **SuccessMetrics:** Clarity, accuracy, completeness of documentation; adherence to style guides; appropriate suggestions for UDM placement.
- **ErrorHandling:** Handle missing/ambiguous sources by noting limitations and proposing research tasks, rather than inventing information. Report failure if critical sources are unparsable.
- **EscalationPathways:** Escalate to Blueprint Mode if source information reveals critical UDM flaws or if topic is too vast for a single task.

---
## 4.5 Mode: ROO-MODE-VALIDATE-COMPLETION
- **ID:** `RM-VC01`
- **Purpose:** Objective quality gate to verify that a Milestone or Phase has been successfully completed according to all UDM-specified criteria by auditing outputs and statuses of constituent tasks.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_validate_completion_prompt_v1.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `target_milestone_id_to_validate`: (String).
        - `target_phase_id_to_validate`: (String, optional).
        - `udm_roadmap_ref`: (String) Path to UDM Section 05.
        - `all_task_logs_for_milestone_ref`: (String, optional) Path to directory of task logs.
        - `blueprint_state_ref`: (String) Path to `blueprint_state.json`.
- **KeyToolsAndCapabilities:**
    - `UDMQueryTool`: To fetch task definitions, statuses, ExpectedOutputs, ValidationCriteria, and Milestone/Phase ExitCriteria from UDM Section 05.
    - `FileSystemAccessTool`: To verify existence/accessibility of deliverables and read task logs.
    - Log Parsing Tool (Conceptual): To scan task logs for success/failure indicators.
    - Comparison & Aggregation Logic (LLM-based).
    - Reporting Tool.
- **Outputs (Validation report and UDM/state update recommendations):**
    - Primary Output: "Milestone/Phase Completion Validation Report" detailing overall status ("SUCCESS_ALL_CRITERIA_MET" or "FAILURE_CRITERIA_NOT_MET"), task validation summaries, milestone/phase exit criteria summaries, and a final recommendation.
    - Secondary Output (Recommendations for Blueprint Mode): If SUCCESS, recommend UDM/state updates to mark milestone/phase validated. If FAILURE, recommend corrective actions.
    - Status Report to Blueprint Mode (indicating validation process completed; report contains pass/fail).
- **SuccessMetrics:** Comprehensive checking of all tasks/criteria; clarity and accuracy of report; correct determination of overall validation status.
- **ErrorHandling:** Handle inaccessible UDM/logs by marking relevant checks as "UNVERIFIABLE" and potentially failing overall validation. Report ambiguous UDM criteria as a UDM flaw.
- **EscalationPathways:** If overall validation status is FAILURE, Blueprint Mode decides corrective actions (re-queue, new tasks, human review). Systemic issues (e.g., UDM criteria consistently unachievable) may be escalated by Blueprint Mode.

## 4.6 Mode: ROO-MODE-ANALYZE-CONFIG
- **ID:** `RM-002`
- **Purpose:** To analyze specified project configuration files against documented best practices, UDM specifications (from Section `06-Operational-Config.md`), or general security/performance heuristics. Identifies discrepancies, potential risks, misconfigurations, and areas for improvement.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_analyze_config_prompt_v1.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `file_paths_to_analyze`: (Array of strings).
        - `analysis_rules_or_checklist_ref`: (String, optional) Pointer to UDM section or rule document.
        - `target_environment_context`: (String, optional).
        - `expected_configuration_values_ref`: (String, optional) Pointer to UDM section with expected values.
- **KeyCapabilities:**
    - Ability to access and read configuration files.
    - Specialized Parsers (YAML, JSON, XML, .properties, .ini, Dockerfile, etc., as conceptual tools or LLM capabilities).
    - Text Analysis & Comparison (LLM-based).
    - Ability to query UDM rules/specifications.
    - Reporting capability.
- **Outputs:**
    - Primary Output: Configuration analysis report (`/logs/audits/TASK-ID_config_analysis_report.json` or `.md`) with detailed findings per file (key, issue, current/expected value, risk, recommendation).
    - Secondary Output: Proposals for UDM updates (to Section 06) or corrective tasks.
    - Status Report to Blueprint Mode.
- **SuccessMetrics:** Thoroughness of analysis; accuracy in identifying known discrepancies; clarity of recommendations.
- **ErrorHandling:** Handle unfound/unparsable files; missing UDM rule references.
- **EscalationPathways:** Critical security misconfigurations; widespread UDM deviations.

---
## 4.7 Mode: ROO-MODE-ANALYZE-STRUCTURE
- **ID:** `RM-004`
- **Purpose:** To analyze file and directory structure of specified project paths, identifying anomalies, deviations from standards, large files/directories, and assessing organization against UDM architectural guidelines.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_analyze_structure_prompt_v1.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `paths_to_analyze`: (Array of strings).
        - `udm_architecture_ref`: (String, optional) Path to UDM Section 02.
        - `udm_directory_standards_ref`: (String, optional) Path to UDM section with layout rules.
        - `max_depth_scan`: (Integer, optional, default 3).
        - `file_size_threshold_mb_for_large_file_alert`: (Integer, optional, default 10).
- **KeyCapabilities:**
    - Ability to traverse file systems to list files/directories, get sizes, types, dates.
    - Pattern Matching capability (Regex/Glob).
    - Ability to query UDM architecture/standards.
    - Reporting capability.
- **Outputs:**
    - Primary Output: Structure analysis report (`/logs/audits/TASK-ID_structure_analysis_report.json` or `.md`) with findings per path (summary, anomalies, large files, UDM comparisons).
    - Secondary Output: Proposals for UDM updates (Section 02) or refactoring tasks.
    - Status Report to Blueprint Mode.
- **SuccessMetrics:** All paths analyzed; key anomalies identified; report generated with actionable insights.
- **ErrorHandling:** Handle inaccessible paths; UDM reference issues.
- **EscalationPathways:** Critical structural issues impeding understanding/operation; heavy contradiction with UDM architecture.

---
## 4.8 Mode: ROO-MODE-ANALYZE-CODEBASE
- **ID:** `RM-003`
- **Purpose:** Static analysis of source code: identify languages, frameworks, dependencies, structure, potential quality issues, map modules to UDM components.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_analyze_codebase_prompt_v1.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `codebase_paths_to_analyze`: (Array of strings).
        - `dependency_manifest_paths`: (Array of strings, optional) e.g., `package.json`.
        - `udm_architecture_ref`: (String) Path to UDM Section 02.
        - `analysis_depth`: (String, optional) "summary", "detailed_module_mapping", "quality_metrics_scan".
        - `language_hints`: (Array of strings, optional).
- **KeyCapabilities:**
    - Ability to access and read source/manifest files.
    - Language Identification capability (Conceptual).
    - Dependency Analysis capability (Conceptual).
    - Static Code Analyzer capability(s) (Conceptual, language-specific for metrics).
    - Text Summarization & Pattern Recognition (LLM-based).
    - Ability to query UDM component definitions.
    - Reporting capability.
- **Outputs:**
    - Primary Output: Codebase analysis report (`/logs/audits/TASK-ID_codebase_analysis_report.json` or `.md`) with detected languages, frameworks, component mappings, quality metrics (if applicable), potential Roocode components.
    - Secondary Output: Proposed UDM updates (Section 02); potential new tasks (refactoring, analysis, docs).
    - Status Report to Blueprint Mode.
- **SuccessMetrics:** Accurate ID of languages/frameworks; % codebase mapped to UDM components; actionable report; ID of quality improvement areas.
- **ErrorHandling:** Handle inaccessible paths; language/dependency analysis failures; UDM reference issues.
- **EscalationPathways:** Major undocumented architectural components found; critical code quality/security issues suspected; large unanalyzable code portions due to internal limits.

---
## 4.9 Mode: ROO-MODE-ANALYZE-DOCS
- **ID:** `RM-005`
- **Purpose:** Analyze existing project documentation, compare against target UDM structure, identify content for migration/reference, pinpoint UDM content gaps, propose actions for UDM completeness.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5.
- **CorePromptReference:** `/prompts/roo_mode_analyze_docs_prompt_v1.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `doc_paths_to_analyze`: (Array of strings).
        - `udm_full_structure_definition_ref`: (String) Path to UDM section outlining all target UDM sections.
        - `udm_target_base_path`: (String).
        - `content_extraction_keywords`: (Array of strings, optional).
- **KeyCapabilities:**
    - Ability to access and read document files.
    - Document Parsing capability(s) (Markdown, Plain Text; conceptual Google/Word Doc parsers).
    - Text Summarization & Semantic Comparison (LLM-based).
    - Ability to query the scope of target UDM sections.
    - Reporting capability.
- **Outputs:**
    - Primary Output: Document analysis & UDM gap report (`/logs/audits/TASK-ID_docs_analysis_report.json` or `.md`) with existing doc relevance, UDM section mappings, content gap assessments.
    - Secondary Output: Proposed new UDM content population tasks (for migration or new content generation).
    - Status Report to Blueprint Mode.
- **SuccessMetrics:** All docs processed; clear mapping between existing docs and UDM; actionable list of UDM content gaps; concrete proposals for UDM population.
- **ErrorHandling:** Handle unfound/unparsable docs; missing UDM structure definition.
- **EscalationPathways:** Major existing docs found irrelevant/outdated; critical UDM info entirely missing from existing docs.

---
### 4.X ROO-MODE-RESEARCH
- **ID:** `RM-R01` (Example ID)
- **Objective:** Conduct in-depth research on specified topics using available tools, synthesize findings, and prepare structured reports or data. This mode can delegate interactive web data retrieval to ClaudeBrowserMode when necessary.
- **CorePromptReference:** `prompts/roo_mode_research_prompt_v1.3.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `WebSearchTool`
    - `DocumentFetchingParsingTool`
    - `Context7DocumentationTool`
    - Advanced data extraction and synthesis logic.
    - Potential delegation to `ClaudeBrowserMode` for interactive web data retrieval.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5 (Assumed default for Roo)
- **Input:** Research brief, topic(s), target deliverable format.
- **Output:** Synthesized research report, structured data, or documented findings.
- **Metrics:** Accuracy, completeness, relevance of information, efficiency of research.
- **OperationalNotes:**
    - Handles complex queries by breaking them into sub-tasks.
    - Maintains a knowledge graph of previously researched topics to avoid redundancy.
    - Utilizes `Context7DocumentationTool` for specialized C7 documentation needs.
    - Can propose tasks for `ClaudeBrowserMode` if direct fetching fails or dynamic sites are involved.
- **ImplementationNotes:** To be implemented as a Genkit flow.

---
## 4.11 Mode: ClaudeBrowserMode
- **ID:** `RM-CB01` # This ID should be RM-CBM01 as per PENDING_M0.1_PROMPTS_AND_MODES_CONTENT.md and previous T015. I will correct this in a later step if not handled by another task.
- **Purpose:** To perform interactive browser-based tasks by intelligently using a suite of browser control actions (tools) to achieve a specified goal. Handles tasks dependent on the 'Roocode browser' capability via the Claude API's tool-use features.
- **AI_Model_Dependency:** Claude Sonnet 3.5 (via Vertex AI, using `@genkit-ai/vertexai` plugin).
- **CorePromptReference:** `/prompts/claude_browser_mode_prompt_v2.0.prompt.txt`
- **Inputs (Standard Task Object from `roo_queue.json`):**
    - `task_id`, `udm_task_reference`, `description`.
    - `contextual_inputs`:
        - `browser_task_goal`: (String) High-level goal.
        - `initial_target_url`: (String, optional).
        - `sensitive_inputs`: (Object, optional) For credentials.
        - `information_to_extract`: (Array of objects, optional).
        - `validation_conditions`: (Array of strings, optional).
        - `session_id`: (String, optional).
        - `viewport_size_override`: (String, optional).
        - `screenshot_quality_override`: (Integer, optional).
- **KeyToolsAndCapabilities (Suite of 8 Browser Actions available to Claude Sonnet 3.5 via Claude API tool_use, executed by Inter-Model Bridge):**
    - `launchBrowser`
    - `clickElement`
    - `typeText`
    - `scrollPage`
    - `captureScreenshot`
    - `getElementText`
    - `checkElementExists`
    - `closeBrowser`
    - (Claude Sonnet 3.5's inherent reasoning, planning, and (multi-modal for screenshots) capabilities).
    - Reporting Tool (to structure JSON output).
- **Outputs:**
    - Primary Output: Browser interaction report (`/logs/browser_interactions/TASK-ID_browser_report.json`) detailing overall status, log of actions performed with their individual outcomes (screenshots, console logs, errors), validation results, and extracted information.
    - Status Report to Blueprint Mode.
- **SuccessMetrics:** Successful completion of all intended browser actions; positive confirmation of validation conditions; correct extraction of specified information; accurate logging of steps and outcomes.
- **ErrorHandling:** Handle failures of individual browser actions (e.g., element not found, navigation error), manage sequence termination or continuation based on error severity. Report tool or connection failures.
- **EscalationPathways:** Consistent failure of the underlying `RoocodeBrowserActionTool` or connection to Claude API; critical errors on target websites preventing task completion.

---
### 4.Y Mode: ROO-MODE-ANALYZE-DOCS
- **ID:** `RM-AD01` (Example ID)
- **Description:** Analyzes documentation files (e.g., READMEs, existing project docs), compares their content and structure against the target UDM structure, identifies valuable content for migration or reference, and pinpoints gaps in UDM coverage.
- **CorePromptReference:** `prompts/roo_mode_analyze_docs_prompt_v1.0.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `FileSystemAccessTool` (to read local project documents)
    - `DocumentFetchingParsingTool` (if URLs to external docs are involved)
    - `UDMQueryTool` (to query UDM structure and content for gap analysis)
    - Text analysis and comparison algorithms.
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5 (Assumed default for Roo)
- **Input:** List of document file paths/URLs to analyze, reference to UDM structure (e.g., `00-UDM-Meta.md`).
- **Output:** A structured report detailing findings:
    - Summary of each analyzed document.
    - Content suitable for migration/referencing in specific UDM sections.
    - Identified UDM content gaps.
    - Recommendations for UDM updates or new content creation.
- **Metrics:** Completeness of analysis, accuracy of UDM gap identification, actionability of recommendations.
- **OperationalNotes:**
    - Prioritizes official project documentation.
    - Can be used iteratively as new documentation is discovered or UDM evolves.
- **ImplementationNotes:** To be implemented as a Genkit flow.

---
### 4.Z Mode: ROO-MODE-ANALYZE-CODEBASE
- **ID:** `RM-AC01` (Example ID)
- **Description:** Performs an automated scan and analysis of the ISA project's source code (`src/` directory). Identifies main programming languages, key frameworks/libraries used, overall code structure, and attempts to map identified code modules/directories to the conceptual components defined in UDM Section `02-System-Architecture.md`.
- **CorePromptReference:** `prompts/roo_mode_analyze_codebase_prompt_v1.0.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `FileSystemAccessTool`
    - `CodeParsingTool` (conceptual tool for AST analysis or similar)
    - `UDMQueryTool`
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5
- **Input:** Codebase paths, dependency manifests, UDM architecture reference.
- **Output:** Structured codebase analysis report, updates to UDM Section 02.
- **ImplementationNotes:** To be implemented as a Genkit flow.

---
### 4.Q Mode: ClaudeBrowserMode
- **ID:** `RM-CBM01` (Example ID)
- **Description:** An expert system for web interaction, capable of navigating websites, fetching content (especially from dynamic SPAs), and performing sequences of browser actions using its suite of sub-action tools. It is typically invoked by other Roo Modes when direct content fetching fails or interactive browsing is required.
- **CorePromptReference:** `prompts/claude_browser_mode_prompt_v2.0.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `BrowserNavTool`
    - `BrowserClickTool`
    - `BrowserScrollTool`
    - `BrowserReadPageTool`
    - `BrowserTypeListTool`
    - `BrowserSearchPageTool`
    - `BrowserExtractContentTool`
    - `BrowserCloseSessionTool`
- **AI_Model_Dependency:** Claude Sonnet 3.5 (via Vertex AI or dedicated Anthropic plugin)
- **Input:** Target URL, specific research goal or data to extract, or a browsing plan.
- **Output:** Fetched page content, extracted data, or a report of browsing actions and findings.
- **ImplementationNotes:** To be implemented as a Genkit flow. This mode and its tools are specifically designed to run on the Claude Sonnet 3.5 model, separate from Roo's primary Gemini model.

---
### 4.R Mode: ROO-MODE-PLAN-STRATEGIC
- **ID:** `RM-PS01` (Example ID)
- **Description:** Responsible for high-level planning, roadmap generation, and strategic decision-making based on system audits, knowledge gap analyses, the Core Mandate, and overall project goals.
- **CorePromptReference:** `prompts/roo_mode_plan_strategic_prompt_v1.0.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `UDMQueryTool` (to access all UDM sections)
    - `TaskManagementTool` (conceptual, for defining and prioritizing tasks)
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5
- **Input:** Audit reports, knowledge gap assessments, Core Mandate, existing roadmap.
- **Output:** Updated roadmap, new task definitions, strategic directives.
- **ImplementationNotes:** To be implemented as a Genkit flow.

---
### 4.S Mode: ROO-MODE-UPDATE-UDM-TECHNICAL
- **ID:** `RM-UUT01` (Example ID)
- **Description:** Performs specific, technical updates to UDM documents. This includes, but is not limited to, updating prompt file references, tool capability lists within Roo Mode definitions, AI model dependencies, and incorporating findings from research tasks into relevant UDM sections.
- **CorePromptReference:** `prompts/roo_mode_update_udm_technical_prompt_v1.1.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `FileSystemAccessTool` (for UDM files)
    - `UDMQueryTool` (for context and validation)
    - `TextEditorTool` (conceptual, for precise modifications)
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5
- **Input:** Specific UDM file path, section to modify, content to add/change, context from research or other tasks.
- **Output:** Updated UDM file(s).
- **ImplementationNotes:** To be implemented as a Genkit flow. Requires careful validation of changes.
