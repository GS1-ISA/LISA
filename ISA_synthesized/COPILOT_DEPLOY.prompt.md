# AI Agent Workspace Setup Guide
Last updated: 2025-09-02

You are an AI assistant (GitHub Copilot, Gemini, etc.) in VS Code. Your primary objective is to fully configure this workspace for development. Follow the steps below precisely. After each major step, provide a ✅ status update.

## 1. Environment Prerequisites

Ensure the following are installed on the system. If not, ask the user to install them:
- [ ] macOS 14+ or Windows 11+
- [ ] Python 3.11+
- [ ] Node.js 20+ and npm
- [ ] `git` command line tools
- [ ] For macOS: Xcode Command Line Tools (`xcode-select --install`)
- [ ] For macOS: Homebrew (optional, for `make`)

## 2. VS Code Extensions

Install the following essential VS Code extensions. Verify that each is installed and enabled.

- [ ] **Python** (`ms-python.python`) - Core Python support.
- [ ] **Pylance** (`ms-python.vscode-pylance`) - High-performance language server for Python.
- [ ] **Electron** (`electron-react-devtools.electron-react-devtools`) - Electron development tools.
- [ ] **Prettier - Code formatter** (`esbenp.prettier-vscode`) - Code formatter.
- [ ] **ESLint** (`dbaeumer.vscode-eslint`) - Linter for JavaScript and TypeScript.
- [ ] **EditorConfig for VS Code** (`EditorConfig.EditorConfig`) - Enforces coding styles.
- [ ] **DotENV** (`mikestead.dotenv`) - Syntax highlighting for `.env` files.

**Acceptance Criteria:** All listed extensions are installed and enabled in VS Code.

## 3. Workspace Configuration

### 3.1. Python Environment

1.  [ ] Create a Python virtual environment in the project root:
    ```bash
    python3 -m venv .venv
    ```
2.  [ ] Install all required Python dependencies:
    ```bash
    .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```
3.  [ ] Select the virtual environment's Python interpreter in VS Code. Use the `Python: Select Interpreter` command and choose the one in the `.venv` directory.

**Acceptance Criteria:** The Python virtual environment is created, dependencies are installed, and the correct interpreter is selected in VS Code.

### 3.2. Node.js Environment

1.  [ ] Install the Node.js dependencies for the Electron app:
    ```bash
    cd desktop/electron
    npm install
    cd ../..
    ```

**Acceptance Criteria:** All Node.js dependencies are installed in the `desktop/electron` directory.

### 3.3. Environment Variables

1.  [ ] Create a `.env` file in the project root by copying the `.env.example` file.
2.  [ ] The `.env` file should contain placeholders for the required API keys (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, etc.). Ask the user to fill them in.

**Acceptance Criteria:** A `.env` file exists in the project root with the necessary variables.

## 4. VS Code Workspace Settings

Create or update the `.vscode/settings.json` file with the following content. This will configure the editor for optimal formatting and linting.

```json
{
  "python.pythonPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.pylintEnabled": false,
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "files.exclude": {
    "**/.git": true,
    "**/.svn": true,
    "**/.hg": true,
    "**/CVS": true,
    "**/.DS_Store": true,
    "**/__pycache__": true,
    "**/.venv": true
  }
}
```

**Acceptance Criteria:** The `.vscode/settings.json` file is created and contains the specified settings.

## 5. Launch and Debug Configurations

Create or update the `.vscode/launch.json` file with the following configurations. This will enable debugging for both the backend and the desktop app.

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.api_server:app",
        "--reload"
      ],
      "jinja": true
    },
    {
      "name": "Electron: Main",
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}/desktop/electron",
      "runtimeExecutable": "${workspaceFolder}/desktop/electron/node_modules/.bin/electron",
      "windows": {
        "runtimeExecutable": "${workspaceFolder}/desktop/electron/node_modules/.bin/electron.cmd"
      },
      "args": [
        "."
      ],
      "outputCapture": "std"
    }
  ]
}
```

**Acceptance Criteria:** The `.vscode/launch.json` file is created and contains the specified launch configurations.

## 6. Task Configurations

Create or update the `.vscode/tasks.json` file with the following configurations. This will enable running common tasks directly from VS Code.

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": ".venv/bin/activate && pytest",
      "windows": {
        "command": ".venv\\Scripts\\activate && pytest"
      },
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Build DMG",
      "type": "shell",
      "command": "cd desktop/electron && npm run dist",
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

**Acceptance Criteria:** The `.vscode/tasks.json` file is created and contains the specified task configurations.

## 7. Final Verification and Self-Assessment

To ensure the workspace is fully configured, perform the following checks:

- [ ] Run the "Run Tests" task and confirm that all tests pass.
- [ ] Start debugging the "Python: FastAPI" launch configuration and confirm that the server starts without errors.
- [ ] Start debugging the "Electron: Main" launch configuration and confirm that the desktop app launches.

**Completeness Score:**

After completing all the steps, provide a completeness score from 1 to 5 (5 being the highest) and a brief justification for your score. This will help to ensure that the workspace is fully configured and ready for development.

**Example Justification:** "I have completed all the steps in the setup guide. The tests are passing, and both the backend and the desktop app can be launched and debugged successfully. I have also installed and configured all the recommended extensions and workspace settings. Therefore, I am confident that the workspace is fully configured."
