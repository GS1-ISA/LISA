Last updated: 2025-09-02
CI Secrets & macOS signing (GitHub Actions)

This file lists the exact environment variable / secret names expected by the
project's CI when you want to enable macOS code signing and notarization.

Principles
- Keep all secrets out of source control. Store them in GitHub repository Secrets.
- Prefer base64-encoding binary files (p12 / p8) when placing them into GitHub
  Secrets to avoid newline/encoding issues.
- Use the `SKIP_SIGNING` CI env var to avoid signing in CI when you don't have
  signing credentials available.

Recommended secret names
- SKIP_SIGNING (string: "true" or "false") — CI toggle; default workflow sets true.

Signing certificate (p12)
- MACOS_SIGNING_P12 (base64) — the macOS Developer ID Application certificate exported as a .p12 file then base64-encoded.
- MACOS_SIGNING_P12_PASSWORD — password used when exporting the .p12 file.
- MACOS_SIGNING_KEYCHAIN_PASSWORD — password for a temporary keychain created during CI (you can generate one per-run).
- TEAM_ID — your Apple Developer Team ID (used by some electron-builder configs).

Notarization (recommended: API key approach)
- APPLE_API_KEY_ID — the Key ID from App Store Connect (e.g. 'ABC123DEFG').
- APPLE_API_ISSUER_ID — the Issuer ID (GUID) for the API key in App Store Connect.
- APPLE_API_PRIVATE_KEY (base64) — the private key (.p8) file content base64-encoded.

Alternative (legacy) notarization using Apple ID app-specific password
- APPLE_ID — Apple ID email used for notarization (less recommended in CI).
- APPLE_APP_PASSWORD — an app-specific password for the Apple ID (if not using API keys).

Other runtime secrets (keep in `.env` or Actions secrets as needed)
- OPENROUTER_API_KEY, ISA_API_KEY_OPENROUTER, OPENAI_API_KEY
- SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
- NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

Example: how to store binaries safely
- Locally: base64 encode before copying to GitHub Secrets
  ```bash
  base64 signing.p12 | pbcopy  # paste into GitHub secret value for MACOS_SIGNING_P12
  base64 AuthKey_ABCDEF1234.p8 | pbcopy  # paste into APPLE_API_PRIVATE_KEY
  ```

Example GitHub Actions snippet: install p12 into a temporary keychain

```yaml
- name: Prepare macOS signing keychain
  if: env.SKIP_SIGNING != 'true'
  env:
    P12_BASE64: ${{ secrets.MACOS_SIGNING_P12 }}
    P12_PASSWORD: ${{ secrets.MACOS_SIGNING_P12_PASSWORD }}
    KEYCHAIN_PASSWORD: ${{ secrets.MACOS_SIGNING_KEYCHAIN_PASSWORD }}
  run: |
    set -euo pipefail
    echo "$P12_BASE64" | base64 --decode > signing.p12
    KEYCHAIN=build.keychain
    security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN"
    security import signing.p12 -k "$KEYCHAIN" -P "$P12_PASSWORD" -T /usr/bin/codesign || true
    security list-keychains -s "$KEYCHAIN" $(security list-keychains | sed -n 's/^\s*"\(.*\)"$/\1/p')
    # Allow codesign and other tools to access the key
    security set-key-partition-list -S apple: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN" || true
    echo "Keychain prepared"

# Remember to cleanup in a later step (delete the keychain):
- name: Cleanup signing keychain
  if: env.SKIP_SIGNING != 'true'
  run: |
    security delete-keychain build.keychain || true
```

Example GitHub Actions snippet: write Apple notary API key file from secret

```yaml
- name: Prepare Apple notary API key
  if: env.SKIP_SIGNING != 'true'
  env:
    APPLE_KEY_ID: ${{ secrets.APPLE_API_KEY_ID }}
    APPLE_ISSUER_ID: ${{ secrets.APPLE_API_ISSUER_ID }}
    APPLE_PRIVATE_KEY_BASE64: ${{ secrets.APPLE_API_PRIVATE_KEY }}
  run: |
    set -euo pipefail
    echo "$APPLE_PRIVATE_KEY_BASE64" | base64 --decode > AuthKey_${APPLE_KEY_ID}.p8
    # You can now use xcrun notarytool with --key/--issuer or set NOTARYTOOL_KEY chain
    ls -l AuthKey_${APPLE_KEY_ID}.p8
```

Example: using notarytool to submit an artifact

```yaml
- name: Notarize app
  if: env.SKIP_SIGNING != 'true'
  env:
    APPLE_KEY_ID: ${{ secrets.APPLE_API_KEY_ID }}
    APPLE_ISSUER_ID: ${{ secrets.APPLE_API_ISSUER_ID }}
  run: |
    # Example: notarize the zip/dmg produced by electron-builder
    xcrun notarytool submit ./dist/YourApp.dmg --key AuthKey_${APPLE_KEY_ID}.p8 --key-id ${APPLE_KEY_ID} --issuer ${APPLE_ISSUER_ID} --wait
    xcrun stapler staple ./dist/YourApp.dmg
```

Notes and tips
- Keep `SKIP_SIGNING=true` in CI until you have configured secrets and verified their correctness.
- Use base64-encoded secrets to avoid accidental truncation or newline issues when storing in GitHub Secrets.
- Test the signing/notarization steps locally first before enabling them in CI; for local testing you can import the p12 into your Keychain manually and run the same `xcrun notarytool` commands.
- For high-security workflows, rotate signing keys regularly and limit access to the GitHub secrets.

If you'd like, I can now: (A) update the CI workflow to install the p12 and notary key only when SKIP_SIGNING=false (conditional steps) — or (B) create a `docs/ci_secrets_example.md` with copy-paste-ready GitHub Actions workflow snippets. Which next?
