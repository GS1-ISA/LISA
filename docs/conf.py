from datetime import datetime

project = "ISA SuperApp"
author = "ISA Team"
copyright = f"{datetime.now():%Y}, {author}"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.mermaid",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # Exclude research artifacts/templates by default (curate via toctree when wanted)
    "research/**",
    "templates/**",
    # Exclude data-style files under docs from Sphinx scanning
    "**/*.csv",
    "**/*.json",
    "**/*.jsonl",
    "**/*.yaml",
    "**/*.yml",
    "**/*.pdf",
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

myst_enable_extensions = [
    "colon_fence",
]

# Interpret fenced code blocks with language "mermaid" as mermaid directives
myst_fence_as_directive = [
    "mermaid",
]
