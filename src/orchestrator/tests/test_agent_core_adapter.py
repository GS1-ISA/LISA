import os

from orchestrator.agent_core_adapter import OrchestratorAgentRunner


def test_agent_core_adapter_stub_mode():
    os.environ["ADAPTER_STUB_MODE"] = "1"
    runner = OrchestratorAgentRunner()
    res = runner.run("test goal")
    assert res.final.startswith("Final answer:")
    assert any(step.startswith("plan:") for step in res.steps)
    assert any(step.startswith("research:") for step in res.steps)
    assert any(step.startswith("synthesize:") for step in res.steps)

