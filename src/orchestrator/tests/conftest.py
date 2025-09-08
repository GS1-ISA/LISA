import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PKG_SRC = REPO / "packages" / "orchestrator" / "src"
sys.path.insert(0, str(PKG_SRC))
