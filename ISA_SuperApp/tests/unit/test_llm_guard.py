import os
import importlib


def test_llm_client_forbid_direct_llm(monkeypatch):
    monkeypatch.setenv("ISA_FORBID_DIRECT_LLM", "1")
    # Reload module to ensure env is read
    mod = importlib.import_module("src.llm_client")
    importlib.reload(mod)
    try:
        mod.LLMClient()
        assert False, "Expected policy guard to raise"
    except RuntimeError as e:
        assert "forbidden" in str(e).lower()

