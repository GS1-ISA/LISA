from src.memory.router import MemoryRouter
from src.memory import KnowledgeGraphMemory
from src.retrieval import VectorIndex


def test_memory_router_detect_and_context_builds():
    kg = KnowledgeGraphMemory()
    kg.create_entity("ESG regulation", "topic", ["policy", "csrd"])
    idx = VectorIndex()
    idx.rebuild([
        ("doc1", "ESG regulation impacts reporting.", {}),
        ("doc2", "Tracing uses OpenTelemetry.", {}),
    ])
    r = MemoryRouter(kg, idx)
    ctype = r.route_store("Plan: owner: ops id:42", session_id="t")
    assert ctype in {"structured", "short_term", "long_term"}
    ctx = r.build_context("ESG regulation", k=3)
    assert ctx.snippets and any("ESG" in s or "KG:" in s for s in ctx.snippets)

