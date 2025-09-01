# Project Roadmap & Future Plans

This document outlines future improvements and tasks identified during project audits and development.

## Audit Findings - Remaining Recommendations

### 1. Implement `tokens.css` Generation
*   **Description:** The `tokens.css` file is currently empty, resolving a 404 error, but it is intended to contain design tokens (e.g., from Figma). A process needs to be established to generate and populate this file with actual styling information.
*   **Priority:** Medium
*   **Details:** This task requires investigation into the project's design system workflow and integration with tools that can export design tokens to CSS.

### 2. Research and Integrate Best Practices for Python Subprocess Management
*   **Description:** While immediate Python path issues for `subprocess.run` calls have been addressed, a broader review of best practices for managing Python subprocesses (including `PYTHONPATH`, environment variables, and error handling) is recommended. This ensures long-term robustness and maintainability.
*   **Priority:** Medium
*   **Details:** This involves researching industry best practices, potentially exploring alternative subprocess management techniques, and updating relevant project documentation (e.g., `GEMINI.md`, `development_practices.md`).

### 3. General Review and Refactoring of `subprocess.run` Calls
*   **Description:** An ongoing task to continuously review any new or existing `subprocess.run` calls within the codebase. The goal is to ensure they adhere to best practices, handle `PYTHONPATH` and other environment variables correctly, and consider alternatives where direct Python function calls are more appropriate and efficient.
*   **Priority:** Ongoing / Low (for new instances)
*   **Details:** This is a continuous code quality effort that should be integrated into development workflows and code reviews.
