# Mode Failure Simulation Plan

This document outlines blueprints for simulating various failure scenarios within the Roocode multi-agent system to test its resilience and error recovery mechanisms.

## 1. Memory Sync Mode Write Failure

**Scenario:** Simulate a failure where `Memory Sync Mode` is unable to write data to the long-term memory bank (e.g., due to network issues, database connection loss, or permission errors).

**Blueprint:**
1.  **Precondition:** `Memory Sync Mode` is active and attempting to persist session state or embeddings.
2.  **Simulation:** Introduce a controlled error that prevents `Memory Sync Mode` from successfully completing a write operation to its designated storage (e.g., temporarily revoke write permissions to the target directory/database, or simulate a network timeout).
3.  **Expected Outcome:**
    *   `Memory Sync Mode` detects the write failure.
    *   It attempts a predefined number of retries (e.g., 3 retries with exponential backoff).
    *   If retries fail, `Memory Sync Mode` logs the detailed error (e.g., "Permission Denied", "Database Connection Lost") and reports the failure to the `ORCHESTRATOR`.
    *   `ORCHESTRATOR` receives the error report, logs it, and based on severity:
        *   If critical, escalates to `DEBUGGER` for root cause analysis.
        *   If persistent, alerts `HUMAN-INPUT` for manual intervention.
        *   Potentially triggers a system-wide "degraded mode" or pauses memory synchronization until the issue is resolved.
4.  **Validation:** Verify that the error is correctly logged, reported to `ORCHESTRATOR`, and appropriate escalation/fallback actions are initiated.

## 2. CODER Mode Heartbeat Loss

**Scenario:** Simulate a `CODER` mode becoming unresponsive or crashing mid-task, leading to a loss of its "heartbeat" signal.

**Blueprint:**
1.  **Precondition:** `CODER` mode is actively executing a task (e.g., generating code, applying diffs).
2.  **Simulation:** Introduce a controlled event that causes `CODER` mode to stop responding or terminate unexpectedly (e.g., force-kill its process, introduce an infinite loop that prevents it from reporting status).
3.  **Expected Outcome:**
    *   `AUDITOR` (in its Guardian role) continuously monitors agent heartbeats.
    *   `AUDITOR` detects the absence of `CODER`'s heartbeat within a predefined timeout period.
    *   `AUDITOR` immediately notifies the `ORCHESTRATOR` of the unresponsive `CODER` instance.
    *   `ORCHESTRATOR` receives the alert and initiates recovery:
        *   Attempts to gracefully terminate and restart the `CODER` process.
        *   If restart fails or the issue persists, re-assigns the interrupted task to a new `CODER` instance or escalates to `DEBUGGER` for diagnosis.
        *   Logs the incident in `agent_task_history.json` and `project_journal.md`.
4.  **Validation:** Verify that `AUDITOR` correctly detects the heartbeat loss, `ORCHESTRATOR` is notified, and appropriate recovery actions (restart, re-assignment, escalation) are attempted.

## 3. RESEARCH Mode Claude API Failure Triggering Fallback to Gemini

**Scenario:** Simulate `RESEARCH` mode (primarily using Claude 3.5 Sonnet) encountering a persistent API error or rate limit, requiring a fallback to Gemini 2.5 Flash for continued operation.

**Blueprint:**
1.  **Precondition:** `RESEARCH` mode is attempting to use Claude 3.5 Sonnet for a research query.
2.  **Simulation:** Introduce a controlled error that causes Claude API calls to fail (e.g., invalid API key, simulated rate limit, network error).
3.  **Expected Outcome:**
    *   `RESEARCH` mode attempts the Claude API call.
    *   Upon failure, `RESEARCH` mode attempts a predefined number of retries.
    *   If retries fail, `RESEARCH` mode reports the persistent Claude API failure to the `ORCHESTRATOR` (or `TRIGGER` mode, if implemented).
    *   `ORCHESTRATOR` (or `TRIGGER` mode) detects the Claude failure and, based on a pre-configured policy, dynamically re-routes the research task to a `RESEARCH` instance (or a new `RESEARCH` sub-task) configured to use Gemini 2.5 Flash.
    *   `RESEARCH` (Gemini-backed) attempts to complete the task using its capabilities.
    *   The incident is logged, and if the Claude issue persists, `HUMAN-INPUT` is alerted.
4.  **Validation:** Verify that Claude API failures are detected, retries are attempted, the fallback mechanism to Gemini is triggered, and the task is re-attempted with the fallback model. Ensure proper logging of the model switch.