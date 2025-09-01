from __future__ import annotations

import os
from datetime import datetime, timedelta

try:
    import duckdb  # type: ignore
except Exception:
    duckdb = None  # type: ignore


class IdempotencyStore:
    def __init__(self, db_path: str = "data/idempotency.duckdb"):
        self.db_path = db_path
        self._conn = None
        if os.getenv("USE_DELTA") == "1" and duckdb is not None:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self._conn = duckdb.connect(db_path)
            self._init_schema()

    def _init_schema(self) -> None:
        if self._conn is None:
            return
        self._conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_jobs (
            job_id VARCHAR PRIMARY KEY,
            status VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );
        """)

    def is_processed(self, job_id: str) -> bool:
        if self._conn is None:
            return False
        row = self._conn.execute(
            "SELECT 1 FROM processed_jobs WHERE job_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)",
            [job_id],
        ).fetchone()
        return row is not None

    def mark_processed(self, job_id: str, ttl_hours: int | None = 24) -> None:
        if self._conn is None:
            return
        expires_at = None
        if ttl_hours is not None:
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
        self._conn.execute(
            "INSERT OR REPLACE INTO processed_jobs (job_id, status, expires_at) VALUES (?, 'completed', ?)",
            [job_id, expires_at],
        )
