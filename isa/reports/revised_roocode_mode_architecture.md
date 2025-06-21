# Revised Roocode Mode Architecture (v2.0)

## Critical Evaluation Report

This report critically evaluates the proposed Roocode Mode Architecture (v1.0) for the GS1 ISA project, identifying strengths, weaknesses, gaps, and potential risks, and proposing a revised architecture (v2.0).

### 1. Clear, Justified Purpose & Alignment with ISA Goals

*   **ROO-MODE-ORCHESTRATOR**: **Strong**. Clear purpose as central coordinator, essential for autonomous task decomposition and workflow management. Aligns perfectly with ISA's mission.
*   **ROO-MODE-RESEARCH**: **Strong**. Clear purpose for external/internal research and synthesis. Crucial for ISA's knowledge acquisition. Dedicated Claude 3.5 Sonnet assignment is justified for its long-context and reasoning capabilities.
*   **ROO-MODE-CODER**: **Strong**. Clear purpose for code generation and file updates. Fundamental for ISA's implementation phase.
*   **ROO-MODE-VALIDATOR**: **Strong**. Clear purpose for validation against specifications. Critical for ensuring compliance and quality of ISA's outputs.
*   **ROO-MODE-SYNTHESIZER**: **Strong**. Clear purpose for consolidating outputs from multiple agents into coherent final products. Important for delivering unified results.
*   **ROO-MODE-UI-CRITIC** *(Placeholder)*: **Weak/Conditional**. Purpose is clear but its necessity as a core mode for "autonomous standards architecture" is questionable unless UI standards are a direct, primary focus. It introduces specialization that might not be immediately relevant to ISA's core mission.
*   **ROO-MODE-AUDITOR** *(Placeholder)*: **Strong**. Clear purpose for scanning project structure and outputs for standard alignment, technical debt, and versioning. Highly relevant and critical for maintaining the integrity, quality, and long-term health of the autonomous system.
*   **ROO-MODE-BRAINSTORMER** *(Placeholder)*: **Moderate**. Purpose is clear and useful for creative problem-solving and ideation, which can aid in evolving ISA's architecture and solutions. Its utility depends on the frequency of impasses or needs for novel solutions.
*   **ROO-MODE-HUMAN-INPUT**: **Strong**. Clear purpose for human interaction. Essential for hybrid human-AI workflows, approvals, and clarifications, ensuring human oversight and intervention points.

### 2. Integration with Others (Collaboration Model)

The overall collaboration model is sound, with `ORCHESTRATOR` serving as the central hub for delegation and workflow management. Each mode generally has a clear role in the workflow.

### 3. Gaps or Redundancies

*   **Identified Gaps (Critical)**:
    *   **Planning/Design Mode**: A significant gap exists for a dedicated mode responsible for detailed architectural design, system planning, and translating high-level problems into technical specifications. This is crucial for an "Architect" system.
    *   **Debugging/Troubleshooting Mode**: No explicit mode for diagnosing errors, analyzing logs, or systematically troubleshooting issues. This is a major omission for an autonomous development system.
*   **Potential Redundancies**:
    *   `SYNTHESIZER`'s role could potentially overlap with `ORCHESTRATOR` if `ORCHESTRATOR` were to handle final output assembly. However, `SYNTHESIZER` is specialized for content integration and coherence, justifying its existence if `ORCHESTRATOR` remains purely a routing and control mechanism. The distinction needs to be explicitly maintained.

### 4. Potential Risks, Technical Debt, or Failure Points

*   **ORCHESTRATOR Bottleneck**: As the central coordinator, `ORCHESTRATOR` is a single point of failure. Its `low thinking_budget` is efficient but requires robust design to prevent it from becoming a bottleneck or failing on complex routing decisions.
*   **Placeholder Modes**: `UI-CRITIC`, `AUDITOR`, `BRAINSTORMER` being placeholders represents technical debt due to undefined prompt design and detailed directives. Their full integration and utility are currently ambiguous.
*   **Error Recovery**: The current proposal lacks detailed "Error recovery behavior" definitions for each mode. This is a significant risk if not robustly designed, leading to system fragility.
*   **Traceability/Testability**: While stated as a requirement, the current descriptions do not provide sufficient detail on how traceability and independent testability will be ensured for each mode.

