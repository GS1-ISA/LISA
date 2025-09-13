from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests


@dataclass
class FetchRecord:
    url: str
    ok: bool
    status: int
    bytes: int
    sha256: str
    fetched_at: float
    from_cache: bool
    note: str = ""


def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _robots_allowed(url: str, user_agent: str = "ISA-ResearchBot") -> bool:
    try:
        from urllib import robotparser

        rp = robotparser.RobotFileParser()
        p = urlparse(url)
        robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        # Fail-closed: if robots cannot be fetched/parsed, deny
        return False


def fetch(
    url: str,
    *,
    cache_dir: str | Path = ".cache/research",
    allow_network: bool = False,
    user_agent: str = "ISA-ResearchBot",
    timeout: int = 20,
    audit_log: str | Path = "docs/audit/research_audit.jsonl",
) -> tuple[Optional[bytes], FetchRecord]:
    """Fetch url with caching, optional network, and audit logging.

    - If url is a local path or file://, read locally (no network).
    - If allow_network is False, only return from cache (or None).
    - When network is allowed, honor robots.txt (fail-closed if not allowed).
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    audit_path = Path(audit_log)
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    parsed = urlparse(url)
    # Local file handling
    if parsed.scheme in ("", "file"):
        path = Path(parsed.path if parsed.scheme == "file" else url)
        data = path.read_bytes()
        sha = _sha256_bytes(data)
        rec = FetchRecord(
            url=str(path),
            ok=True,
            status=200,
            bytes=len(data),
            sha256=sha,
            fetched_at=time.time(),
            from_cache=True,
            note="local-file",
        )
        with audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec)) + "\n")
        return data, rec

    # Network: check cache first (by URL sha)
    url_key = hashlib.sha256(url.encode("utf-8")).hexdigest()
    cache_file = cache_dir / f"{url_key}.bin"
    meta_file = cache_dir / f"{url_key}.json"
    if cache_file.exists():
        data = cache_file.read_bytes()
        sha = _sha256_bytes(data)
        rec = FetchRecord(
            url=url,
            ok=True,
            status=200,
            bytes=len(data),
            sha256=sha,
            fetched_at=time.time(),
            from_cache=True,
            note="cache-hit",
        )
        with audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec)) + "\n")
        return data, rec

    # Allow override via env var (for nightly jobs); PR CI should keep default False
    env_allow = os.getenv("ALLOW_RESEARCH_LIVE", "0") == "1"
    if not (allow_network or env_allow):
        rec = FetchRecord(
            url=url,
            ok=False,
            status=0,
            bytes=0,
            sha256="",
            fetched_at=time.time(),
            from_cache=False,
            note="network-disabled",
        )
        with audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec)) + "\n")
        return None, rec

    # Robots check
    if not _robots_allowed(url, user_agent=user_agent):
        rec = FetchRecord(
            url=url,
            ok=False,
            status=0,
            bytes=0,
            sha256="",
            fetched_at=time.time(),
            from_cache=False,
            note="robots-disallow",
        )
        with audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec)) + "\n")
        return None, rec

    headers = {"User-Agent": user_agent}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        ok = 200 <= r.status_code < 300
        data = r.content if ok else b""
        sha = _sha256_bytes(data) if ok else ""
        if ok:
            cache_file.write_bytes(data)
            meta_file.write_text(
                json.dumps(
                    {
                        "url": url,
                        "status": r.status_code,
                        "headers": dict(r.headers),
                        "sha256": sha,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        rec = FetchRecord(
            url=url,
            ok=ok,
            status=r.status_code,
            bytes=len(data),
            sha256=sha,
            fetched_at=time.time(),
            from_cache=False,
        )
    except Exception as e:
        rec = FetchRecord(
            url=url,
            ok=False,
            status=0,
            bytes=0,
            sha256="",
            fetched_at=time.time(),
            from_cache=False,
            note=f"error:{e}",
        )
        data = None

    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(rec)) + "\n")
    return data, rec
