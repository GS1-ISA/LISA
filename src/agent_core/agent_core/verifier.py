from typing import Any


class Verifier:
    """Runs quality gates (skeleton)."""

    def verify(self, context: dict[str, Any]) -> dict[str, bool]:
        return {"lint": True, "tests": True, "typecheck": True}
