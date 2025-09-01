Param()
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")
if (-Not (Test-Path ".venv")) { py -3 -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt | Out-Null
$env:ISA_TEST_MODE="1"
try {
  pytest -q
} catch {
  python tests\run_tests.py
}
