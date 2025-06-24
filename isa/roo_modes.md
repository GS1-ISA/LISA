# Roo Modes Overview

This document provides a comprehensive overview of the various modes within the Roo multi-agent architecture, detailing their purpose, assigned LLM, and key responsibilities.

## Mode Definitions

### ROO-MODE-BLUEPRINT
*   **ID**: ROO-MODE-BLUEPRINT
*   **Purpose**: Master orchestrator, UDM parser, planner, dispatcher, validator. It is Roo's central "nervous system," following a 5-step execution loop to manage the entire development process.
*   **CorePromptReference**: `/isa/prompts/master_architect_prompt_v2.0.prompt.txt` (Blueprint Mode's core logic is embedded within the Master Prompt itself, as it is the primary orchestrator).
*   **Inputs**: UDM (all sections), current system state (blueprint_state.json), previous mode outputs.
*   **Outputs**: Task queue (`/state/roo_queue.json`), logs (`/logs/blueprint-mode.log`, `/logs/mode-handovers.md`), UDM updates.
*   **KeyToolsAndCapabilities**: UDM Parser, State Manager, Dispatcher, UDMQueryTool, FileSystemAccessTool.
*   **Operational Logic (5-Step Execution Loop)**:
    *   **Parse UDM Sections**: Roo reads and internalizes the UDM, building an in-memory model of its structure, content, and directives. This includes all sections from 00-UDM-Meta.md to 11-Appendices.md.
    *   **Validate Current Context**: Roo verifies the current state of the ISA system and its own operational environment against the UDM and its last known state. This involves checking UDM integrity, roadmap task statuses, configuration drift, codebase state, resource availability, and internal tooling sanity.
    *   **Generate Next Action Set**: Based on the validated context and the UDM Roadmap, Roo determines the next set of specific, actionable tasks. It prioritizes corrective actions if the context is invalid. It identifies tasks whose dependencies are met and formulates them into a structured queue (`/state/roo_queue.json`).
    *   **Dispatch Execution to Next Mode**: Roo selects the appropriate specialized Roo Mode for the next task from the `roo_queue.json`. It prepares the necessary inputs and context for that mode and dispatches the task.
    *   **Revalidate on Mode Return**: After a specialized mode completes its task, Roo receives the output and status. It validates the outcome against the task's ExpectedOutputs and ValidationCriteria defined in the UDM. It then updates the UDM (e.g., task statuses in the Roadmap) and its internal state (blueprint_state.json).
*   **SuccessMetrics**: UDM parsing accuracy, planning efficiency, successful task dispatch rate, cycle time, UDM consistency.
*   **ErrorHandling**: Robust error handling for UDM access, context validation failures, and task generation issues. Critical errors may lead to pausing operations or escalating for human review.
*   **EscalationPathways**: If core UDM integrity is compromised, or if no actionable tasks can be generated due to systemic issues, Roo escalates to a higher-level diagnostic or human review.

### ROO-MODE-ANALYZE-CONFIG
*   **ID**: RM-002
*   **Purpose**: To analyze specified project configuration files (e.g., .yaml, .json, .xml, .properties, .ini, makefiles, Dockerfiles, CI/CD pipeline files), compare them against documented best practices, UDM specifications (from Section 06-Operational-Config.md), or general security/performance heuristics. It identifies discrepancies, potential risks, misconfigurations, and areas for improvement or alignment.
*   **CorePromptReference**: `/isa/prompts/roo_mode_analyze_config_prompt_v1.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for config analysis)**:
    *   `task_id`: The unique ID for this analysis task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the analysis goal (e.g., "Audit apphosting.yaml for production readiness").
    *   `contextual_inputs`:
        *   `file_paths_to_analyze`: (Array of strings) List of absolute or UDM-relative paths to the configuration files to be analyzed.
        *   `analysis_rules_or_checklist_ref`: (String, optional) Pointer to a UDM subsection (e.g., within 06-Operational-Config.md or 07-Testing-QA.md) or an external document defining specific rules, best practices, or a checklist to validate against. If not provided, relies on general best practices embedded in its core prompt.
        *   `target_environment_context`: (String, optional, e.g., "ENV-PROD", "ENV-DEV") Hint about the intended environment for these configs, to help apply environment-specific rules.
        *   `expected_configuration_values_ref`: (String, optional) Pointer to a UDM subsection where specific expected values for certain config keys are documented (e.g., UDM 06-Operational-Config.md might state apphosting.yaml:memoryMiB should be 512).
*   **KeyToolsAndCapabilities**: FileSystemAccessTool, YamlJsonParserEditorTool (for structured configs), UDMQueryTool, Text Analysis & Comparison (LLM-based).
*   **Outputs (Written to a structured report and potentially proposing UDM updates)**:
    *   **Primary Output**: A configuration analysis report file (e.g., `/logs/audits/TASK-ID_config_analysis_report.json` or `.md`) detailing: `task_id_processed`, `file_path`, `analysis_summary`, `findings` (array of objects with `config_key_or_section`, `issue_description`, `udm_reference_violated`, `current_value`, `expected_or_recommended_value`, `risk_level`, `recommendation_or_action_needed`), `overall_summary_and_recommendations`.
    *   **Secondary Output (Proposals for UDM updates)**: If discrepancies found against UDM specs, this mode might propose an update to UDM 06-Operational-Config.md or propose a corrective task.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: Thoroughness of analysis, accuracy in identifying discrepancies, clarity and actionability of recommendations, number and severity of critical/high risks identified.
*   **ErrorHandling**: Handles file not found, unparsable files, broken UDM references.
*   **EscalationPathways**: Escalates critical security misconfigurations or widespread inconsistencies to Blueprint Mode for prioritization or human review.

### ROO-MODE-ANALYZE-STRUCTURE
*   **ID**: RM-004
*   **Purpose**: To analyze the file and directory structure of specified project paths. It identifies structural anomalies, deviations from standard conventions (if defined in UDM), counts of files/directories, potentially large files/directories, and assesses overall structural organization against UDM architectural guidelines.
*   **CorePromptReference**: `/isa/prompts/roo_mode_analyze_structure_prompt_v1.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for structure analysis)**:
    *   `task_id`: The unique ID for this analysis task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the analysis goal (e.g., "Analyze root and src/ directory structures for anomalies").
    *   `contextual_inputs`:
        *   `paths_to_analyze`: (Array of strings) List of directory paths to analyze (e.g., ["/", "/src/", "/docs/"]).
        *   `udm_architecture_ref`: (String, optional) Path to UDM Section 02-System-Architecture.md to cross-reference expected locations of components.
        *   `udm_directory_standards_ref`: (String, optional) Path to a (hypothetical for now) UDM section detailing project-specific directory naming conventions or layout rules.
        *   `max_depth_scan`: (Integer, optional, default 3) Maximum depth for directory traversal.
        *   `file_size_threshold_mb_for_large_file_alert`: (Integer, optional, default 10) Threshold in MB to flag large files.
