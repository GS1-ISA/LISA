import logging
from contextlib import contextmanager
import os

from .logging_conf import setup_logging
from .memory_store import KnowledgeGraphMemory
from .reasoning import SequentialReasoner
from .retrieval import VectorIndex
from .memory.router import MemoryRouter
from .memory.logs import MemoryEventLogger
from .utils.orch_loader import run_orchestrator_stub

setup_logging()
log = logging.getLogger("assistant")

try:
    from opentelemetry import trace

    _TRACER = trace.get_tracer("ISA_SuperApp.assistant")

    @contextmanager
    def _span(name: str):
        with _TRACER.start_as_current_span(name):
            yield

except Exception:
    @contextmanager
    def _span(name: str):
        yield


class AssistantOrchestrator:
    def __init__(
        self,
        memory: KnowledgeGraphMemory | None = None,
        reasoner: SequentialReasoner | None = None,
        retriever: VectorIndex | None = None,
    ):
        self.memory = memory or KnowledgeGraphMemory()
        self.reasoner = reasoner or SequentialReasoner()
        self.retriever = retriever or VectorIndex()
        self.mem_router = MemoryRouter(self.memory, self.retriever)
        self.mem_logger = MemoryEventLogger()

    def rebuild_index_from_memory(self):
        with _span("assistant.rebuild_index"):
            docs = []
            g = self.memory.dump_graph()
            for name, ent in g.get("entities", {}).items():
                text = name + " " + " ".join(ent.get("observations", [])[:5])
                docs.append((name, text, {"type": ent.get("type", "unknown")}))
            if docs:
                self.retriever.rebuild(docs)

    def ask(
        self, question: str, use_memory: bool = True, max_steps: int = 5, explain: bool = False
    ):
        with _span("assistant.ask"):
            # Optional orchestrator facades (feature flags)
            # Prefer LangGraph runner when enabled; else try stub
            if os.getenv("ISA_USE_LANGGRAPH_ORCH", "0") == "1":
                from .utils.orch_loader import run_orchestrator_graph

                final = run_orchestrator_graph(question)
                if final:
                    ans = final
                    idx = ans.lower().find("final answer:")
                    if idx >= 0:
                        ans = ans[idx + len("final answer:") :].strip()
                    return (ans, {"orchestrator_graph": True}) if explain else ans
            if os.getenv("ISA_USE_ORCHESTRATOR_STUB", "0") == "1":
                stub = run_orchestrator_stub(question)
                if stub:
                    ans = stub
                    idx = ans.lower().find("final answer:")
                    if idx >= 0:
                        ans = ans[idx + len("final answer:") :].strip()
                    return (ans, {"orchestrator_stub": True}) if explain else ans
            context = ""
            if use_memory:
                with _span("assistant.retrieve"):
                    routed = self.mem_router.build_context(question, k=5)
                    context = "\n".join(routed.snippets)
            with _span("assistant.reason"):
                res = self.reasoner.run(question, context=context, max_steps=max_steps)
            # Save event to memory log and adapters
            self.mem_router.route_store(f"Q: {question}\nA: {res.final_answer}", session_id="interactive")
            self.mem_logger.log("ask", session_id="interactive", content=question, meta={"context_len": len(context)})
        if explain:
            feats: dict[str, int] = {}
            for line in context.split("\n"):
                for tok in [x.lower() for x in line.split() if len(x) > 3][:20]:
                    feats[tok] = feats.get(tok, 0) + 1
            imp = sorted(feats.items(), key=lambda x: x[1], reverse=True)[:10]
            trace = "\n".join([f"Step {t.number}: {t.content}" for t in res.thoughts])
            return res.final_answer, {"trace": trace, "importance": imp}
            return res.final_answer

    def process_user_input(self, user_input: str, session_id: str) -> str:
        """Compatibility shim used by the /chat form endpoint.

        For now it simply routes to ask() without using the session id.
        """
        return self.ask(user_input, explain=False)