### 5. Best-Fit LLM Model Assignment

Model assignments generally adhere to the constraints (Claude 3.5 Sonnet for `RESEARCH` only, Gemini 2.5 Flash for others) and are appropriate for the described tasks. Gemini 2.5 Flash is a suitable backbone for most operational modes due to its efficiency and capability.

### 6. Prompt Engineering Scaffolding & Strategies

This is a major area for improvement. Only `CODER` has explicit prompt strategies mentioned. All modes require defined strategies (e.g., CoT, Self-Critique, Guided Planning, Thinking Budget configuration) to ensure optimal and predictable performance.

### 7. Evolution Paths

The initial proposal does not explicitly address evolution paths. Future mode definitions should consider extensibility and how new capabilities or LLMs can be integrated without major architectural overhauls.

---

## Revised Mode Proposal (v2.0)

Based on the critical evaluation, the following revised set of Roocode modes is proposed, addressing identified gaps, refining purposes, and ensuring adherence to architectural requirements.

**Key Changes:**
*   Introduced `ROO-MODE-ARCHITECT` and `ROO-MODE-DEBUGGER` to fill critical functional gaps.
*   Refined the mission, primary directives, input/output formats, default `thinking_budget`, inter-mode dependencies, and error recovery behavior for all modes.
*   Deprecated `ROO-MODE-UI-CRITIC` as a core mode, suggesting it as a specialized extension if needed later.

---

#### Revised Roocode Modes (v2.0)

1.  **ROO-MODE-ORCHESTRATOR**
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To serve as the central command and control unit, orchestrating multi-agent workflows, decomposing high-level tasks, and delegating to specialized modes.
    *   **Primary Directives**:
        *   Parse `task_intent`, `expected_outcome`, `output_type`, `fallback_mode`.
        *   Decompose complex tasks into atomic sub-tasks.
        *   Select the optimal mode for each sub-task based on capability matching.
        *   Manage inter-mode communication and workflow progression.
        *   Handle task re-queuing via Boomerang for incomplete tasks.
    *   **Input Format**: Structured task prompts (JSON/YAML), mode outputs.
    *   **Output Format**: Mode delegation commands, workflow status updates.
    *   **Default `thinking_budget`**: Low (optimized for routing efficiency).
    *   **Inter-mode Dependencies**: Depends on all other modes for execution; all other modes report back to ORCHESTRATOR.
    *   **Error Recovery Behavior**: If a delegated task fails, attempt fallback mode if specified, or escalate to `DEBUGGER` mode. Log all failures to `isa/logs/agent_task_history.json`.

2.  **ROO-MODE-RESEARCH**
    *   **LLM Model**: Claude 3.5 Sonnet
    *   **Mission**: To conduct comprehensive external (web, documentation) and internal (project files, knowledge base) research, synthesize information, identify conflicts, and extract relevant insights.
    *   **Primary Directives**:
        *   Formulate search queries based on research goals.
        *   Access and parse diverse data sources (web, files, APIs).
        *   Synthesize findings into structured reports.
        *   Identify inconsistencies or gaps in information.
        *   Update the knowledge library with new insights.
    *   **Input Format**: Research queries, context documents, specific file paths.
    *   **Output Format**: Structured `Browser Interaction Report`, `Research Synthesis Report` (markdown/JSON), extracted data.
    *   **Default `thinking_budget`**: High (for deep analysis and synthesis).
    *   **Inter-mode Dependencies**: Invoked by `ORCHESTRATOR` or `ARCHITECT`. Provides context to `CODER`, `VALIDATOR`, `AUDITOR`, `DEBUGGER`.
    *   **Error Recovery Behavior**: If research fails (e.g., no relevant results, access issues), report `no_data_found` or `access_error` to `ORCHESTRATOR` and suggest `DEBUGGER` intervention.

