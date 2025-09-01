# ISA SuperDesign  Full Package (2025-08-17)

See `DEV_SETUP.md` for a concise macOS developer quick setup.

- API: FastAPI at `127.0.0.1:8787`

CI secrets (GitHub)

This project uses GitHub Actions for macOS builds. To enable signing and
notarization you must add a few repository secrets under Settings → Secrets
and variables → Actions. Typical secrets and names used in this repo:

- `SKIP_SIGNING` (set to `true` to skip signing in CI; set `false` to enable)
- `MACOS_SIGNING_P12` (base64-encoded .p12 signing certificate)
- `MACOS_SIGNING_P12_PASSWORD`
- `MACOS_SIGNING_KEYCHAIN_PASSWORD`
- `APPLE_API_KEY_ID`
- `APPLE_API_ISSUER_ID`
- `APPLE_API_PRIVATE_KEY` (base64-encoded .p8 private key)

Basic steps to add a secret:

1. In your repository on GitHub, go to Settings → Secrets and variables → Actions.
2. Click New repository secret and paste the secret name and value.
3. For binary files (p12/.p8) base64-encode them locally and paste the base64 string.

See `docs/ci_secrets.md` for more details and example workflow snippets.
- UIs: /ui/users, /ui/admin (login), /ui/graph, /metrics
- Desktop: Electron DMG/NSIS under `desktop/electron`
- Docs: MkDocs in `docs/` (`scripts/docs_serve.sh`)
- Tests: `scripts/test_all.sh` (mac) or `scripts\win\test_all.ps1` (Windows)

## Quickstart
See `docs/install.md` and `docs/quickstart.md`.
