import atexit
import logging
import subprocess
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Form, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from .assistant import AssistantOrchestrator
from .logging_conf import setup_logging

# from .memory import ChatHistory # Removed as ChatHistory is not defined in src/memory.py
# from .utils.path_utils import find_project_root  # unused; removed to avoid import error
from .nesy.lnn_validator import validate_record
from .utils.otel import init_tracing

# Configure logging
setup_logging()
log = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Resolve web UI directory relative to this file to avoid CWD issues
_BASE_DIR = Path(__file__).resolve().parents[1]
_WEBUI_DIR = _BASE_DIR / "webui"
if _WEBUI_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_WEBUI_DIR)), name="static")
else:
    log.warning("webui directory not found at %s; skipping static mount", _WEBUI_DIR)

# Optional tracing (OpenTelemetry) — controlled by OTEL_ENABLED=1
init_tracing(app)

# Initialize Jinja2 templates (optional)
from typing import Optional
templates: Optional[Jinja2Templates]
try:
    templates = Jinja2Templates(directory=str(_WEBUI_DIR if _WEBUI_DIR.exists() else _BASE_DIR))
except Exception:
    templates = None  # UI routes will provide minimal responses if needed

# Initialize orchestrator
orchestrator = AssistantOrchestrator()

uvicorn_process = None


def start_uvicorn():
    global uvicorn_process
    host = "127.0.0.1"
    port = 8787
    command = ["uvicorn", "src.api_server:app", f"--host={host}", f"--port={port}", "--reload"]
    uvicorn_process = subprocess.Popen(command)
    log.info(f"FastAPI server started at http://{host}:{port}")


def cleanup_processes():
    if uvicorn_process:
        uvicorn_process.terminate()
        uvicorn_process.wait()


# --- Routes ---


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/ui/users")


@app.get("/ui/users", response_class=HTMLResponse)
async def user_interface(request: Request):
    if templates:
        return templates.TemplateResponse("users.html", {"request": request})
    return HTMLResponse("<html><body><h1>Users</h1></body></html>")


@app.get("/ui/admin", response_class=HTMLResponse)
async def admin_interface(request: Request):
    if templates:
        return templates.TemplateResponse("admin.html", {"request": request})
    return HTMLResponse("<html><body><h1>Admin</h1></body></html>")


@app.post("/chat")
async def chat(request: Request, user_input: str = Form(...), session_id: str = Form(...)):
    response = orchestrator.process_user_input(user_input, session_id)
    return {"response": response}


class AskPayload(BaseModel):
    question: str
    explain: bool | None = False


@app.post("/ask")
async def ask(payload: AskPayload):
    """Compatibility endpoint used by integration tests.

    Accepts a JSON body with {question, explain} and returns an answer (and optionally explanation).
    """
    if payload.explain:
        answer, meta = orchestrator.ask(payload.question, explain=True)
        return {"answer": answer, "meta": meta}
    return {"answer": orchestrator.ask(payload.question, explain=False)}


@app.post("/validate")
async def validate(record: dict):
    """Validate a record against NeSy rules (MVP).

    Returns a list of violations with rule_id, message, and path.
    """
    violations = validate_record(record)
    return {"violations": [asdict(v) for v in violations]}


# --- Minimal Admin/Search/Doc endpoints to satisfy system tests ---


class IngestPayload(BaseModel):
    """Optional ingest payload.

    For MVP tests we keep it free-form and optional.
    """
    seeds: list[str] | None = None


@app.post("/admin/ingest")
async def admin_ingest(payload: IngestPayload | None = None):
    """Seed a tiny in-memory knowledge set for demos/tests.

    Idempotent and safe: it only adds if missing.
    """
    seeds = payload.seeds if payload and payload.seeds else [
        "ESG regulation",
        "CSRD directive",
        "OpenTelemetry tracing",
    ]
    for term in seeds:
        orchestrator.memory.create_entity(term, type="topic")
        orchestrator.memory.add_observations(
            term,
            [
                f"seed:{term}",
                "auto-ingested for tests",
            ],
        )
    return {"status": "ok", "added": len(seeds)}


@app.post("/admin/reindex")
async def admin_reindex():
    orchestrator.rebuild_index_from_memory()
    return {"status": "ok"}


class SearchPayload(BaseModel):
    query: str
    k: int | None = 5


@app.post("/search")
async def search(payload: SearchPayload):
    q = payload.query
    k = payload.k or 5
    try:
        hits = orchestrator.retriever.search(q, k=k)
    except Exception:
        hits = []
    return {"query": q, "hits": hits}


class DocGenPayload(BaseModel):
    title: str
    outline: str | None = None


@app.post("/doc/generate")
async def doc_generate(payload: DocGenPayload):
    title = payload.title.strip() or "Untitled"
    sections = [s.strip() for s in (payload.outline or "").split(";") if s.strip()]
    body = [f"# {title}", ""]
    for s in sections:
        body.append(f"## {s}")
        body.append("")
        body.append("TBD.")
        body.append("")
    md = "\n".join(body).rstrip() + "\n"
    return {"markdown": md}


# --- Observability: Metrics & Correlation IDs ---
import time
import uuid

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=("method", "path", "status"),
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    labelnames=("method", "path", "status"),
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        response: Response = await call_next(request)
        status = str(response.status_code)
    except Exception:
        status = "500"
        raise
    finally:
        duration = time.perf_counter() - start
        path = request.url.path
        method = request.method
        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, path=path, status=status).observe(duration)
    # Ensure request ID is present for correlation
    response.headers.setdefault("X-Request-ID", req_id)
    return response


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


# @app.get("/history/{session_id}") # Removed as ChatHistory is not defined in src/memory.py
# async def get_history(session_id: str):
#     history = ChatHistory(session_id)
#     return history.get_messages()

if __name__ == "__main__":
    start_uvicorn()
    atexit.register(cleanup_processes)
