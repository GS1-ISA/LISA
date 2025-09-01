import atexit
import logging
import subprocess
from dataclasses import asdict

from fastapi import FastAPI, Form, Request
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
app.mount("/static", StaticFiles(directory="webui"), name="static")

# Optional tracing (OpenTelemetry) — controlled by OTEL_ENABLED=1
init_tracing(app)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="webui")

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
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/ui/admin", response_class=HTMLResponse)
async def admin_interface(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.post("/chat")
async def chat(request: Request, user_input: str = Form(...), session_id: str = Form(...)):
    response = orchestrator.process_user_input(user_input, session_id)
    return {"response": response}


@app.post("/validate")
async def validate(record: dict):
    """Validate a record against NeSy rules (MVP).

    Returns a list of violations with rule_id, message, and path.
    """
    violations = validate_record(record)
    return {"violations": [asdict(v) for v in violations]}


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
