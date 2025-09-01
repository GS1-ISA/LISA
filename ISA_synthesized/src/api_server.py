import subprocess
import atexit
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .logging_conf import setup_logging
from .assistant import AssistantOrchestrator

# from .memory import ChatHistory # Removed as ChatHistory is not defined in src/memory.py
from .utils.path_utils import find_project_root

# Configure logging
setup_logging()
log = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="webui"), name="static")

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


# @app.get("/history/{session_id}") # Removed as ChatHistory is not defined in src/memory.py
# async def get_history(session_id: str):
#     history = ChatHistory(session_id)
#     return history.get_messages()

if __name__ == "__main__":
    start_uvicorn()
    atexit.register(cleanup_processes)
