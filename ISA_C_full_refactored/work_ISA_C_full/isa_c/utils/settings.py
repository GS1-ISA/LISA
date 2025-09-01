from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path
import os


class Settings(BaseSettings):
    data_dir: Path = Path(os.getenv("ISA_DATA_DIR", "data"))
    offline: int = int(os.getenv("ISA_OFFLINE", "1"))
    log_level: str = os.getenv("ISA_LOG_LEVEL", "INFO")
    default_modules: list[str] = ["cellar", "efrag", "eurostat", "sec", "gs1", "gs1nl"]

    model_config = SettingsConfigDict(env_prefix="ISA_", env_file=".env", extra="ignore")

    @field_validator("default_modules", mode="before")
    @classmethod
    def _split_modules(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


SETTINGS = Settings()
