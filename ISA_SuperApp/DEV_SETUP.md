Last updated: 2025-09-02
macOS Developer Quick Setup (M1 optimized)

This file lists the exact steps to prepare a macOS development environment for the
ISA SuperDesign project.

Prerequisites
- macOS with Xcode Command Line Tools installed: xcode-select --install
- Python 3.11+ (system Python 3.13.6 is known to work)
- Node.js 18+ or Node 24+ (project tested with Node v24.5.0)
- Homebrew (optional, recommended)

Quickstart (Devcontainer)

If you use VS Code, open the repo and choose “Reopen in Container”. The devcontainer installs Python 3.11, ruff/mypy/pytest, gh, and pre-commit hooks.

Local Steps

1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

2) Install Python dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3) Make the project editable-install (recommended)

```bash
pip install -e .
```

4) Install Node dependencies for the desktop app

```bash
cd desktop/electron
npm install
cd -
```

5) Create a local `.env` from the template and fill secrets (DO NOT commit `.env`)

```bash
cp .env.example .env
# edit .env and provide real API keys and DB credentials
```

6) Verify required environment variables

```bash
source .venv/bin/activate
python scripts/check_env.py
```

7) Run tests

```bash
source .venv/bin/activate
pytest -q
```

8) Run the FastAPI server (dev)

```bash
source .venv/bin/activate
uvicorn src.api_server:app --reload --port 8787
```

9) Run the Electron app (dev)

```bash
# in one terminal
source .venv/bin/activate
# start local API server first
uvicorn src.api_server:app --reload --port 8787

# in another terminal
cd desktop/electron
npm run dev
```

10) Build macOS DMG

Requirements: Xcode & electron-builder prerequisites

```bash
cd desktop/electron
npm run dist
```

Notes
- Keep `.env` out of source control. `.env.example` contains placeholders.
- If tests fail with import errors, ensure you've run `pip install -e .` or run pytest using the venv Python as shown above.

Additional macOS helper

```
# If you need Xcode Command Line Tools installed, run:
./scripts/install_xcode_cli.sh

# Review development practices at docs/development_practices.md
```

CI notes

- The GitHub Actions workflow supports skipping code signing in CI by setting the `SKIP_SIGNING` environment variable to `true` (default in the workflow). If you have signing configured in GitHub Secrets, set `SKIP_SIGNING=false` to allow full signed builds.
- Build artifacts from the Electron build are uploaded to the workflow run as an artifact named `electron-dist` for inspection.
- To clean logs and temporary build files locally, run:

```bash
./scripts/cleanup_logs_and_builds.sh

Agentic utilities (local-first)

- Update docs timestamps: `python3 scripts/auto_doc_update.py`
- Index/search docs: `make index`, then `python3 scripts/query_index.py --md "determinism"`
- Lint docs links/Refs: `make docs-lint` (writes `docs/audit/docs_ref_report.md`)
- Prepare PR notes (Plan/Diff/Evidence): `make pr-notes` (writes `agent/outcomes/PR_NOTES.md`)
- Log outcomes and summarize: `python3 scripts/agent_outcomes.py --task "X" --strategy scaffold_repair --status success`, then `make outcomes-summary`
```
