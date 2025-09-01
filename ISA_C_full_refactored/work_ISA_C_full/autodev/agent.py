from __future__ import annotations

import json
import os
import re
from typing import Any

from .llm_providers import LLMClient
from .markdown_io import extract_tasks
from .state import load_state, save_state, tick_cost


def read(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def apply_patches(patches):
    for p in patches:
        rel = p.get("path", "unknown.txt").replace("/", "_")
        text = p.get("unified_diff", "")
        write_file(f"patches/{rel}.diff", text)


def replace_first_open_checkbox(md_text: str) -> str:
    return re.sub(r"- \[ \] ", "- [x] ", md_text, count=1)


def run_once() -> dict[str, Any]:
    state = load_state()
    gem = read("Gemini.md")
    roadmap = read("roadmap.md")
    tasks = extract_tasks(roadmap)
    next_task = tasks[0][0] if tasks else "No open tasks"
    sys = gem
    user = json.dumps(
        {"roadmap_excerpt": roadmap[:4000], "task": next_task, "state": state}, ensure_ascii=False
    )
    llm = LLMClient()
    result = llm.complete_json(system=sys, user=user)
    for f in result.get("files", []):
        write_file(f.get("path", "out/output.txt"), f.get("content", ""))
    apply_patches(result.get("patches", []))
    decision = result.get("decision", "plan")
    if decision in ("implement", "reflect") and tasks:
        new_rm = replace_first_open_checkbox(roadmap)
        write_file("roadmap.md", new_rm)
    os.makedirs("logs", exist_ok=True)
    write_file("logs/run.json", json.dumps(result, indent=2, ensure_ascii=False))
    tick_cost(state, 0.00)
    state["last_task"] = next_task
    save_state(state)
    return result
