#!/usr/bin/env bash
set -euo pipefail

# Xcode CLI tools
xcode-select -p >/dev/null 2>&1 || xcode-select --install || true

# Homebrew & Node (optional)
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found — skipping brew installs (optional)."
else
  brew list node@20 >/dev/null 2>&1 || brew install node@20
fi

# Enable 'code' CLI if available — user may need to add it from VS Code (Shell Command)
if ! command -v code >/dev/null 2>&1; then
  echo "VS Code 'code' CLI not found. In VS Code: Cmd+Shift+P → 'Shell Command: Install code in PATH'"
else
  # Recommended extensions
  code --install-extension GitHub.copilot || true
  code --install-extension GitHub.copilot-chat || true
  code --install-extension ms-python.python || true
  code --install-extension ms-python.vscode-pylance || true
  code --install-extension ms-python.black-formatter || true
  code --install-extension charliermarsh.ruff || true
  code --install-extension ms-vscode.makefile-tools || true
  code --install-extension ms-azuretools.vscode-docker || true
  code --install-extension esbenp.prettier-vscode || true
  code --install-extension redhat.vscode-yaml || true
  code --install-extension github.vscode-github-actions || true
fi

echo "VS Code bootstrap complete ✅"
