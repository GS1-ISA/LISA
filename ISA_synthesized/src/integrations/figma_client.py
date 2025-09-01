import logging
import os
import re
from typing import Any, Dict, Optional, Tuple

import requests

log = logging.getLogger("figma_client")
FIGMA_API = "https://api.figma.com/v1"


def get_token() -> Optional[str]:
    return os.getenv("FIGMA_ACCESS_TOKEN") or os.getenv("FIGMA_TOKEN")


def extract_file_key_from_url(url: str) -> Optional[str]:
    m = re.search(r"figma\.com/(?:design|file)/([A-Za-z0-9]+)", url)
    return m.group(1) if m else None


def verify_token() -> Tuple[bool, str]:
    token = get_token()
    if not token:
        return False, "Missing FIGMA_ACCESS_TOKEN"
    try:
        r = requests.get(f"{FIGMA_API}/me", headers={"X-FIGMA-TOKEN": token}, timeout=30)
        if r.status_code == 200:
            me = r.json()
            return True, "Figma auth OK."
        return False, f"Figma /me failed: {r.status_code} {r.text[:200]}"
    except Exception as e:
        return False, f"Figma verification error: {e}"


def fetch_file_json(file_key: str) -> dict:
    token = get_token()
    if not token:
        raise RuntimeError("FIGMA_ACCESS_TOKEN missing")
    r = requests.get(f"{FIGMA_API}/files/{file_key}", headers={"X-FIGMA-TOKEN": token}, timeout=60)
    r.raise_for_status()
    return r.json()


def _rgba_to_css(rgba: Dict[str, Any]) -> str:
    r = rgba.get("r", 0) * 255
    g = rgba.get("g", 0) * 255
    b = rgba.get("b", 0) * 255
    a = rgba.get("a", 1)
    return f"rgba({int(r)},{int(g)},{int(b)},{a:.3f})"


def generate_css_tokens(file_json: dict) -> str:
    styles = file_json.get("styles", {})
    style_meta = {k: v for k, v in styles.items()}
    css_lines = [":root {", "  /* chart tokens */"]
    seen = set()

    def add_var(name: str, value: str):
        import re

        key = re.sub(r"[^a-z0-9\-]", "-", name.lower())
        key = re.sub(r"-+", "-", key).strip("-")
        var = f"  --{key}: {value};"
        if var not in seen:
            css_lines.append(var)
            seen.add(var)

    def walk(node):
        if not isinstance(node, dict):
            return
        fills = node.get("fills") or []
        style_id = node.get("styles", {}).get("fill")
        if style_id and style_id in style_meta and fills:
            st = style_meta[style_id]
            name = st.get("name", "color")
            for f in fills:
                if f.get("type") == "SOLID" and f.get("color"):
                    add_var(f"color-{name}", _rgba_to_css(f["color"]))
                    break
        if node.get("type") == "TEXT":
            style_id = node.get("styles", {}).get("text")
            if style_id and style_id in style_meta:
                st = style_meta[style_id]
                name = st.get("name", "text")
                style = node.get("style", {})
                fs = style.get("fontSize")
                lh = style.get("lineHeightPx")
                if fs:
                    add_var(f"font-size-{name}", f"{fs}px")
                if lh:
                    add_var(f"line-height-{name}", f"{lh}px")
        for child in node.get("children", []) or []:
            walk(child)

    doc = file_json.get("document") or {}
    walk(doc)
    defaults = ["#2563eb", "#16a34a", "#f59e0b", "#ef4444", "#8b5cf6", "#14b8a6", "#f97316"]
    for i, c in enumerate(defaults, start=1):
        add_var(f"chart-color-{i}", c)
    add_var("semantic-positive", "#16a34a")
    add_var("semantic-warning", "#f59e0b")
    add_var("semantic-danger", "#ef4444")
    css_lines.append("}")
    return "\n".join(css_lines)


def write_tokens_css(path: str, css: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(css)
