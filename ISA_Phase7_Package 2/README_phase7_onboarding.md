# ISA Phase 7 Developer Onboarding

## Purpose
Prepare new contributors for involvement in Phase 7 (Externalization & Ecosystem Growth) of the ISA project.

## Key Concepts
- **Federation Support**: Multiple independent ISA instances exchanging standard ontologies and prompts.
- **Trust and Attribution**: Tracking sources of knowledge and decisions across federated nodes.
- **Cross-org Collaboration**: Integrating external contributions with governance rules and evaluation thresholds.

## Toolchain
- **Gemini 2.5 Pro** for prompt expansion and structured AI evaluation
- **OpenAI Codex-1** for code transformation, mutation, and test writing
- **Roocode 2025 IDE** for agent execution, governance enforcement, and doc-based development

## How to Contribute
1. Clone the repo and install dependencies via `scripts/setup.sh`
2. Review `VERSION.yaml` for compatibility guidelines
3. Follow the roadmap in `docs/phases/phase7.md`
4. Use prebuilt templates in `docs/templates/` to expand documentation or prompts
5. Submit changes via GitHub with required metadata attached

## Verification
Run `scripts/check_drift.py` weekly to validate that all document templates and expansions are in sync with governance and schema rules.
