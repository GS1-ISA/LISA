# Plan to Resolve TypeScript Errors and Verify Dependency Update

**Problem Statement:** The `npm test` command failed due to TypeScript parsing errors, specifically related to HTML entities (`<`, `>`, `&gt;`) being present in the code where actual `<` and `>` characters are expected. Additionally, there's a typo (`reportDraphafter` instead of `reportDrafter`) in `src/ai/agents/proposal_review_workflow.ts`. The overall goal is to ensure the dependency update for `@tanstack-query-firebase/react` and `@tanstack/react-query` has not introduced regressions.

**Proposed Solution Steps:**

1.  **Analyze and Confirm Character Encoding Issue:**
    *   **Action:** Re-read `src/ai/tools/agentic_workflows/proposal_review_tools.ts` to confirm the exact character encoding (e.g., `<`, `>`, `&lt;`, `&gt;`).
    *   **Expected Outcome:** Identify the precise HTML entities causing the parsing errors.

2.  **Correct Character Encoding in `proposal_review_tools.ts`:**
    *   **Action:** Use `write_to_file` to overwrite the entire content of `src/ai/tools/agentic_workflows/proposal_review_tools.ts`. The new content will have all instances of `<`, `>`, `&lt;`, and `&gt;` replaced with their correct characters (`<`, `>`). This is a more robust approach to ensure the characters are correctly written, bypassing potential issues with `apply_diff` or `search_and_replace` when dealing with subtle encoding discrepancies.
    *   **Expected Outcome:** The `proposal_review_tools.ts` file will be syntactically correct with proper generic type annotations.

3.  **Correct Typo in `proposal_review_workflow.ts`:**
    *   **Action:** Use `apply_diff` to replace `reportDraphafter` with `reportDrafter` in `src/ai/agents/proposal_review_workflow.ts`.
    *   **Expected Outcome:** The typo will be corrected, resolving the `Cannot find name 'reportDraphafter'` error.

4.  **Re-run Test Suite:**
    *   **Action:** Execute `npm test` to verify that all TypeScript errors are resolved and that the application's functionalities are working as expected after the dependency update.
    *   **Expected Outcome:** The test suite runs successfully, indicating no regressions.

**Mermaid Diagram of the Plan:**

```mermaid
graph TD
    A[Start: npm test failed] --> B{Analyze Errors};
    B --> C{Identify Character Encoding Issues in proposal_review_tools.ts};
    C --> D[Correct Character Encoding using write_to_file];
    D --> E{Identify Typo in proposal_review_workflow.ts};
    E --> F[Correct Typo using apply_diff];
    F --> G[Re-run npm test];
    G --> H{Tests Pass?};
    H -- Yes --> I[Task Completed];
    H -- No --> J[Debug Further];