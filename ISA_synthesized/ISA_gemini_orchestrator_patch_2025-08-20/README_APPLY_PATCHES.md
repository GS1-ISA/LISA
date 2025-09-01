# ISA Gemini Orchestrator Patch
Generated: 2025-08-20T10:09:27.414815Z

## Contents
- `GEMINI.md` (drop-in orchestrator prompt replacement)
- `.env.example` (complete, documented)
- `CHANGELOG.md` (initialized)
- `.gemini/workspace.json` (workspace registry)
- `docs/PROJECT_MEMORY.md` (curated long-term memory)
- `scripts/` (new or updated scripts):
  - `generate_tokens.py`
  - `verify_credentials.py`
  - `smoke_test.py`
  - `start_isa_servers.sh`
- `patches/` (unified diffs):
  - `api_server_subprocess_and_static.patch`
  - `generate_tokens_addition.patch`
  - `verify_credentials_addition.patch`
  - `smoke_test_addition.patch`

## How to apply
1. **Back up or commit your current work.**
2. Extract this archive at the **project root** (same level as `src/`, `scripts/`, `docs/`, etc.).
3. Copy/merge top-level files into your repo:
   - Replace `GEMINI.md` with the provided one.
   - Add/merge `.env.example`, `CHANGELOG.md`, `.gemini/workspace.json`, `docs/PROJECT_MEMORY.md`.
   - Add/replace scripts under `scripts/` as needed.
4. Apply patches (best effort, may require manual merges):
   ```bash
   git apply --reject --whitespace=fix patches/api_server_subprocess_and_static.patch || true
   git apply --reject --whitespace=fix patches/generate_tokens_addition.patch || true
   git apply --reject --whitespace=fix patches/verify_credentials_addition.patch || true
   git apply --reject --whitespace=fix patches/smoke_test_addition.patch || true
   ```
   If any `.rej` files are created, open them and manually integrate the hunks.
5. Ensure dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # ensure 'requests' is available for smoke_test
   ```
6. Verify:
   ```bash
   python scripts/verify_credentials.py
   python scripts/generate_tokens.py --out webui/tokens.css
   python scripts/smoke_test.py || true
   ```
7. Start the app (dev):
   ```bash
   ./scripts/start_isa_servers.sh
   ```

## Notes
- If `git apply` fails due to context mismatches, use the provided full-file versions in `scripts/` and adjust `src/api_server.py` per the patch logic.
- Remember to add your secrets to `.env` (do **not** commit them).

