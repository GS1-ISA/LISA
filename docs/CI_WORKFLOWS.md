Title: CI Workflows Overview — PR, Nightly, Weekly

PR (ci.yml)
- Lint/format (ruff): gate.
- Typecheck (mypy): initially advisory, becomes gate once green.
- Tests (pytest+coverage): advisory until thresholds met; then gate.
- Security (bandit, pip-audit, gitleaks): advisory → gate.
- Artifacts: coverage.xml if present; logs.

Deep Checks (on-demand, nightly.yml via workflow_dispatch)
- Mutation tests (mutmut) on mapping logic.
- Fuzzing (atheris) for parsers (curated targets).
- Benchmarks (pytest-benchmark) and perf budget diff.

Formal & Supply Chain (on-demand, weekly.yml via workflow_dispatch)
- CrossHair on pure mapping utilities (curated list).
- SBOM generation (syft) and container scans (trivy).

Event‑Driven Maintenance
- Heavy checks are triggered by significance of changes rather than fixed schedules. Criteria include:
  - Large diffs (LOC/files), critical modules touched, dependency or Docker changes
  - Coverage/type/security regressions, complexity increases
- You can also run deep checks manually via the on‑demand workflows.

Agent Check (on-demand, agent_check.yml)
- Runs `agent/check.py` to execute a compact, container-free self-test harness:
  - ruff format/check, mypy (advisory), pytest + coverage XML, semgrep JSON (advisory), docs build (if mkdocs present)
  - Emits `agent/outcomes/<run_id>.json` and uploads it as an artifact for agent parsing

Current thresholds and critical paths (tunable)
- Thresholds: files changed > 15 OR total LOC delta (adds+deletes) > 500
- Critical paths (any touch triggers deep checks):
  - `ISA_SuperApp/src/pipelines`, `ISA_SuperApp/src/nesy`, `ISA_SuperApp/src/utils`, `ISA_SuperApp/src/api_server.py`
  - `ISA_SuperApp/schemas`, `ISA_SuperApp/Dockerfile`, `ISA_SuperApp/docker-compose.yml`
  - `ISA_SuperApp/requirements.txt`, `ISA_SuperApp/requirements-dev.txt`, `infra/`

Gating Schedule
- Start permissive (advisory) to avoid blocking; flip to gating per plan acceptance when green.

Automation — Git & PR Management
- Auto PR on push (auto_pr.yml): opens a PR to `main` for any branch push; adds `autoupdate` label.
- PR Labeler (labeler.yml): applies labels by path; adds `autoupdate` to all PRs.
- Auto update PR branch (auto_update.yml): rebases/merges `main` into PRs labeled `autoupdate`.
- Auto format (format_autocommit.yml): applies `ruff format` and commits back to same-repo PR branches.
- Commit message lint (commitlint.yml): enforces Conventional Commits on PRs.
- Auto-merge (automerge.yml): when `automerge` label present and checks pass, enables squash auto-merge.
- Releases (release-please.yml): drafts release PRs and tags based on commit history.
- Docs auto-sync (docs_auto_sync.yml): updates “Last updated” lines in docs and opens a PR.
- Research benches (poc_bench.yml): runs Q11/Q12 micro-benches and opens a PR with results.