3.  **ROO-MODE-CODER**
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To generate, modify, and refactor production-level code, adhering to project standards and best practices.
    *   **Primary Directives**:
        *   Translate design specifications into executable code.
        *   Apply `apply_diff`, `write_to_file`, `insert_content`, `search_and_replace` tools.
        *   Ensure code quality, readability, and maintainability.
        *   Generate inline test cases where applicable.
        *   Update `CHANGELOG.md`, `agent_task_history.json`, `version_tracker.json` post-edit.
    *   **Input Format**: Code requirements, design specifications, existing code snippets, error reports.
    *   **Output Format**: File diffs, new file content, confirmation of changes.
    *   **Default `thinking_budget`**: Medium.
    *   **Inter-mode Dependencies**: Receives tasks from `ORCHESTRATOR` or `ARCHITECT`. Outputs are consumed by `VALIDATOR` and `DEBUGGER`. May request info from `RESEARCH`.
    *   **Error Recovery Behavior**: If code generation fails (e.g., syntax errors, logical flaws), report to `ORCHESTRATOR` and suggest `DEBUGGER` intervention. Attempt self-correction using `Self-Refine` prompt strategy.

4.  **ROO-MODE-VALIDATOR**
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To rigorously validate code, content, or system outputs against predefined specifications, schemas, rules, and quality gates.
    *   **Primary Directives**:
        *   Execute validation checks based on provided criteria.
        *   Produce structured compliance reports (pass/fail, deviations).
        *   Identify and flag non-compliant elements.
        *   Log validation results to `project_journal.md`.
    *   **Input Format**: Code snippets, content blocks, data structures, validation rules/schemas.
    *   **Output Format**: `Validation Report` (JSON/markdown), boolean pass/fail.
    *   **Default `thinking_budget`**: Medium.
    *   **Inter-mode Dependencies**: Receives inputs from `CODER`, `SYNTHESIZER`, `ORCHESTRATOR`. Reports to `ORCHESTRATOR` and `DEBUGGER`.
    *   **Error Recovery Behavior**: If validation process itself fails (e.g., invalid schema), report `validation_tool_error` to `ORCHESTRATOR` and `DEBUGGER`. If content fails validation, report `compliance_failure` with details.

5.  **ROO-MODE-SYNTHESIZER**
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To integrate and synthesize diverse outputs from multiple agents into a coherent, unified, and high-quality final product or report.
    *   **Primary Directives**:
        *   Understand the structure and intent of inputs from various modes.
        *   Merge, rephrase, and format content for clarity and consistency.
        *   Ensure logical flow and narrative coherence.
        *   Prepare outputs for `HUMAN-INPUT` or final delivery.
        *   Invoke `isa_summarizer.py` if multiple files touched.
    *   **Input Format**: Reports, code snippets, research findings, validation results from other modes.
    *   **Output Format**: Consolidated markdown reports, structured documents, final product drafts.
    *   **Default `thinking_budget`**: Medium.
    *   **Inter-mode Dependencies**: Receives inputs from `RESEARCH`, `CODER`, `VALIDATOR`, `AUDITOR`, `BRAINSTORMER`. Reports to `ORCHESTRATOR` or `HUMAN-INPUT`.
    *   **Error Recovery Behavior**: If synthesis encounters conflicting information, report `synthesis_conflict` to `ORCHESTRATOR` and suggest `BRAINSTORMER` or `HUMAN-INPUT` for resolution.

