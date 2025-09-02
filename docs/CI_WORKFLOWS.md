Title: CI Workflows Overview — PR, Nightly, Weekly
Last updated: 2025-09-02

PR (ci.yml)
- Lint/format (ruff): gate.
- Typecheck (mypy): initially advisory, becomes gate once green.
- Tests (pytest+coverage): advisory until thresholds met; then gate.
- Security (bandit, pip-audit, gitleaks): advisory → gate.
- Artifacts: coverage.xml if present; logs.
 - Combined Coverage: runs app + packages + infra tests with coverage and uploads `coverage-total.xml`; advisory no-regression check against baseline.
 - Memory coherence: enforced drift gate; uploads memory logs snapshot.
 - Coherence Audit: generates repo graph and KPIs; uploads scorecard and lists.
 - Package Wheels: builds stub package wheels (advisory) and uploads artifacts.
  - Bloat Check: runs prune_bloat.py (dry-run) and uploads `bloat_candidates.txt` as an artifact.
 - Memory: advisory coherence gate; snapshot of JSONL memory logs uploaded as artifact.

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

Coverage Details
- `.coveragerc` omits tests and stdlib and enables branch coverage; sources include app, packages, and infra where relevant.

Bloat & LFS
- `scripts/prune_bloat.py` identifies OS cruft, archives, and temp folders. CI uploads candidates (advisory) to keep clutter from creeping back.
- Large/binary files should be tracked via LFS where retention is required (see `docs/ops/LFS_POLICY.md`).

Promotion Criteria — Memory Coherence Gate
- Stability: 7 consecutive PR runs with drift <= configured threshold (default 0.9) and no gate warnings.
- Coverage: memory unit tests green (`test_memory_router.py`, `test_memory_drift.py`) across supported Python versions.
- Artifacts: memory logs snapshot uploaded on each PR; artifact present for last 7 runs.
- Privacy/Audit: deletion events (when present) are logged with reasons; audit test passes.
- Flakiness: no intermittent failures attributed to memory gate during the stability window.
Once these conditions are met, flip the memory coherence gate from advisory to enforced and document the change in `docs/QUALITY_GATES.md` and the release notes.

Planned CI (Guilds)
- Diplomacy Guild: ingestion coverage checks, summary sampling accuracy, horizon‑scanning evidence logging.
- Standards Guild: co‑authoring/publisher lint jobs, digital balloting smoke, dissent resolution workflow tests.

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

Local-First Utilities (make)
- `make docs-lint`: Lint markdown titles, links, and Refs; report to `docs/audit/docs_ref_report.md`.
- `make pr-notes`: Generate `agent/outcomes/PR_NOTES.md` with Plan/Diff/Evidence ready for PRs.
- `make outcomes-summary`: Summarize agent outcomes to `docs/audit/agent_outcomes_summary.md`.
- `make healthcheck`: Run lint, types (advisory), determinism snapshot, security scans, and docs lint; report to `docs/audit/healthcheck.md`.
