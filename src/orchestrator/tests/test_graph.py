from orchestrator import PlanToolReflect


def test_plan_tool_reflect_runs():
    g = PlanToolReflect()
    res = g.run("hello orchestrator")
    assert res.final.startswith("Final answer: ")
    assert any(s.startswith("plan:") for s in res.steps)
    assert any(s.startswith("tool:") for s in res.steps)
    assert any(s.startswith("reflect:") for s in res.steps)

