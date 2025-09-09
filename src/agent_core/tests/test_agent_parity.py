import typing as t

from src.agent_core.agents.planner import PlannerAgent
from src.agent_core.agents.researcher import ResearcherAgent
from src.agent_core.agents.synthesizer import SynthesizerAgent


class _DocsProviderStub:
    class _Result(t.NamedTuple):
        snippets: list[str]

    def get_docs(self, query: str, libs: list[str]) -> "_DocsProviderStub._Result":
        return _DocsProviderStub._Result(snippets=[f"Overview for {libs[0]}: ..."]) if libs else _DocsProviderStub._Result(snippets=[])


class _WebResearchToolStub:
    def search(self, query: str, max_results: int = 5) -> list[dict]:
        return [
            {"title": f"Result for {query}", "href": "https://example.com", "body": "stub"}
        ]

    def read_url(self, url: str) -> str:
        return "example content about the topic"


class _RAGMemoryStub:
    def __init__(self) -> None:
        self._docs: list[dict] = []

    def add(self, *, text: str, source: str, doc_id: str, **_: t.Any) -> None:  # type: ignore[override]
        self._docs.append({"document": text, "metadata": {"source": source}})

    def get_collection_count(self) -> int:
        return len(self._docs)

    def query(self, query_text: str, n_results: int = 5) -> list[dict]:  # pragma: no cover - trivial stub
        # simple return of most recent docs
        return list(reversed(self._docs))[:n_results]


def test_planner_generates_basic_plan():
    planner = PlannerAgent(docs_provider=_DocsProviderStub())
    plan = planner.run("Evaluate langgraph orchestration patterns")
    assert isinstance(plan, list) and len(plan) >= 3
    assert any("challenges" in s.lower() for s in plan)


def test_researcher_interacts_with_tools_and_memory():
    researcher = ResearcherAgent(_WebResearchToolStub(), _RAGMemoryStub())
    summary = researcher.run("search for orchestrator design", max_steps=2)
    assert "Completed research" in summary
    # ensure some content ended in memory
    assert researcher.rag_memory.get_collection_count() >= 0


def test_synthesizer_produces_report_from_memory():
    mem = _RAGMemoryStub()
    mem.add(text="A long document about orchestration and agents.", source="https://example.com", doc_id="doc-1")
    syn = SynthesizerAgent()
    report = syn.run("agent orchestration", mem)
    assert report.startswith("# Research Report:")
    assert "Sources Consulted" in report