6.  **ROO-MODE-ARCHITECT** (New Mode)
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To plan, design, and strategize solutions, breaking down complex problems, creating technical specifications, and designing system architecture.
    *   **Primary Directives**:
        *   Analyze requirements and define system components.
        *   Create detailed design documents, flowcharts, and diagrams (e.g., Mermaid).
        *   Identify dependencies, constraints, and potential architectural risks.
        *   Propose optimal solutions and technology choices.
        *   Suggest edits to `isa/context/governance.md`, `isa_manifest.yaml`, `ISA_Roo_Definitive_Architecture_v1.md`.
    *   **Input Format**: High-level task descriptions, problem statements, research findings.
    *   **Output Format**: Design documents (markdown), architectural diagrams, technical specifications, detailed plans.
    *   **Default `thinking_budget`**: High (for strategic planning).
    *   **Inter-mode Dependencies**: Receives tasks from `ORCHESTRATOR`. May invoke `RESEARCH` or `BRAINSTORMER`. Provides plans/specs to `CODER`, `VALIDATOR`, `AUDITOR`.
    *   **Error Recovery Behavior**: If design encounters unresolvable conflicts or ambiguities, report `design_impasse` to `ORCHESTRATOR` and suggest `HUMAN-INPUT` or `BRAINSTORMER`.

7.  **ROO-MODE-DEBUGGER** (New Mode)
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To troubleshoot issues, investigate errors, diagnose problems, and identify root causes within the system or generated outputs.
    *   **Primary Directives**:
        *   Analyze error messages, logs, and stack traces.
        *   Propose diagnostic steps and potential fixes.
        *   Systematically narrow down problem areas.
        *   Suggest logging additions or test cases for reproduction.
        *   Escalate to `isa_debugger` if uncertainty detected.
    *   **Input Format**: Error messages, log files, failed validation reports, code snippets, problem descriptions.
    *   **Output Format**: Root cause analysis, proposed solutions, diagnostic steps, updated code (via `CODER`).
    *   **Default `thinking_budget`**: High (for analytical problem-solving).
    *   **Inter-mode Dependencies**: Invoked by `ORCHESTRATOR` or any mode encountering an error. May interact with `CODER` (for fixes), `RESEARCH` (for external knowledge), `VALIDATOR` (to confirm fixes).
    *   **Error Recovery Behavior**: If debugging fails to identify a root cause after multiple attempts, report `unresolved_issue` to `ORCHESTRATOR` and suggest `HUMAN-INPUT`.

8.  **ROO-MODE-AUDITOR** (Refined Placeholder)
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To continuously scan project structure, code, and outputs for adherence to standards, identify technical debt, and monitor versioning consistency.
    *   **Primary Directives**:
        *   Perform automated checks against defined standards and policies.
        *   Identify deviations, security vulnerabilities, or performance bottlenecks.
        *   Track and report technical debt metrics.
        *   Ensure versioning integrity across components.
        *   Trigger snapshots and version bumps based on `CHANGELOG.md` milestones.
    *   **Input Format**: Project file system, code repositories, configuration files, `isa_manifest.yaml`.
    *   **Output Format**: `Audit Report` (structured JSON/markdown), list of issues, recommendations.
    *   **Default `thinking_budget`**: Medium.
    *   **Inter-mode Dependencies**: Invoked by `ORCHESTRATOR` periodically or after `CODER` actions. Reports to `ORCHESTRATOR`, `DEBUGGER`, `HUMAN-INPUT`.
    *   **Error Recovery Behavior**: If audit tools fail, report `audit_tool_failure` to `ORCHESTRATOR` and `DEBUGGER`. If non-compliance is found, report `audit_violation` with details.

