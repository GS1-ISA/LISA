import logging
from .logging_conf import setup_logging
from .memory import KnowledgeGraphMemory
from .reasoning import SequentialReasoner
from .retrieval import VectorIndex

setup_logging()
log = logging.getLogger("assistant")


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

    def rebuild_index_from_memory(self):
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
        context = ""
        if use_memory:
            terms = {t.strip(",.;:").lower() for t in question.split() if len(t) > 3}
            snippets = []
            for term in list(terms)[:8]:
                for ent in self.memory.query(term):
                    snippets.append(f"[{ent.name} ({ent.type})] " + "; ".join(ent.observations[:2]))
            try:
                vec_hits = self.retriever.search(question, k=5)
                for h in vec_hits:
                    snippets.append(
                        f"[SIM:{h.get('id')}] score={h.get('score'):.3f} :: "
                        + h.get("text", "")[:200]
                    )
            except Exception as e:
                log.debug("Vector search failed: %s", e)
            context = "\n".join(snippets[:10])
        res = self.reasoner.run(question, context=context, max_steps=max_steps)
        if explain:
            feats = {}
            for line in context.split("\n"):
                for tok in [x.lower() for x in line.split() if len(x) > 3][:20]:
                    feats[tok] = feats.get(tok, 0) + 1
            imp = sorted(feats.items(), key=lambda x: x[1], reverse=True)[:10]
            trace = "\n".join([f"Step {t.number}: {t.content}" for t in res.thoughts])
            return res.final_answer, {"trace": trace, "importance": imp}
        return res.final_answer