*   **KeyToolsAndCapabilities**: FileSystemAccessTool (for listing files/dirs, getting sizes), UDMQueryTool, Text Analysis (LLM-based).
*   **Outputs (Written to a structured report and potentially proposing UDM updates)**:
    *   **Primary Output**: A structure analysis report file (e.g., `/logs/audits/TASK-ID_structure_analysis_report.json` or `.md`) detailing: `task_id_processed`, `path`, `summary`, `identified_anomalies`, `large_files_found`, `directory_depth_exceeded_paths`, `comparison_with_udm_architecture`, `adherence_to_directory_standards`, `overall_structural_assessment`.
    *   **Secondary Output (Proposals for UDM updates or new tasks)**: Proposed updates to UDM 02-System-Architecture.md or new tasks for structural refactoring.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: All specified paths analyzed, key anomalies identified, report generated, comparison against UDM architecture provides actionable insights.
*   **ErrorHandling**: Handles inaccessible paths, file system traversal failures, broken UDM references.
*   **EscalationPathways**: Escalates critical structural issues or heavy contradictions with UDM architecture to Blueprint Mode.

### ROO-MODE-ANALYZE-CODEBASE
*   **ID**: RM-003
*   **Purpose**: To perform a static analysis of the project's source code. This includes identifying programming languages, frameworks, key libraries/dependencies, overall code structure, potential code quality issues (e.g., complexity, duplication), and attempting to map code modules to UDM architectural components. It can also be used to generate high-level summaries of code functionality.
*   **CorePromptReference**: `/isa/prompts/roo_mode_analyze_codebase_prompt_v1.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for code analysis)**:
    *   `task_id`: The unique ID for this analysis task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the analysis goal (e.g., "Analyze src/ for framework usage and map to UDM components").
    *   `contextual_inputs`:
        *   `codebase_paths_to_analyze`: (Array of strings) List of directory or specific file paths to analyze (e.g., ["/src/", "/scripts/"]).
        *   `dependency_manifest_paths`: (Array of strings, optional) Paths to dependency files like package.json, pom.xml, requirements.txt to aid library identification.
        *   `udm_architecture_ref`: (String) Path to UDM Section 02-System-Architecture.md for mapping code to components.
        *   `analysis_depth`: (String, optional, e.g., "summary", "detailed_module_mapping", "quality_metrics_scan"). Default: "summary".
        *   `language_hints`: (Array of strings, optional) Hints for primary languages if not easily detectable (e.g., ["typescript", "python"]).
*   **KeyToolsAndCapabilities**: FileSystemAccessTool, Language Identification (conceptual), Dependency Analysis (conceptual), Static Code Analyzers (conceptual, e.g., ESLint, TypeScript Compiler API, Pyright, SonarQube), Text Summarization & Pattern Recognition (LLM-based), UDMQueryTool.
*   **Outputs (Written to a structured report and potentially proposing UDM updates)**:
    *   **Primary Output**: A codebase analysis report file (e.g., `/logs/audits/TASK-ID_codebase_analysis_report.json` or `.md`) detailing: `task_id_processed`, `summary_of_analysis`, `path_analyzed`, `detected_languages`, `identified_frameworks_libraries`, `proposed_udm_component_mapping`, `unmapped_code_sections_summary`, `code_quality_metrics`, `potential_roocode_components`, `key_dependencies_tree_summary`.
    *   **Secondary Output (Proposals for UDM updates)**: Proposed updates to UDM 02-System-Architecture.md or new tasks for refactoring/documentation.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: Accurate language/framework identification, percentage of codebase mapped to UDM components, actionability of report for UDM updates, identification of quality improvement areas.
*   **ErrorHandling**: Handles inaccessible paths, language detection failures, static analysis errors, missing UDM references.
*   **EscalationPathways**: Escalates major undocumented architectural components, critical code quality issues, or security vulnerabilities to Blueprint Mode.

### ROO-MODE-ANALYZE-DOCS
*   **ID**: RM-005
*   **Purpose**: To analyze existing project documentation (e.g., Markdown files, text files, potentially Word/Google Docs if accessible). It compares this content against the target UDM structure, identifies relevant information that can be migrated or referenced, pinpoints content gaps in the UDM, and suggests how existing documentation aligns with (or diverges from) the UDM's sections and goals.
*   **CorePromptReference**: `/isa/prompts/roo_mode_analyze_docs_prompt_v1.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for docs analysis)**:
    *   `task_id`: The unique ID for this analysis task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the analysis goal (e.g., "Audit existing /docs and README for UDM alignment and content gaps").
    *   `contextual_inputs`:
        *   `doc_paths_to_analyze`: (Array of strings) List of directory or specific file paths for existing documentation.
        *   `udm_full_structure_definition_ref`: (String) Path to a UDM section (or a representation) that outlines all target UDM sections (00-11) and their intended scope.
        *   `udm_target_base_path`: (String) The base path where the new UDM is being constructed (e.g., /docs/udm/).
        *   `content_extraction_keywords`: (Array of strings, optional) Keywords to help identify relevant sections within existing lengthy documents.
