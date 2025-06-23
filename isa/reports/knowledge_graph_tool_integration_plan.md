# Plan: Integrate `queryKnowledgeGraphTool` into ISA System

**Task Intent:** Integrate the `queryKnowledgeGraphTool` into the ISA system, allowing AI flows to query the Neo4j Knowledge Graph.

**Expected Outcome:** A new tool function is implemented in `src/ai/tools/` that can connect to Neo4j and execute Cypher queries based on natural language input, returning structured results. This tool will then be made available for use by AI flows.

**Output Type:** Confirmation of successful implementation and integration of the `queryKnowledgeGraphTool`.

**Fallback Mode:** debug

## Detailed Plan:

1.  **Re-read Current File Contents:** Re-read `src/ai/tools/knowledge-graph-tools.ts` and `src/ai/genkit.ts` to get their absolute latest content, ensuring no discrepancies.
2.  **Correct `knowledge-graph-tools.ts`:**
    *   Remove the problematic `import { defineTool } from 'genkit';` or `import { defineTool } from 'genkit/core';` line.
    *   Ensure that `defineTool` is called as `ai.defineTool` within the file, as observed in other tool definitions.
3.  **Correct `genkit.ts`:**
    *   Remove the `tools` array from the `genkit({...})` configuration object, as the error message indicates this property does not exist.
    *   Add a `genkit.addTool(queryKnowledgeGraphTool);` call *after* the `genkit({...})` initialization to correctly register the tool.
4.  **Update Logging and Versioning:** Update `CHANGELOG.md`, `isa/logs/agent_task_history.json`, and `isa/versions/version_tracker.json` to reflect the successful implementation and integration of the `queryKnowledgeGraphTool`.

## Mermaid Diagram for the Plan:

```mermaid
graph TD
    A[Start Task: Integrate queryKnowledgeGraphTool] --> B{Read src/ai/tools/knowledge-graph-tools.ts & src/ai/genkit.ts};
    B --> C{Analyze current file content and errors};
    C --> D{Modify src/ai/tools/knowledge-graph-tools.ts};
    D --> D1[Remove defineTool import];
    D --> D2[Ensure ai.defineTool is used];
    C --> E{Modify src/ai/genkit.ts};
    E --> E1[Remove 'tools' array from genkit config];
    E --> E2[Add genkit.addTool(queryKnowledgeGraphTool) after genkit init];
    D & E --> F{Apply Changes};
    F --> G{Check for new errors};
    G -- No Errors --> H[Update CHANGELOG.md];
    H --> I[Update isa/logs/agent_task_history.json];
    I --> J[Update isa/versions/version_tracker.json];
    J --> K[Confirm successful implementation];
    K --> L[Switch to Code Mode for implementation];
    G -- Errors --> C;