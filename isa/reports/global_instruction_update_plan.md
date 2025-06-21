### Review and Refine Global Instructions Plan

**Objective:** Review and refine the global custom instructions in `isa/prompts/unified_autopilot.json` to ensure accuracy, completeness, and effectiveness, and apply any necessary refinements or updates.

**Current Status:** The content of `isa/prompts/unified_autopilot.json` has been read and reviewed.

**Identified Improvement:**
A minor clarification is needed in **Section 7: Path Discipline** to explicitly include `project_journal.md` as a preferred location under `isa/logs/`. This ensures consistency with instructions 10 and 16, which refer to logging validator results and rollback reasons in `project_journal.md`.

**Proposed Change:**

```json
{
  "global_instructions": "# Custom Instructions for All Modes (Unified ISA Roo Configuration)\\n\\n...\\n\\n## 🧠 Conventions, Registrations, and Policies\\n\\n...\\n\\n7. **Path Discipline**\\n   - Do not write to root unless explicitly instructed.\\n   - Preferred locations:\\n     - `isa/context/`\\n     - `isa/config/`\\n     - `isa/prompts/`\\n     - `isa/reports/`\\n     - `isa/logs/` (including `project_journal.md`)\\n     - `isa/versions/`\\n\\n...\\n"
}
```

**Summary of Review and Refinement Process:**
The global custom instructions in `isa/prompts/unified_autopilot.json` were thoroughly reviewed. The existing instructions are robust and cover critical aspects of agent behavior, quality assurance, and system health. The only identified area for improvement was a minor clarification regarding the explicit placement of `project_journal.md` within the `isa/logs/` directory, which enhances clarity and consistency across the instruction set.

**Workflow Diagram:**

```mermaid
graph TD
    A[Start Task: Review Global Instructions] --> B{Read isa/prompts/unified_autopilot.json};
    B --> C[Review Instructions for Accuracy & Completeness];
    C --> D{Identify Areas for Improvement?};
    D -- Yes --> E[Propose Specific Changes (e.g., Path Discipline Clarification)];
    E --> F[Present Plan to User for Approval];
    F -- User Approves --> G{Write Plan to Markdown File?};
    G -- Yes --> H[Write Plan to isa/reports/global_instruction_update_plan.md];
    G -- No --> I[Proceed to Implementation];
    H --> I;
    I --> J[Switch Mode to Code];
    J --> K[Implement Changes in Code Mode];
    K --> L[Document Changes in CHANGELOG.md, agent_task_history.json, version_tracker.json];
    L --> M[Run isa_validator.py];
    M --> N[Report Outcome with attempt_completion];
    D -- No --> N;