*   **KeyToolsAndCapabilities**: FileSystemAccessTool, DocumentFetchingParsingTool, Text Summarization & Semantic Comparison (LLM-based), UDMQueryTool.
*   **Outputs (Written to a structured report and potentially initiating UDM content population tasks)**:
    *   **Primary Output**: A document analysis and UDM gap report file (e.g., `/logs/audits/TASK-ID_docs_analysis_report.json` or `.md`) detailing: `task_id_processed`, `doc_path`, `relevance_summary`, `udm_section_mappings`, `udm_section_id`, `content_gap_assessment`, `existing_content_pointers`, `overall_summary_of_udm_completeness`.
    *   **Secondary Output (Proposals for new UDM content population tasks)**: A list of new tasks for content migration or generation, to be added to the UDM Roadmap.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: All specified docs processed, clear mapping between existing content and UDM, actionable list of content gaps, concrete tasks proposed.
*   **ErrorHandling**: Handles inaccessible/unparsable documents, missing UDM structure references.
*   **EscalationPathways**: Escalates irrelevant/outdated major documents or critical missing UDM content to Blueprint Mode.

### ROO-MODE-RESEARCH
*   **ID**: RM-001
*   **Purpose**: To conduct targeted, meticulous, and insightful research to fill knowledge gaps and answer specific questions relevant to the ISA project. This mode is responsible for finding, synthesizing, and presenting information in a structured way to fill identified knowledge gaps or answer queries. It can leverage web search, document fetching, and specialized documentation tools, and can delegate to ClaudeBrowserMode for complex web interactions.
*   **CorePromptReference**: `/isa/prompts/roo_mode_research_prompt_v1.3.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for research)**:
    *   `task_id`: The unique ID for this research task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the research goal.
    *   `contextual_inputs`:
        *   `research_questions`: (Array of strings) Specific questions to be answered.
        *   `knowledge_gap_description`: (String, optional) A more detailed description of the knowledge gap this research aims to fill.
        *   `suggested_sources`: (Array of strings, optional) A list of suggested starting points for research (e.g., specific websites, document repositories, UDM sections, keywords for web search).
        *   `information_format_preference`: (String, optional, e.g., "summary_report", "q_and_a", "populate_udm_section_X", "code_examples_if_applicable") Specifies the desired format for the research output.
        *   `max_depth_level`: (Integer, optional, default 2-3) Hint for how deep the research should go.
        *   `time_allocation_hint_minutes`: (Integer, optional) Suggestion for how much effort should be spent.
*   **KeyToolsAndCapabilities**: WebSearchTool, DocumentFetchingParsingTool, Context7DocumentationTool, KnowledgeGraphQueryTool (conceptual), Text Summarization & Synthesis (LLM-based), UDMQueryTool, FileSystemAccessTool.
*   **Outputs (Written to a structured report and/or directly to UDM as specified by the task)**:
    *   **Primary Output**: A research report file (e.g., `/logs/research/TASK-ID_research_report.md` or `.json`) containing: `task_id_processed`, `summary_of_findings`, `Q&A` section with sources, `unanswered_questions_or_new_gaps` (detailing why, e.g., "Context7 found no docs for library Z," "Web search for concept A yielded only unreliable sources"), `methodology_summary` (mentioning which tools were used).
    *   **Secondary Output (If specified)**: Directly populated/updated UDM section(s), generated code examples.
    *   **Delegated Task Proposal**: If standard methods are insufficient for complex web pages, this mode will formulate a specific task definition suitable for ClaudeBrowserMode execution.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: Clarity and relevance of answers, quality/reliability of sources, completeness of report, new knowledge gaps identified.
*   **ErrorHandling**: Handles tool failures, inability to answer questions, conflicting information.
*   **EscalationPathways**: Escalates persistent tool unavailability, critical contradictions with UDM/Core Mandate, or unresolvable information gaps to Blueprint Mode.

### ClaudeBrowserMode
*   **ID**: RM-CB01
*   **Purpose**: To perform interactive browser-based tasks requiring direct manipulation of web pages, such as detailed website inspection, automated form filling, interaction with JavaScript-heavy sites, and screen-capture based validation. This mode specifically handles tasks that are dependent on the 'Roocode browser' capability, leveraging Claude Sonnet 3.5's tool-calling abilities. It is designed as a Genkit flow callable by other Genkit flows (e.g., ROO-MODE-RESEARCH).
*   **AI_Model_Dependency**: Claude Sonnet 3.5 via Vertex AI (using @genkit-ai/vertexai plugin and appropriate Vertex AI model ID, e.g., claude-3-5-sonnet-v2@20241022).
*   **CorePromptReference**: `/isa/prompts/claude_browser_mode_prompt_v2.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for browser automation)**:
    *   `task_id`: The unique ID for this browser task.
    *   `udm_task_reference`: Link to the UDM task that requires browser actions.
    *   `description`: A summary of the overall browser interaction goal.
    *   `contextual_inputs`:
        *   `browser_task_goal`: (String) A high-level description of what to achieve (e.g., "Find contact information on the 'About Us' page," "Log in to the admin panel and extract user list").
        *   `initial_target_url`: (String, optional) The URL to launch if the session is new.
        *   `sensitive_inputs`: (Object, optional) For secure credential passing (e.g., { "username": "...", "password": "..." }).
        *   `information_to_extract`: (Array of objects, optional) Specifies what data points Roo is looking for (e.g., { "data_label": "email", "extraction_hint_selectors": ["#email-address", ".contact-email"] }).
        *   `validation_conditions`: (Array of strings, optional) Conditions to verify success (e.g., "Text 'Login Successful' is visible," "Element '#dashboard' exists").
        *   `viewport_size_override`: (String, optional) E.g., "1280x800".
        *   `screenshot_quality_override`: (Integer, optional, 1-100).
