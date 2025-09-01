from typing import Dict, Any


class Critic:
    """Produces structured critiques (skeleton)."""

    def review(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return {"summary": "Looks good", "actions": []}

