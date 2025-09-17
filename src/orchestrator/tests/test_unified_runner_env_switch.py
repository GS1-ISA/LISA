
from orchestrator.graph import PlanToolReflect


def test_unified_runner_env_switch_uses_adapter_stub(monkeypatch):
    monkeypatch.setenv("ORCHESTRATOR_USE_AGENT_CORE", "1")
    # Ensure adapter stays in stub mode to avoid heavy deps in CI
    monkeypatch.setenv("ADAPTER_STUB_MODE", "1")
    runner = PlanToolReflect()
    res = runner.run("unify orchestration")
    assert res.final.startswith("Final answer:")
    # We expect at least plan/research/synthesize markers from adapter stub
    assert any(s.startswith("plan:") for s in res.steps)
