## Validation Automation Plan

This plan outlines a routine for continuously integrating the `isa/isa_validator.py` script to proactively identify and address system inconsistencies. It covers execution frequency, triggering mechanisms, logging, and reporting.

### 1. Purpose of `isa/isa_validator.py`

The `isa/isa_validator.py` script is designed to ensure the integrity and consistency of the ISA project's runtime environment. Specifically, it performs the following checks:

*   **Virtual Environment Activation:** Verifies that a Python virtual environment (`.venv`) is active and that `sys.prefix` correctly points to it.
*   **`.env` File Presence:** Confirms the existence of the `.env` file, which is crucial for loading environment variables.
*   **`python-dotenv` Installation:** Checks if the `python-dotenv` library is installed, as it's necessary for loading environment variables from the `.env` file.

Any issues detected are logged to `isa/logs/venv_issues.log`, and a summary is printed to standard output.

### 2. Current Logging Format in `project_journal.md`

The `project_journal.md` file currently captures the standard output of the `isa/isa_validator.py` script, providing a concise record of validation runs. An example of a successful run's log entry is:

```markdown
Running ISA Validator...
INFO: Virtual environment active: /Users/frisowempe/Desktop/isa_workspace/.venv
INFO: .env file found at .env.
INFO: python-dotenv is installed.
INFO: Environment validation successful.
ISA Validator completed successfully.
```

To enhance traceability, future entries will include a timestamp and a clear indication of the validation outcome.

### 3. Routine for Automated Execution

To establish continuous integration of validation, `isa/isa_validator.py` will be executed at key points in the development lifecycle.

#### 3.1. Frequency of Execution

*   **On Every Commit (Pre-commit Hook):** This provides immediate feedback to developers, preventing environment-related issues from being committed to the codebase.
*   **Before Major Deployments:** Ensures the target deployment environment meets the necessary prerequisites.
*   **Nightly Builds (CI/CD Pipeline):** Serves as a regular health check for the development and integration environments, catching any configuration drift.

#### 3.2. Trigger Mechanisms

##### a. Git Pre-commit Hook (Local Development)

A pre-commit hook will be configured to run the validator before allowing a commit. If the validation fails, the commit will be aborted, prompting the developer to resolve the issues.

**Example `.git/hooks/pre-commit` (create if it doesn't exist and make executable):**

```bash
#!/bin/bash

echo "Running ISA Environment Validator..."
python isa/isa_validator.py

if [ $? -ne 0 ]; then
    echo "ISA Environment Validation failed. Please fix the issues before committing."
    exit 1
fi

echo "ISA Environment Validation passed."
exit 0
```

##### b. CI/CD Pipeline (e.g., GitHub Actions, GitLab CI)

The validator will be integrated into the project's CI/CD pipeline as a mandatory step. This ensures that all code merged into main branches or deployed passes environment validation.

**Example GitHub Actions Workflow (`.github/workflows/validate.yml`):**

```yaml
name: ISA Environment Validation

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop

jobs:
  validate-environment:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x' # Specify your Python version

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install python-dotenv

    - name: Create dummy .env for CI (if not present)
      run: |
        touch .env # Create an empty .env file if it doesn't exist for the validator to pass
      continue-on-error: true # Allow this step to fail if .env already exists

    - name: Run ISA Environment Validator
      run: python isa/isa_validator.py
```

##### c. Scheduled Cron Job (Staging/Production Environments)

For environments where a CI/CD pipeline might not be the primary trigger (e.g., long-running staging servers), a cron job can be set up for nightly validation.

**Example Cron Entry (run `crontab -e`):**

```cron
0 3 * * * /usr/bin/python3 /Users/frisowempe/Desktop/isa_workspace/isa/isa_validator.py >> /Users/frisowempe/Desktop/isa_workspace/project_journal.md 2>&1
```

*Note: Adjust paths (`/usr/bin/python3`, `/Users/frisowempe/Desktop/isa_workspace/`) as per the specific server configuration.*

#### 3.3. Output Capture and Logging in `project_journal.md`

To ensure `project_journal.md` provides a comprehensive and timestamped record, the output of `isa/isa_validator.py` will be appended with a clear header.

**Proposed Logging Mechanism:**

Instead of directly redirecting the script's output, a wrapper script or CI/CD step will capture the output and format it before appending to `project_journal.md`.

**Example (Bash script to be called by CI/CD or cron):**

```bash
#!/bin/bash

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
VALIDATOR_OUTPUT=$(python isa/isa_validator.py 2>&1)
VALIDATION_STATUS=$?

echo "---" >> project_journal.md
echo "### ISA Environment Validation Report - $TIMESTAMP" >> project_journal.md
echo "" >> project_journal.md
echo "\`\`\`" >> project_journal.md
echo "$VALIDATOR_OUTPUT" >> project_journal.md
echo "\`\`\`" >> project_journal.md

if [ $VALIDATION_STATUS -eq 0 ]; then
    echo "**Status: ✅ SUCCESS**" >> project_journal.md
else
    echo "**Status: ❌ FAILED**" >> project_journal.md
    echo "Detailed issues: See isa/logs/venv_issues.log" >> project_journal.md
fi
echo "" >> project_journal.md

exit $VALIDATION_STATUS
```

This script ensures:
*   A clear markdown header with a timestamp.
*   The full output of the validator is captured.
*   A prominent status (SUCCESS/FAILED) is added.
*   A reference to `isa/logs/venv_issues.log` is provided for failures.

#### 3.4. Mechanisms for Alerting or Reporting Validation Failures

*   **CI/CD Pipeline Failure:** The most direct alert. If the `isa/isa_validator.py` script (or its wrapper) exits with a non-zero status code, the CI/CD job will fail, triggering standard notifications (email, Slack, GitHub Checks).
*   **Git Pre-commit Hook:** Blocks the commit, providing immediate feedback to the developer.
*   **Dashboard Integration (`status_dashboard.md`):** As per global instruction 18, the outcome of validation runs should be reflected in `isa/reports/status_dashboard.md`. A separate process (e.g., a CI/CD step or a post-cron script) can parse `project_journal.md` or `isa/logs/venv_issues.log` to update the dashboard.
*   **Monitoring `isa/logs/venv_issues.log`:** For critical environments, monitoring tools can be configured to alert on new entries or specific error patterns in `isa/logs/venv_issues.log`.

### 4. Validation Workflow Diagram

```mermaid
graph TD
    A[Developer Commits Code] --> B{Git Pre-commit Hook};
    B -- Success --> C[Code Pushed to Repository];
    B -- Failure --> D[Commit Rejected - Developer Fixes];
    C --> E[CI/CD Pipeline Triggered];
    E --> F[Run ISA Validator Wrapper Script];
    F -- Success --> G[Append Success to project_journal.md];
    F -- Failure --> H[Append Failure to project_journal.md];
    H --> I[Alert Team (CI/CD Notification)];
    G --> J[Continue CI/CD Pipeline];
    J --> K[Deploy/Release];
    subgraph Scheduled Checks
        L[Nightly Cron Job] --> F;
    end
    F --> M[Update status_dashboard.md];
    F --> N[Log detailed issues to isa/logs/venv_issues.log];
```

This plan provides a robust framework for ensuring the ISA project's environment consistency through continuous validation.