
# Agentic System: Autonomous Research Agent

**Owner**: `eng-lead`
**Status**: Implemented

## Overview

The Autonomous Research Agent is a multi-agent system designed to conduct research on a given topic, synthesize findings, and produce a structured, cited report. It is a core component of the project's strategy to automate knowledge gathering and analysis, directly supporting the goals of `Track R - Knowledge Gaps & Ecosystem Research`.

The system is designed as a "crew" of specialized agents that collaborate in a sequential workflow, orchestrated by a central graph.

## Architecture

The research process is managed by the `ResearchGraph` orchestrator (`src/orchestrator/research_graph.py`) and involves three distinct agents:

1.  **`PlannerAgent`**: 
    -   **Role**: To take a high-level user query and decompose it into a structured plan of specific, actionable research questions.
    -   **Source**: `src/agent_core/agents/planner.py`

2.  **`ResearcherAgent`**:
    -   **Role**: To execute each task from the research plan. It uses the `WebResearchTool` to browse the web, reads relevant pages, and uses a self-correction mechanism to evaluate content before storing it in the `RAGMemory`.
    -   **Source**: `src/agent_core/agents/researcher.py`

3.  **`SynthesizerAgent`**:
    -   **Role**: To take the complete set of information gathered in the `RAGMemory` and generate a final, coherent Markdown report, complete with citations.
    -   **Source**: `src/agent_core/agents/synthesizer.py`

### Supporting Components

-   **WebResearchTool**: A tool for searching the web and reading page content. Includes caching to prevent redundant requests. (`src/tools/web_research.py`)
-   **RAGMemory**: A persistent vector store using ChromaDB that serves as the agent crew's collective memory. (`src/agent_core/memory/rag_store.py`)

## How to Use

The research system is operated via `make` commands.

### Running a Research Task

Run the full multi-agent research crew via make or directly with Python:

```bash
# via make (writes to agent/outcomes/research_report.md)
make research-run query="Your Research Topic"

# or directly (prints to stdout)
python run_research_crew.py --query "Your Research Topic"
```

Environment notes:
- Docs provider integration is disabled by default; set `CONTEXT7_ENABLED=1` and provide `CONTEXT7_PROJECT`/`CONTEXT7_KEY` to enable.

### Evaluating a Research Report

After a report has been generated, you can evaluate its quality:

```bash
make research-eval query="Your Research Topic"
```

This command will:
1.  Invoke the `scripts/evaluate_research.py` script.
2.  Perform structural, citation, and simulated relevance checks.
3.  Print a JSON summary of the quality score and save it to `agent/outcomes/research_quality_report.json`.

## Integration with Project

-   **Roadmap**: This system directly contributes to `Track R`.
-   **TODO**: The implementation tasks are tracked in `docs/TODO.md` under section `01) Autonomous Research Agent Implementation`.
-   **Agentic Architecture**: This system is a reference implementation of the multi-agent collaboration principles outlined in `docs/AGENTIC_ARCHITECTURE.md`.