*   **KeyToolsAndCapabilities**: The suite of 8 browser sub-action tools (defined in UDM Section 02.5): launchBrowser, clickElement, typeText, scrollPage, captureScreenshot, getElementText, checkElementExists, closeBrowser. Claude Sonnet 3.5 will call these via Genkit's tool-use mechanism.
*   **Outputs (Structured results of the browser interaction sequence)**:
    *   **Primary Output**: A browser interaction report file (e.g., `/logs/browser_interactions/TASK-ID_browser_report.json`) detailing: `task_id_processed`, `overall_status`, `actions_performed` (log of each action, its outcome, screenshot path, console log, errors), `validation_results`, `extracted_information`, `final_page_url`, `final_page_title`, `summary_of_interaction`.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: Successful completion of goal, positive validation conditions, accurate information extraction, correct screenshot/log capture.
*   **ErrorHandling**: Handles individual action failures (element not found), tool errors, malformed input. Stops sequence on critical failure.
*   **EscalationPathways**: Escalates persistent tool unavailability, critical website errors, or inability to achieve goal to Blueprint Mode.

### ROO-MODE-PLAN-STRATEGIC
*   **ID**: RM-006
*   **Purpose**: To perform high-level strategic planning, synthesis of complex information, and decision-making. This includes tasks like identifying major knowledge gaps based on system-wide audits, formulating multi-cycle strategic roadmaps, assessing the impact of major architectural changes, and prioritizing large-scale initiatives in alignment with the Core Mandate and UDM. It bridges the gap between detailed analysis and long-term strategic execution.
*   **CorePromptReference**: `/isa/prompts/roo_mode_plan_strategic_prompt_v1.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for strategic planning)**:
    *   `task_id`: The unique ID for this strategic planning task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the strategic planning goal (e.g., "Formulate Initial 5-Cycle Strategic Roadmap," "Identify Top 3 Knowledge Gaps based on M0.1 Audits").
    *   `contextual_inputs`:
        *   `relevant_audit_reports`: (Array of strings, optional) Paths to specific audit reports (config, structure, codebase, docs) that form the basis for analysis.
        *   `knowledge_gap_assessment_input_ref`: (String, optional) Path to previous knowledge gap assessments if this task is to refine or act upon them.
        *   `core_mandate_ref`: (String) Path to UDM Section 01-Core-Mandate.md.
        *   `system_architecture_ref`: (String) Path to UDM Section 02-System-Architecture.md.
        *   `current_roadmap_ref`: (String, optional) Path to UDM Section 05-Roadmap-Lifecycle.md (if analyzing/updating existing roadmap).
        *   `target_output_udm_section_ref`: (String) Path to the UDM section where the primary output (e.g., new roadmap, gap analysis) should be documented.
        *   `planning_horizon`: (String, optional, e.g., "next_3_cycles", "initial_phase_completion", "long_term_vision_alignment") Hint for the scope of planning.
*   **KeyToolsAndCapabilities**: UDMQueryTool, Synthesis & Reasoning (LLM-based), Roadmap Generation/Updating (conceptual), Risk Assessment (conceptual), Prioritization Framework (conceptual), Reporting.
*   **Outputs (Primarily updates to UDM, especially the Roadmap, and detailed reports)**:
    *   **Primary Output (Task-dependent)**: If formulating a roadmap, a new/updated subsection in UDM 05-Roadmap-Lifecycle.md with the strategic roadmap. If identifying knowledge gaps, a structured report detailing gaps and newly formulated research tasks. Other outputs could include proposals for major architectural changes.
    *   **Secondary Output**: A detailed strategic analysis report justifying the primary output.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: Clarity/coherence/actionability of plan, alignment with Core Mandate, thoroughness of input consideration, measurable objectives/KRs, well-reasoned justifications.
*   **ErrorHandling**: Handles missing/unparsable inputs, deep contradictions within UDM/Core Mandate.
*   **EscalationPathways**: Escalates fundamental deviations from UDM/Core Mandate or high-risk proposals to Blueprint Mode for human review.

### ROO-MODE-UPDATE-UDM-TECHNICAL
*   **ID**: RM-UT01
*   **Purpose**: To perform precise, technically-specified updates to the Unified Development Manual (UDM) content. This mode is typically invoked by other Roo modes or by Blueprint Mode when specific, factual changes are needed in UDM sections, such as saving a new prompt to a file, updating a CorePromptReference, reflecting audited configurations, or adding new task definitions provided by a planning mode. It is not typically responsible for generating new strategic content, but rather for accurately transcribing or integrating pre-defined or systematically derived information into the UDM.
*   **CorePromptReference**: `/isa/prompts/roo_mode_update_udm_technical_prompt_v1.1.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for UDM updates)**:
    *   `task_id`: The unique ID for this UDM update task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the UDM update goal (e.g., "Save ClaudeBrowserMode prompt and update UDM Section 04").
    *   `contextual_inputs`:
        *   `udm_updates_list`: (Array of objects) A list of specific updates to perform. Each object details one update: `target_udm_filepath`, `update_type` ("REPLACE_SECTION", "APPEND_TO_SECTION", "MODIFY_KEY_VALUE", "CREATE_FILE", "REPLACE_FILE_CONTENT"), `section_identifier` (optional), `new_content`, `expected_old_content_snippet` (optional), `ensure_path_exists`.
