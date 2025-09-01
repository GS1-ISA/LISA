from typing import Any


class Critic:
    """Produces structured critiques (skeleton)."""

    def review(self, result: dict[str, Any]) -> dict[str, Any]:
        return {"summary": "Looks good", "actions": []}
