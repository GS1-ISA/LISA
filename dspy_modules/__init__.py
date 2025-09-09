"""Compatibility shim for tests importing `dspy_modules`.

Delegates to the canonical implementation under `src.dspy.src.dspy_modules`.
"""

from src.dspy.src.dspy_modules.modules import ClassifierStub  # noqa: F401
