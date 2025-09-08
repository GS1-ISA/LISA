from __future__ import annotations

import logging
import time
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

from src.tools.web_research import WebResearchTool
from src.agent_core.memory.rag_store import RAGMemory
from src.agent_core.agents.planner import PlannerAgent
from src.agent_core.agents.researcher import ResearcherAgent
from src.agent_core.agents.synthesizer import SynthesizerAgent
from src.orchestrator.research_graph import ResearchGraph
from src.docs_provider.context7 import get_provider as get_docs_provider


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="ISA Research API", version="0.1.0")


# Basic Prometheus metrics (low cardinality)
REQS = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "code"])
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 5),
    labelnames=("method", "endpoint"),
)


@app.middleware("http")
async def metrics_middleware(request, call_next):  # type: ignore[no-untyped-def]
    start = time.perf_counter()
    try:
        response = await call_next(request)
        code = getattr(response, "status_code", 500)
        return response
    finally:
        elapsed = time.perf_counter() - start
        endpoint = request.url.path
        method = request.method
        LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)
        REQS.labels(method=method, endpoint=endpoint, code=str(locals().get("code", 500))).inc()


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    """Simple healthcheck for container HEARTCHECK."""
    return "ok"


@app.get("/metrics")
def metrics() -> Response:
    """Prometheus scrape endpoint."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/research")
def research(query: str = Query(..., description="High-level research query")) -> JSONResponse:
    """Run the multi-agent research flow and return the final Markdown report."""
    logging.info("Setting up research components for API call")
    web_tool = WebResearchTool()
    rag_memory = RAGMemory()
    docs_provider = get_docs_provider()

    planner = PlannerAgent(docs_provider=docs_provider)
    researcher = ResearcherAgent(web_tool=web_tool, rag_memory=rag_memory)
    synthesizer = SynthesizerAgent()

    graph = ResearchGraph(
        planner=planner,
        researcher=researcher,
        synthesizer=synthesizer,
        rag_memory=rag_memory,
        docs_provider=docs_provider,
    )

    logging.info("Running research graph")
    result_md = graph.run(query)
    return JSONResponse({"query": query, "result_markdown": result_md})