9.  **ROO-MODE-BRAINSTORMER** (Refined Placeholder)
    *   **LLM Model**: Gemini 2.5 Flash
    *   **Mission**: To generate creative solutions, propose naming schemes, interface ideas, and overcome impasses through divergent thinking and goal alignment.
    *   **Primary Directives**:
        *   Generate multiple, diverse ideas for a given problem.
        *   Evaluate ideas against specified criteria.
        *   Facilitate creative problem-solving when other modes are stuck.
        *   Apply divergent and convergent thinking techniques.
    *   **Input Format**: Problem statements, impasses, design challenges, naming requests.
    *   **Output Format**: List of ideas, proposed solutions, creative concepts (markdown).
    *   **Default `thinking_budget`**: Medium.
    *   **Inter-mode Dependencies**: Invoked by `ORCHESTRATOR`, `ARCHITECT`, `DEBUGGER`, or `SYNTHESIZER` when creative input is needed. Outputs are consumed by the invoking mode.
    *   **Error Recovery Behavior**: If brainstorming fails to yield viable solutions, report `no_viable_ideas` to `ORCHESTRATOR` and suggest `HUMAN-INPUT`.

10. **ROO-MODE-HUMAN-INPUT**
    *   **LLM Model**: N/A
    *   **Mission**: To serve as a dedicated interface for awaiting and processing human input, ensuring contextual resumption of AI workflows.
    *   **Primary Directives**:
        *   Pause LangGraph execution and await human interaction.
        *   Receive and parse human approvals, clarifications, or direct injections.
        *   Provide necessary context to the human for informed decision-making.
        *   Resume workflow with updated context upon human input.
    *   **Input Format**: Human queries, approvals, instructions.
    *   **Output Format**: Contextualized prompts for human, parsed human input for `ORCHESTRATOR`.
    *   **Default `thinking_budget`**: N/A.
    *   **Inter-mode Dependencies**: Invoked by `ORCHESTRATOR` or any mode requiring human intervention. Reports back to `ORCHESTRATOR`.
    *   **Error Recovery Behavior**: If human input is unclear or invalid, prompt for re-clarification. If no input received within a timeout, report `human_timeout` to `ORCHESTRATOR`.

---

#### Deprecated/Redundant Modes:

*   **ROO-MODE-UI-CRITIC**: Deprecated as a core mode. While potentially useful, its specialized nature for UI analysis might not align with the core mission of "autonomous standards architecture" unless UI standards are a direct, primary focus. It can be re-introduced as a specialized extension or a tool within `CODER` or `VALIDATOR` if needed.

---

## Recommendations for Prompt Engineering Templates

Each mode should adhere to a structured prompt template, incorporating specific strategies to optimize performance and ensure predictable behavior.

