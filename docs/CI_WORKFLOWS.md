# CI Workflows Overview — PR, Nightly, Weekly
Last updated: 2025-09-10

PR (ci.yml)
- Lint/format (ruff): enforced.
- Typecheck (mypy): advisory → enforced after stability window.
- Tests (pytest+coverage): advisory; core coverage gate promoted after stability.
- Determinism: enforced (deterministic splitter test, offline).
- Security (bandit, pip-audit, gitleaks): advisory → enforced.
- Concurrency: cancel in‑progress runs per ref; pip cache enabled; pytest‑xdist for parallel tests.
- Artifacts/signals (advisory):
  - Combined Coverage: `coverage-total.xml`; no‑regression check.
  - Memory coherence: drift check (advisory) + memory log snapshot (artifact).
  - Latency Histogram: `perf_histogram.json` from scripts/perf_hist.py.
  - Coherence Audit: repo graph and KPIs (on demand).
  - Bloat Check: `bloat_candidates.txt` from prune_bloat.py (dry‑run).

Deep Checks (scheduled + on-demand)
- Nightly (nightly.yml): curated mutation tests, benchmarks; adapter env‑switch test (orchestrator→agent_core in stub mode).
- Determinism matrix (determinism_matrix.yml): daily cross‑OS test (advisory).

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
- Critical paths (any touch triggers deep checks) — this repository variant:
  - Core agents/orchestrator: `src/agent_core/**`, `src/orchestrator/**`
  - Research tooling and memory: `src/tools/**`, `src/docs_provider/**`, `infra/rag/**`
  - CI/Infra and dependency surfaces: `.github/workflows/**`, `infra/**`, `requirements*.txt`, `pyproject.toml`, `Makefile`

  Historical paths referencing `ISA_SuperApp/**` apply to the API‑first variant and are not active here.

Gating Schedule
- Start permissive (advisory) to avoid blocking; flip to gating per plan acceptance when green. Determinism is already enforced.

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

Additional Workflows
- Virtuous Cycle (virtue_cycle.yml): daily meta audit, docs build (advisory), cost telemetry, virtue log artifact.
- Meta Audit (meta_audit.yml): weekly inventory + risk X‑ray; auto‑maintains Top Risk issue.
- PDF Index (pdf_index.yml): manual job builds `pdf_index.jsonl` from ISA goals PDFs using `scripts/ingest_pdfs.py`.
- PR Metric Guard (pr_metric_guard.yml): blocks PRs missing a metric‑delta sentence.
- Import Discipline: advisory guard ensures orchestrator/llm do not import agent_core except via adapter.

Planned CI (Guilds)
- Diplomacy Guild: ingestion coverage checks, summary sampling accuracy, horizon‑scanning evidence logging.
- Standards Guild: co‑authoring/publisher lint jobs, digital balloting smoke, dissent resolution workflow tests.

Automation — Git & PR Management
- Auto PR on push (`auto_pr.yml`): opens a PR to `main` for any branch push; adds `autoupdate` label.
- PR Labeler (`labeler.yml`): applies labels by path; adds `autoupdate` to all PRs.
- Auto update PR branch (`auto_update.yml`): rebases/merges `main` into PRs labeled `autoupdate`.
- Auto format (`format_autocommit.yml`): applies `ruff format` and commits back to same-repo PR branches.
- Commit message lint (`commitlint.yml`): enforces Conventional Commits on PRs.
- Auto-merge (`automerge.yml`): when `automerge` label present and checks pass, enables squash auto-merge.
- Releases (`release-please.yml`): drafts release PRs and tags based on commit history.
- Docs auto-sync (`docs_auto_sync.yml`): updates “Last updated” lines in docs and opens a PR.
- Research benches (`poc_bench.yml`): runs Q11/Q12 micro-benches and opens a PR with results.
- Context7 Parity (`context7.yml`): runs documentation parity checks against the live provider (requires secrets).
- Repository Index (`repo_index.yml`): Periodically runs the `make index` command.
- Tidy (`tidy.yml`): A workflow for general repository maintenance tasks.

Container Smoke Tests
- Some CI jobs reference building and curling an API container (`uvicorn src.api_server:app ...`). This repository does not include `src/api_server.py`; those steps are advisory/no‑op unless you add a minimal FastAPI app.

Local-First Utilities (make)
- `make docs-lint`: Lint markdown titles, links, and Refs; report to `docs/audit/docs_ref_report.md`.
- `make pr-notes`: Generate `agent/outcomes/PR_NOTES.md` with Plan/Diff/Evidence ready for PRs.
- `make outcomes-summary`: Summarize agent outcomes to `docs/audit/agent_outcomes_summary.md`.
- `make healthcheck`: Run lint, types (advisory), determinism snapshot, security scans, and docs lint; report to `docs/audit/healthcheck.md`.
- `make agent-sync`: Meta audit, docs build (advisory), cost report.
- `make virtuous-cycle`: Runs `agent-sync` and appends a virtue log entry.
- `make pdf-index`: Builds `artifacts/pdf_index.jsonl` from ISA goals PDFs for local research memory.
