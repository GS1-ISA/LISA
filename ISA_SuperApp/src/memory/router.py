from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from .adapters.base import MemoryRecord
from .adapters.langchain_adapter import LangChainMemoryAdapter
from .adapters.structured_adapter import StructuredMemoryAdapter
from .adapters.stubs_external import (
    AMemAdapter,
    AwsAugmentedAdapter,
    McpAdapter,
    MemEngineAdapter,
    ZepAdapter,
)
from .logs import MemoryEventLogger
from ..retrieval import VectorIndex
from ..memory import KnowledgeGraphMemory


@dataclass
class RoutedContext:
    context_type: str  # short_term | long_term | structured
    snippets: List[str]


class MemoryRouter:
    def __init__(self, kg: KnowledgeGraphMemory, index: VectorIndex, log_dir: str | None = None) -> None:
        self.kg = kg
        self.index = index
        self.logger = MemoryEventLogger(log_dir)
        # Instantiate adapters (optional/backfilled)
        enabled = os.getenv("ISA_MEMORY_ADAPTERS", "langchain,structured,memengine,zep,amem,aws,mcp").lower().split(",")
        self.langchain = LangChainMemoryAdapter() if "langchain" in enabled else None
        self.structured = StructuredMemoryAdapter() if "structured" in enabled else None
        self.memengine = MemEngineAdapter("memengine") if "memengine" in enabled else None
        self.zep = ZepAdapter("zep") if "zep" in enabled else None
        self.amem = AMemAdapter("amem") if "amem" in enabled else None
        self.aws = AwsAugmentedAdapter("aws") if "aws" in enabled else None
        self.mcp = McpAdapter("mcp") if "mcp" in enabled else None

    def detect_context_type(self, text: str) -> str:
        # Simple heuristic: short if length<160; structured if contains key:value-like; else long
        if len(text) < 160:
            return "short_term"
        if ":" in text and any(k in text.lower() for k in ("id", "owner", "policy")):
            return "structured"
        return "long_term"

    def route_store(self, user_text: str, session_id: str) -> str:
        ctype = self.detect_context_type(user_text)
        rec = MemoryRecord(kind=ctype, content=user_text, meta={"session_id": session_id})
        # Store to available adapters
        for ad in (self.langchain, self.structured, self.memengine, self.zep, self.amem, self.aws, self.mcp):
            if ad is not None:
                ad.store(rec)
        self.logger.log("store", session_id, user_text, {"context_type": ctype})
        return ctype

    def build_context(self, question: str, k: int = 5) -> RoutedContext:
        ctype = self.detect_context_type(question)
        snippets: list[str] = []
        # KG hits
        for ent in self.kg.query(question):
            snippets.append(f"[KG:{ent.name}] " + "; ".join(ent.observations[:2]))
        # Vector hits
        try:
            for h in self.index.search(question, k=k):
                snippets.append(f"[VEC:{h.get('id')}] {h.get('text','')[:160]}")
        except Exception:
            pass
        # Adapter recalls
        if self.langchain:
            snippets.extend(self.langchain.retrieve(question, k=3))
        if self.structured:
            snippets.extend(self.structured.retrieve(question, k=3))
        self.logger.log("retrieve", session_id="-", content=question, meta={"context_type": ctype, "snippets": len(snippets)})
        return RoutedContext(context_type=ctype, snippets=snippets[:10])