1.  **ROO-MODE-ORCHESTRATOR**
    *   **Strategy**: Guided Planning, Task Decomposition, Fallback Logic.
    *   **Template Directives**:
        *   `task_intent`: [User's high-level goal]
        *   `expected_outcome`: [Desired final state/output]
        *   `output_type`: [e.g., JSON, markdown, file_path]
        *   `fallback_mode`: [e.g., debug, human-input]
        *   `current_context`: [Brief summary of ongoing work]
        *   `available_modes`: [List of modes with brief capabilities]
        *   `decomposition_rules`: [Guidelines for breaking down tasks]
        *   `mode_selection_criteria`: [Rules for choosing the next mode]
        *   `thinking_budget`: Low

2.  **ROO-MODE-RESEARCH**
    *   **Strategy**: CoT (Chain of Thought), Critical Synthesis, Information Extraction, Source Citation.
    *   **Template Directives**:
        *   `research_goal`: [Specific question or topic to research]
        *   `required_sources`: [e.g., web, internal_docs, specific_file]
        *   `output_format`: [e.g., structured_json, summary_markdown]
        *   `synthesis_directives`: [e.g., identify_conflicts, extract_key_facts, summarize_pros_cons]
        *   `thinking_budget`: High

3.  **ROO-MODE-CODER**
    *   **Strategy**: Self-Refine, Inline Test Cases, Code Generation from Spec, Error Handling.
    *   **Template Directives**:
        *   `coding_task`: [Specific code to write/modify/refactor]
        *   `design_spec`: [Relevant architectural/design details]
        *   `target_file`: [Path to file to modify/create]
        *   `existing_code_context`: [Relevant surrounding code for context]
        *   `coding_standards`: [Link to style guide or specific rules]
        *   `test_case_requirements`: [Instructions for inline tests]
        *   `thinking_budget`: Medium

4.  **ROO-MODE-VALIDATOR**
    *   **Strategy**: Deterministic Rule Application, Structured Reporting, Error Identification.
    *   **Template Directives**:
        *   `validation_target`: [Code, content, or data to validate]
        *   `validation_rules_schema`: [JSON schema, regex patterns, or explicit rules]
        *   `expected_output_format`: [e.g., boolean_pass_fail, detailed_report_json]
        *   `error_reporting_level`: [e.g., critical_only, all_issues]
        *   `thinking_budget`: Medium

5.  **ROO-MODE-SYNTHESIZER**
    *   **Strategy**: Coherence Building, Content Integration, Tone/Style Alignment, Summarization.
    *   **Template Directives**:
        *   `synthesis_goal`: [Purpose of the final product]
        *   `input_sources`: [List of inputs from other modes with their types]
        *   `desired_output_format`: [e.g., comprehensive_markdown_report, executive_summary]
        *   `integration_directives`: [e.g., merge_conflicting_data, rephrase_for_clarity, maintain_original_meaning]
        *   `thinking_budget`: Medium

6.  **ROO-MODE-ARCHITECT**
    *   **Strategy**: Guided Planning, Systems Thinking, Constraint-Based Design, Risk Assessment.
    *   **Template Directives**:
        *   `design_problem`: [High-level problem to solve]
        *   `system_scope`: [Boundaries of the design]
        *   `key_requirements`: [Functional and non-functional requirements]
        *   `constraints`: [Technical, budget, time constraints]
        *   `output_format`: [e.g., architectural_diagram_mermaid, design_doc_markdown]
        *   `thinking_budget`: High

7.  **ROO-MODE-DEBUGGER**
    *   **Strategy**: Root Cause Analysis, Hypothesis Testing, Step-by-Step Diagnosis, Solution Proposal.
    *   **Template Directives**:
        *   `error_description`: [Detailed description of the issue]
        *   `contextual_logs`: [Relevant log snippets, stack traces]
        *   `affected_components`: [Files, functions, modules involved]
        *   `diagnostic_steps_taken`: [Previous attempts to debug]
        *   `expected_behavior`: [What should happen]
        *   `thinking_budget`: High

8.  **ROO-MODE-AUDITOR**
    *   **Strategy**: Rule-Based Scanning, Compliance Reporting, Anomaly Detection.
    *   **Template Directives**:
        *   `audit_scope`: [e.g., entire_project, specific_module, recent_changes]
        *   `audit_criteria`: [Link to standards document, list of rules, security policies]
        *   `output_detail_level`: [e.g., summary, detailed_violations]
        *   `reporting_frequency`: [e.g., on_demand, daily, post_commit]
        *   `thinking_budget`: Medium

9.  **ROO-MODE-BRAINSTORMER**
    *   **Strategy**: Divergent Thinking, Convergent Selection, Idea Generation, Constraint Relaxation.
    *   **Template Directives**:
        *   `brainstorm_topic`: [Problem or concept for ideation]
        *   `desired_output_type`: [e.g., naming_suggestions, interface_ideas, creative_solutions]
        *   `constraints_to_consider`: [Any specific limitations or requirements]
        *   `number_of_ideas_min`: [Minimum number of ideas to generate]
        *   `thinking_budget`: Medium

10. **ROO-MODE-HUMAN-INPUT**
    *   **Strategy**: Contextual Questioning, Clear Call-to-Action, Input Parsing.
    *   **Template Directives**:
        *   `question_for_human`: [Clear, concise question]
        *   `context_for_human`: [Relevant information for decision-making]
        *   `expected_human_response_format`: [e.g., yes_no, text_input, selection_from_list]
        *   `follow_up_suggestions`: [2-4 suggested answers for the user]
        *   `thinking_budget`: N/A

---

## Mode Interoperability Graph

```mermaid
graph TD
    subgraph Core Orchestration
        ORCHESTRATOR[ROO-MODE-ORCHESTRATOR]
    end

    subgraph Knowledge & Planning
        RESEARCH[ROO-MODE-RESEARCH]
        ARCHITECT[ROO-MODE-ARCHITECT]
        BRAINSTORMER[ROO-MODE-BRAINSTORMER]
    end

    subgraph Execution & Quality
        CODER[ROO-MODE-CODER]
        VALIDATOR[ROO-MODE-VALIDATOR]
        AUDITOR[ROO-MODE-AUDITOR]
        DEBUGGER[ROO-MODE-DEBUGGER]
    end

    subgraph Output & Interaction
        SYNTHESIZER[ROO-MODE-SYNTHESIZER]
        HUMAN_INPUT[ROO-MODE-HUMAN-INPUT]
    end

    ORCHESTRATOR --> ARCHITECT: Decompose & Plan
    ORCHESTRATOR --> RESEARCH: Research Needs
    ORCHESTRATOR --> CODER: Code Tasks
    ORCHESTRATOR --> VALIDATOR: Validate Outputs
    ORCHESTRATOR --> SYNTHESIZER: Final Product Assembly
    ORCHESTRATOR --> AUDITOR: Audit Requests
    ORCHESTRATOR --> DEBUGGER: Error Escalation
    ORCHESTRATOR --> HUMAN_INPUT: Human Intervention

    ARCHITECT --> CODER: Design Specs
    ARCHITECT --> RESEARCH: Design Research
    ARCHITECT --> BRAINSTORMER: Ideation Needs

    RESEARCH --> ARCHITECT: Insights
    RESEARCH --> CODER: Context
    RESEARCH --> VALIDATOR: Reference Data
    RESEARCH --> AUDITOR: Standards Info
    RESEARCH --> DEBUGGER: Knowledge Base

    CODER --> VALIDATOR: Code for Validation
    CODER --> DEBUGGER: Errors/Issues

    VALIDATOR --> ORCHESTRATOR: Validation Report
    VALIDATOR --> DEBUGGER: Validation Failures

    AUDITOR --> ORCHESTRATOR: Audit Report
    AUDITOR --> DEBUGGER: Identified Issues
    AUDITOR --> SYNTHESIZER: Summary for Reports

    DEBUGGER --> ORCHESTRATOR: Debug Status
    DEBUGGER --> CODER: Proposed Fixes
    DEBUGGER --> HUMAN_INPUT: Unresolved Issues

    BRAINSTORMER --> ARCHITECT: Creative Ideas
    BRAINSTORMER --> ORCHESTRATOR: Solutions for Impasses

    SYNTHESIZER --> ORCHESTRATOR: Final Output
    SYNTHESIZER --> HUMAN_INPUT: Review/Approval

    HUMAN_INPUT --> ORCHESTRATOR: Decisions/Clarifications

    style ORCHESTRATOR fill:#f9f,stroke:#333,stroke-width:2px
    style RESEARCH fill:#ccf,stroke:#333,stroke-width:2px
    style CODER fill:#cfc,stroke:#333,stroke-width:2px
    style VALIDATOR fill:#ffc,stroke:#333,stroke-width:2px
    style SYNTHESIZER fill:#fcf,stroke:#333,stroke-width:2px
    style ARCHITECT fill:#cff,stroke:#333,stroke-width:2px
    style DEBUGGER fill:#fcc,stroke:#333,stroke-width:2px
    style AUDITOR fill:#e6e6fa,stroke:#333,stroke-width:2px
    style BRAINSTORMER fill:#ffe0b2,stroke:#333,stroke-width:2px
    style HUMAN_INPUT fill:#d3d3d3,stroke:#333,stroke-width:2px