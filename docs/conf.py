import os
import sys
from datetime import datetime

project = "ISA SuperApp"
author = "ISA Team"
copyright = f"{datetime.now():%Y}, {author}"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
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
    "audit/*",
]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

myst_enable_extensions = [
    "colon_fence",
]