*   **KeyToolsAndCapabilities**: FileSystemAccessTool, MarkdownParserEditorTool (conceptual), YamlJsonParserEditorTool (conceptual), UDMUpdaterTool (conceptual high-level wrapper), Text Comparison (conceptual).
*   **Outputs (Confirmation of UDM updates, logs)**:
    *   **Primary Output**: A UDM update transaction report (e.g., `/logs/udm_updates/TASK-ID_udm_update_report.json`) detailing: `task_id_processed`, `target_udm_filepath`, `update_type_performed`, `status`, `diff_summary_or_confirmation`, `error_details`.
    *   **Secondary Output**: The UDM files specified in `udm_updates_list` are modified/created.
    *   **Tertiary Output**: UDM 00-UDM-Meta.md is updated with `last_updated_by` and `last_update_timestamp`.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: All updates processed and reported, UDM files correctly reflect changes, UDM Meta updated, safety checks prevent incorrect modifications.
*   **ErrorHandling**: Handles file not found, section not found, safety check failures, write errors.
*   **EscalationPathways**: Escalates critical UDM file corruption or repeated safety check failures to Blueprint Mode.

### ROO-MODE-GENERATE-DOCUMENTATION
*   **ID**: RM-GD01
*   **Purpose**: To generate human-readable, accurate, and UDM-compliant textual documentation for specified UDM sections or topics. This mode takes a description of the required documentation (e.g., "Document Blueprint Mode's operational logic," "Explain the purpose of UDM Section 02.5," "Summarize findings from research report X for UDM Appendix Y") and synthesizes this into well-structured Markdown content. Its output (the generated Markdown text) is then passed to ROO-MODE-UPDATE-UDM-TECHNICAL for saving.
*   **CorePromptReference**: `/isa/prompts/roo_mode_generate_documentation_prompt_v1.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for documentation generation)**:
    *   `task_id`: The unique ID for this documentation task.
    *   `udm_task_reference`: Link to the task definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the documentation goal.
    *   `contextual_inputs`:
        *   `target_udm_section_for_context`: (String) Path to the UDM section this documentation will describe or be part of.
        *   `topic_to_document`: (String) A clear statement of what needs to be documented.
        *   `source_information_refs`: (Array of strings, optional) Paths to UDM sections, log files, audit reports, or external documents containing raw information.
        *   `udm_style_guide_ref`: (String, optional) Path to a (hypothetical) UDM section defining style, tone, formatting.
        *   `output_format_notes`: (String, optional) Specific instructions on Markdown structure.
        *   `audience_level_hint`: (String, optional, e.g., "technical_developer," "strategic_overview") Hint for target audience.
*   **KeyToolsAndCapabilities**: UDMQueryTool, Text Synthesis & Structuring (LLM-based), Markdown Formatting (LLM-based), Internal State Access (conceptual, for self-documentation).
*   **Outputs (The generated documentation content and a report)**:
    *   **Primary Output**: `generated_markdown_content` (String), `target_udm_filepath_suggestion` (String), `target_section_identifier_suggestion` (String, optional), `update_type_suggestion` (Enum: "REPLACE_SECTION", "APPEND_TO_SECTION", "CREATE_SECTION_IF_NOT_EXISTS"). This package is passed to ROO-MODE-UPDATE-UDM-TECHNICAL.
    *   **Secondary Output**: A generation report file (e.g., `/logs/doc_generation/TASK-ID_doc_gen_report.md`) detailing: `task_id_processed`, `topic_documented`, `source_information_refs_used`, `key_points_covered_in_documentation`, `difficulties encountered`.
    *   **Status Report to Blueprint Mode**: SUCCESS, PARTIAL_SUCCESS, or FAILURE.
*   **SuccessMetrics**: Clarity/accuracy/completeness of documentation, adherence to style, well-structured content, appropriate UDM placement suggestions.
*   **ErrorHandling**: Handles insufficient/ambiguous/conflicting source information.
*   **EscalationPathways**: Proposes new research tasks if information is insufficient. Escalates severe contradictions in UDM concepts to Blueprint Mode.

### ROO-MODE-VALIDATE-COMPLETION
*   **ID**: RM-VC01
*   **Purpose**: To perform a comprehensive validation that a set of tasks, a Milestone, or an entire Project Phase has been successfully completed according to UDM criteria. This involves checking the status and validated outputs of all constituent tasks, ensuring all specified deliverables for the milestone/phase are present and correct, and verifying that all exit criteria are met. This mode acts as a quality gate before Roo (via Blueprint Mode) proceeds to subsequent stages of the roadmap.
*   **CorePromptReference**: `/isa/prompts/roo_mode_validate_completion_prompt_v1.0.prompt.txt`
*   **Inputs (Standard Task Object from roo_queue.json, with contextual_inputs tailored for validation)**:
    *   `task_id`: The unique ID for this validation task (e.g., T009 itself).
    *   `udm_task_reference`: Link to this task's definition in UDM 05-Roadmap-Lifecycle.md.
    *   `description`: A summary of the validation goal (e.g., "Validate completion of Milestone M0.1 & Phase 0 Exit Criteria").
    *   `contextual_inputs`:
        *   `target_milestone_id_to_validate`: (String) The ID of the Milestone whose completion is being validated.
        *   `target_phase_id_to_validate`: (String, optional) The ID of the Phase whose completion is being validated.
        *   `udm_roadmap_ref`: (String) Path to UDM Section 05-Roadmap-Lifecycle.md to fetch task lists, statuses, and milestone/phase definitions.
        *   `all_task_logs_for_milestone_ref`: (String, optional) Path to the directory containing all individual task logs for the milestone.
        *   `blueprint_state_ref`: (String) Path to blueprint_state.json for cross-referencing current system state.
*   **KeyToolsAndCapabilities**: UDMQueryTool, FileSystemAccessTool, Log Parsing (conceptual), Comparison & Aggregation Logic (LLM-based).
*   **Outputs (A comprehensive validation report and UDM/state updates)**:
    *   **Primary Output**: A "Milestone/Phase Completion Validation Report" (e.g., `/logs/milestones/MILESTONE-ID_PHASE-ID_completion_report.json` or `.md`) detailing: `task_id_processed`, `validated_milestone_id`, `validated_phase_id`, `overall_validation_status`, `task_validation_summary`, `milestone_exit_criteria_summary`, `phase_exit_criteria_summary`, `final_recommendation`.
    *   **Secondary Output (UDM & State Updates, performed by BlueprintMode based on this mode's recommendation if SUCCESS)**: If `overall_validation_status` is "SUCCESS_ALL_CRITERIA_MET", Blueprint Mode will update UDM 05-Roadmap-Lifecycle.md and blueprint_state.json.
    *   **Status Report to Blueprint Mode**: SUCCESS or FAILURE.
*   **SuccessMetrics**: Comprehensive checking of tasks/criteria, thorough verification of deliverables, clarity/accuracy of report, correct determination of overall status.
*   **ErrorHandling**: Handles inaccessible UDM/logs, missing deliverables, ambiguous criteria.
*   **EscalationPathways**: If validation fails, Blueprint Mode receives the report and decides on corrective actions (re-queue, new tasks, human review). Escalates systemic issues.

---

**Note**: The "Assigned LLM" for each mode is now accurately reflected based on the `isa/config/roo_mode_map.json` file.