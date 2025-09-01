from typing import Dict, Any


class Builder:
    """Applies patches, runs tools (skeleton)."""

    def apply(self, changes: Dict[str, Any]) -> bool:
        # Placeholder always succeeds
        return True

