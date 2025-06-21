# Consolidated Report: Pending M0.1 Prompts and UDM Section 04 Mode Definitions

## Introduction

This document consolidates the intended content for pending M0.1 tasks related to Roo Mode prompts and their definitions in UDM Section `04-RooModes.md`. Due to persistent difficulties with file system tools (`create_file_with_block`, `overwrite_file_with_block`, and `replace_with_git_merge_diff`) when attempting to save or modify these files, this report serves as a centralized definition of the required content. This content should be manually reviewed and applied to the respective files in the `prompts/` directory and `docs/udm/04-RooModes.md`.

---

## 1. ROO-MODE-RESEARCH (Covers TASK-P0-M0.1-T030 UDM update & TASK-P0-M0.1-T018)

**Note:** The following UDM 04 definition for `ROO-MODE-RESEARCH` was intended to be applied as part of TASK-P0-M0.1-T030. It also incorporates the requirements of TASK-P0-M0.1-T018 (inclusion of `Context7DocumentationTool`). The prompt file `prompts/roo_mode_research_prompt_v1.3.prompt.txt` was successfully saved during T030.

**Target UDM 04 Definition (`docs/udm/04-RooModes.md`):**
```markdown
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
```

---

## 2. TASK-P0-M0.1-T013: ROO-MODE-ANALYZE-DOCS

**Target Prompt File Path:** `prompts/roo_mode_analyze_docs_prompt_v1.0.prompt.txt`

**Placeholder Prompt Content:**
```markdown
# ROO-MODE-ANALYZE-DOCS Prompt v1.0
# Task ID: TASK-P0-M0.1-T013
# Purpose: To analyze documentation files, compare against UDM structure, identify content for migration, and pinpoint UDM content gaps.
# Key Tools: FileSystemAccessTool, DocumentFetchingParsingTool (if URLs are involved), UDMQueryTool.

[Placeholder for detailed co-designed prompt logic for analyzing document structures, content, and cross-referencing with UDM definitions...]
```

**Target UDM 04 Definition (`docs/udm/04-RooModes.md`):**
```markdown
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
```

---

## 3. TASK-P0-M0.1-T014: ROO-MODE-ANALYZE-CODEBASE

**Target Prompt File Path:** `prompts/roo_mode_analyze_codebase_prompt_v1.0.prompt.txt`

**Placeholder Prompt Content:**
```markdown
# ROO-MODE-ANALYZE-CODEBASE Prompt v1.0
# Task ID: TASK-P0-M0.1-T014
# Purpose: To perform an automated scan and analysis of source code, identify languages, frameworks, structure, and map to UDM conceptual components.
# Key Tools: FileSystemAccessTool, CodeParsingTool (conceptual), UDMQueryTool.

[Placeholder for detailed co-designed prompt logic...]
```

**Target UDM 04 Definition (`docs/udm/04-RooModes.md`):**
```markdown
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
```

---

## 4. TASK-P0-M0.1-T015: ClaudeBrowserMode

**Target Prompt File Path:** `prompts/claude_browser_mode_prompt_v2.0.prompt.txt`

**Placeholder Prompt Content:**
```markdown
# ClaudeBrowserMode Prompt v2.0
# Task ID: TASK-P0-M0.1-T015
# Purpose: To interact with web pages, fetch content (especially from dynamic sites or SPAs), and perform browser-based actions using a suite of sub-action tools, when delegated by other Roo Modes like ROO-MODE-RESEARCH.
# Key Tools/Capabilities: BrowserNavTool, BrowserClickTool, BrowserScrollTool, BrowserReadPageTool, BrowserTypeListTool, BrowserSearchPageTool, BrowserExtractContentTool, BrowserCloseSessionTool.

[Placeholder for detailed co-designed prompt logic, including how to interpret inputs from other Roo modes, plan browsing sequences, manage state, and return structured output...]
```

**Target UDM 04 Definition (`docs/udm/04-RooModes.md`):**
```markdown
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
```

---

## 5. TASK-P0-M0.1-T020: ROO-MODE-PLAN-STRATEGIC

**Target Prompt File Path:** `prompts/roo_mode_plan_strategic_prompt_v1.0.prompt.txt`

**Placeholder Prompt Content:**
```markdown
# ROO-MODE-PLAN-STRATEGIC Prompt v1.0
# Task ID: TASK-P0-M0.1-T020
# Purpose: To synthesize audit findings, knowledge gaps, and strategic goals to formulate or update ISA's development roadmap and high-level plans.
# Key Tools: UDMQueryTool, TaskManagementTool (conceptual).

[Placeholder for detailed co-designed prompt logic...]
```

