#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


ROOT = Path.cwd()


def load_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def path_exists(rel: str) -> bool:
    p = ROOT / rel
    return p.exists()


def workflow_script_refs() -> List[Dict[str, str]]:
    issues = []
    for wf in (ROOT / ".github" / "workflows").glob("*.yml"):
        txt = load_text(wf)
        for m in re.finditer(r"python\s+([\w\-/\.]+\.py)", txt):
            rel = m.group(1)
            if not path_exists(rel):
                issues.append(
                    {
                        "type": "missing_script",
                        "workflow": str(wf),
                        "path": rel,
                        "suggestion": f"Create {rel} or update workflow step to correct path",
                    }
                )
    return issues


def dockerfile_copy_refs() -> List[Dict[str, str]]:
    issues = []
    for df in ROOT.rglob("Dockerfile"):
        txt = load_text(df)
        for m in re.finditer(r"^COPY\s+([^\s]+)\s+", txt, re.MULTILINE):
            src = m.group(1)
            # ignore wildcard/globs
            if "*" in src:
                continue
            rel = str((df.parent / src).relative_to(ROOT)) if not src.startswith("/") else src[1:]
            if not path_exists(rel):
                issues.append(
                    {
                        "type": "missing_copy_source",
                        "dockerfile": str(df),
                        "path": rel,
                        "suggestion": f"Add {rel} or adjust COPY path",
                    }
                )
    return issues


def python_import_refs() -> List[Dict[str, str]]:
    issues = []
    for py in (ROOT / "ISA_SuperApp" / "src").rglob("*.py"):
        txt = load_text(py)
        for m in re.finditer(r"(?:from|import)\s+src(?:\.|\s)([a-zA-Z0-9_\.]+)", txt):
            mod = m.group(1).strip()
            # candidate paths
            parts = mod.split(".")
            base = ROOT / "ISA_SuperApp" / "src" / "/".join(parts)
            candidates = [base.with_suffix(".py"), base / "__init__.py"]
            if not any(c.exists() for c in candidates):
                issues.append(
                    {
                        "type": "missing_module",
                        "source": str(py),
                        "module": f"src.{mod}",
                        "candidates": [str(c.relative_to(ROOT)) for c in candidates],
                        "suggestion": "Create module or fix import path",
                    }
                )
    return issues


def main() -> int:
    issues: List[Dict[str, str]] = []
    issues += workflow_script_refs()
    issues += dockerfile_copy_refs()
    issues += python_import_refs()

    out = ROOT / "docs" / "audit" / "coherence_issues.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"issues": issues}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out} (issues={len(issues)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
