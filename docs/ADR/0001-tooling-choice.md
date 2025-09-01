Title: ADR 0001 — Tooling Choices and Consolidation
Last updated: 2025-09-02

Context
- Aim to maximize signal, minimize bloat.
- Prefer single tools that cover multiple concerns where quality is high.

Decision
- Formatter/Linter: ruff (format + lint + imports). Black optional locally.
- Typing: mypy as CI gate (strict on libs), pyright optional for editors.
- Static analyzers: semgrep (curated), radon (complexity budget), vulture on-demand.
- Security: bandit, pip-audit, gitleaks, trivy (containers). SBOM via syft.
- Testing: pytest, coverage, hypothesis; mutmut nightly; atheris targeted; CrossHair weekly.

Consequences
- Fewer tools reduce config drift; CI is faster and clearer.
- Gating steps are opinionated; short-term transitions may need suppressions.

Status: Accepted

