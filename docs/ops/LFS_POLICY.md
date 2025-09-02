Title: Git LFS Policy — Large/Binary Assets
Last updated: 2025-09-02

Scope
- Store large or binary assets via Git LFS rather than in the main git history.

Tracked patterns (.gitattributes)
- `*.zip`, `*.tar.gz`, `*.tgz`, `*.7z`, `*.dmg`, `*.pdf`, `*.bin`

Setup (one-time on developer machine)
```bash
brew install git-lfs   # or package manager equivalent
git lfs install
```

Usage
- Add matching files normally; Git LFS will handle pointer creation.
- Do not commit archives as source of truth; prefer reproducible scripts or release artifacts.

CI/Release
- Prefer uploading large artifacts to CI/release assets over keeping them in the repo.

