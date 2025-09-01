from typing import Any


class Builder:
    """Applies patches, runs tools (skeleton)."""

    def apply(self, changes: dict[str, Any]) -> bool:
        # Placeholder always succeeds
        return True
