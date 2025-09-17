from __future__ import annotations

import importlib
import json
from pathlib import Path


def test_feature_flag_gating_prefers_env_override_and_respects_FEATURE_FLAGS(
    tmp_path, monkeypatch
):
    # Ensure no ENV override active initially
    monkeypatch.delenv("CONTEXT7_ENABLED", raising=False)
    # Enable feature flags only when requested
    monkeypatch.delenv("FEATURE_FLAGS_ENABLED", raising=False)

    # Point flags file to a temp path used only in this test
    impl = importlib.import_module("src.docs_provider.src.docs_provider.context7")
    impl.FLAGS_FILE = Path(tmp_path) / "flags.json"

    from src.docs_provider.base import NullProvider
    from src.docs_provider.context7 import Context7Provider, get_provider

    # No flag eval (FEATURE_FLAGS_ENABLED unset) -> NullProvider
    if impl.FLAGS_FILE.exists():
        impl.FLAGS_FILE.unlink()
    provider = get_provider()
    assert isinstance(provider, NullProvider)

    # FEATURE_FLAGS_ENABLED=1 but traffic=0 -> NullProvider
    monkeypatch.setenv("FEATURE_FLAGS_ENABLED", "1")
    impl.FLAGS_FILE.write_text(
        json.dumps(
            {
                "flags": {
                    "ISA_REF_DOCS_PROVIDER_20990101": {"enabled": True, "traffic": 0}
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    provider = get_provider()
    assert isinstance(provider, NullProvider)

    # FEATURE_FLAGS_ENABLED=1 and traffic>0 -> Context7Provider
    impl.FLAGS_FILE.write_text(
        json.dumps(
            {
                "flags": {
                    "ISA_REF_DOCS_PROVIDER_20990101": {"enabled": True, "traffic": 1}
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    provider = get_provider()
    assert isinstance(provider, Context7Provider)

    # ENV override forces Context7 even if flags disabled
    monkeypatch.setenv("CONTEXT7_ENABLED", "1")
    monkeypatch.setenv("FEATURE_FLAGS_ENABLED", "0")
    provider = get_provider()
    assert isinstance(provider, Context7Provider)
