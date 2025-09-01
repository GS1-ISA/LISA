Last updated: 2025-09-02
Development Practices

Keep the repository clean and reproducible. Follow these rules:

- Always create a `.venv` for local development and use it to run tests.
- Prefer `pip install -e .` during development so tests import the package naturally.
- Keep a `logs/` folder for important install/build logs (ignored by git if contains secrets).
- After any change that affects runtime behaviour, update or add tests that cover the change.
- Update `DEV_SETUP.md` and `README.md` when setup steps change.
- Keep CI green: add a GitHub Actions workflow that installs deps, runs tests, and builds artifacts.
- Keep a small audit log of actions (install/build/test) in `logs/`.

Cleanup
- Use `scripts/cleanup_logs_and_builds.sh` to prune `logs/`, electron `dist/`, and `node_modules` when you need to reclaim space or reset local build artifacts.

