import importlib
import os


def test_orchestrator_stub_loader(monkeypatch):
    monkeypatch.setenv("ISA_USE_ORCHESTRATOR_STUB", "1")
    mod = importlib.import_module("src.utils.orch_loader")
    importlib.reload(mod)
    res = mod.run_orchestrator_stub("hello world")
    assert res is None or res.startswith("Final answer: ")

