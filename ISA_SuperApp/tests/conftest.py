import importlib
import os
import sys


def pytest_configure(config):
    """Make tests importable whether the package is installed or not.

    Preferred workflow is to develop with an editable install (pip install -e .).
    If the package is not installed, fall back to adding the repo root to sys.path.
    """
    try:
        # Try importing the installed package first
        importlib.import_module("isa_superdesign")
    except Exception:
        repo_root = os.path.dirname(os.path.dirname(__file__))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
