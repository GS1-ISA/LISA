from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]


def basic_validate_columns(df, required: list[str]) -> ValidationResult:
    missing = [c for c in required if c not in df.columns]
    if missing:
        return ValidationResult(False, [f"Missing: {missing}"], [])
    return ValidationResult(True, [], [])