**Target UDM 04 Definition (`docs/udm/04-RooModes.md`):**
```markdown
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
```

---

## 6. TASK-P0-M0.1-T021: ROO-MODE-UPDATE-UDM-TECHNICAL

**Target Prompt File Path:** `prompts/roo_mode_update_udm_technical_prompt_v1.1.prompt.txt`

**Placeholder Prompt Content:**
```markdown
# ROO-MODE-UPDATE-UDM-TECHNICAL Prompt v1.1
# Task ID: TASK-P0-M0.1-T021
# Purpose: To make precise, technically-focused updates to UDM documents, such as changing prompt references, tool lists, or model dependencies for Roo Modes.
# Key Tools: FileSystemAccessTool (for UDM files), UDMQueryTool, TextEditorTool (conceptual).

[Placeholder for detailed co-designed prompt logic for parsing UDM, finding specific sections, and applying changes based on input directives...]
```

**Target UDM 04 Definition (`docs/udm/04-RooModes.md`):**
```markdown
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
```

---

## 7. TASK-P0-M0.1-T022 & T023: ROO-MODE-GENERATE-DOCUMENTATION

**Target Prompt File Path (for T023):** `prompts/roo_mode_generate_documentation_prompt_v1.0.prompt.txt`

**Placeholder Prompt Content (for T023):**
```markdown
# ROO-MODE-GENERATE-DOCUMENTATION Prompt v1.0
# Task ID: TASK-P0-M0.1-T023
# Purpose: To generate comprehensive documentation for UDM sections, Roo Modes, tools, or architectural components based on available information and context.
# Key Tools: UDMQueryTool, FileSystemAccessTool (to read related docs).

[Placeholder for detailed co-designed prompt logic for synthesizing information and structuring it into coherent documentation...]
```

**Target UDM 04 Definition (for T022) (`docs/udm/04-RooModes.md`):**
```markdown
### 4.T Mode: ROO-MODE-GENERATE-DOCUMENTATION
- **ID:** `RM-GD01` (As specified in T022)
- **Description:** Generates textual content for UDM sections, including descriptions of Roo Modes, system components, tools, or operational procedures. It synthesizes information from various sources like master prompts, existing UDM content, and research findings.
- **CorePromptReference:** `prompts/roo_mode_generate_documentation_prompt_v1.0.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `UDMQueryTool` (to access context from other UDM sections)
    - `FileSystemAccessTool` (to read source material if provided as files)
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5
- **Input:** Topic to document, source information references, target UDM section, formatting guidelines.
- **Output:** Generated Markdown content for the specified UDM section.
- **ImplementationNotes:** To be implemented as a Genkit flow.
```

---

## 8. TASK-P0-M0.1-T024 & T025: ROO-MODE-VALIDATE-COMPLETION

**Target Prompt File Path (for T025):** `prompts/roo_mode_validate_completion_prompt_v1.0.prompt.txt`

**Placeholder Prompt Content (for T025):**
```markdown
# ROO-MODE-VALIDATE-COMPLETION Prompt v1.0
# Task ID: TASK-P0-M0.1-T025
# Purpose: To validate the completion of tasks, milestones, or phases by checking their exit criteria, expected outputs, and log files against UDM definitions.
# Key Tools: UDMQueryTool, FileSystemAccessTool (to read logs and outputs).

[Placeholder for detailed co-designed prompt logic for cross-referencing UDM, task logs, and output files to validate completion criteria...]
```

**Target UDM 04 Definition (for T024) (`docs/udm/04-RooModes.md`):**
```markdown
### 4.U Mode: ROO-MODE-VALIDATE-COMPLETION
- **ID:** `RM-VC01` (As specified in T024)
- **Description:** Validates the completion of tasks, milestones, or phases. It checks if all defined objectives, expected outputs, and exit criteria (as specified in UDM Section 05 or individual task definitions) have been met by reviewing task logs, output files, and current UDM state.
- **CorePromptReference:** `prompts/roo_mode_validate_completion_prompt_v1.0.prompt.txt`
- **KeyToolsAndCapabilities:**
    - `UDMQueryTool` (to access roadmap, task definitions, exit criteria)
    - `FileSystemAccessTool` (to read task logs, output files, and `blueprint_state.json`)
- **AI_Model_Dependency:** Gemini 2.5 Flash Preview 20-5
- **Input:** Target task/milestone/phase ID to validate, UDM roadmap reference, paths to relevant logs and output files.
- **Output:** Validation report (JSON or Markdown), updated status in UDM Section 05 and `blueprint_state.json` if validation is successful.
- **ImplementationNotes:** To be implemented as a Genkit flow.
```

---
**End of Report**
