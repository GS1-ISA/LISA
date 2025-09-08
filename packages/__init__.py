"""Monorepo shim package root.

This repo variant provides some packages only under `src/`. To maintain
backwards compatibility with tests or tools expecting `packages.*`, we expose
thin wrappers in this directory that import from the canonical modules under
`src/`.
"""

