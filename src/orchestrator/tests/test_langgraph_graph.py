from orchestrator import GraphRunner


def test_graph_runner_returns_final():
    r = GraphRunner()
    res = r.run("hello graph")
    assert isinstance(res, str)
    assert res.lower().startswith("final answer:")
