from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: list[str] | None = None
    warnings: list[str] | None = None


class BaseAdapter(ABC):
    @abstractmethod
    def fetch(self, since: datetime) -> pd.DataFrame: ...

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        return ValidationResult(True, [], [])

    def run(self, since: datetime) -> pd.DataFrame:
        df = self.fetch(since)
        vr = self.validate(df)
        if not vr.is_valid:
            raise ValueError(f"Validation failed: {vr.errors}")
        return df
