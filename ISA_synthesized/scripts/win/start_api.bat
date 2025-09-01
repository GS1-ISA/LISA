@echo off
setlocal
cd /d %~dp0\..\..
if not exist .venv (
  py -3 -m venv .venv
)
call .\.venv\Scripts\Activate.bat
pip install -r requirements.txt >NUL
set ISA_TEST_MODE=0
uvicorn src.api_server:app --host 127.0.0.1 --port 8787
