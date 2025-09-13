#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent


FILE_EXTS = {".py", ".md", ".yml", ".yaml", ".json", ".toml"}
META_DIR_RX = re.compile(
    r"(ai|meta|agent|gpt|llm|auto|bot|orchestrat|reflect|memory|embed|vector|knowledge|graph|rule|dsl|c4|structurizr|rag|research|audit|ops)",
    re.IGNORECASE,
)
META_RX = re.compile(
    r"(chatgpt|gpt|llm|agent|ai-|meta-|memory|embedding|vector|knowledge.*graph|dsl|c4|structurizr|orchestrat|autonomous|self.*evolv|self.*improv|north.*star|drift|bloat|guard.*rail|token.*budget|idempoten)",
    re.IGNORECASE,
)

CONCEPTS: List[Tuple[str, str]] = [
    ("Agent", r"agent"),
    ("Memory", r"memory"),
    ("Embedding", r"embed"),
    ("Drift", r"drift"),
    ("Bloat", r"bloat"),
    ("Guard-rail", r"guard.*rail"),
    ("DSL", r"dsl"),
    ("C4", r"c4|structurizr"),
    ("Orchestration", r"orchestrat"),
    ("Self-improve", r"self.*improv|self.*evolv"),
]


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def list_meta_dirs(max_depth: int = 3) -> List[Path]:
    out: List[Path] = []
    for d, dirs, files in os.walk(ROOT):
        p = Path(d)
        rel = p.relative_to(ROOT)
        depth = len(rel.parts)
        if depth == 0:
            continue
        if depth <= max_depth and META_DIR_RX.search(str(rel)):
            out.append(rel)
    return sorted(set(out))


def list_candidate_files() -> List[Path]:
    out: List[Path] = []
    for d, dirs, files in os.walk(ROOT):
        # skip .git and build dirs
        if "/.git" in d or d.endswith("/_build"):
            continue
        for name in files:
            p = Path(d) / name
            if p.suffix.lower() in FILE_EXTS:
                out.append(p.relative_to(ROOT))
    return out


def grep_hits(text: str, rx: re.Pattern[str]) -> Tuple[int, Tuple[int, int]]:
    hits = list(rx.finditer(text))
    if not hits:
        return 0, (0, 0)
    h = hits[0]
    # line numbers
    pre = text[: h.start()]
    line = pre.count("\n") + 1
    return len(hits), (max(1, line - 2), line + 2)


def commit_date_for(path: Path) -> str:
    try:
        res = subprocess.run(
            ["git", "log", "-n", "1", "--date=short", "--pretty=%ad", str(path)],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=True,
        )
        return res.stdout.strip() or "1970-01-01"
    except Exception:
        return "1970-01-01"


def build_inventory() -> Tuple[str, List[Path], List[Path]]:
    now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    meta_dirs = list_meta_dirs()
    files = list_candidate_files()
    # Filter meta files by keyword
    meta_files = []
    for p in files:
        text = read_text(ROOT / p)
        if META_RX.search(text):
            meta_files.append(p)

    lines: List[str] = []
    lines.append(f"# Meta-Inventory – generated on {now}")
    lines.append("")
    # Section 1: Folders
    lines.append("## 1. Meta-Folders")
    lines.append("| Folder | Depth | File Count | Human Description |")
    lines.append("|---|---:|---:|---|")
    for rel in meta_dirs:
        depth = len(rel.parts)
        fcount = sum(1 for _ in (ROOT / rel).rglob("*") if _.is_file())
        desc = ",".join(list(map(str, list((ROOT / rel).glob("*"))[:5])))
        lines.append(
            f"| {rel} | {depth} | {fcount} | Files: {Path(desc).name if desc else ''} |"
        )
    lines.append("")

    # Section 2: Files
    lines.append("## 2. Meta-Files")
    lines.append(
        "| File | SHA256 | Lines | Keyword Hits | Excerpt Proving Implementation |"
    )
    lines.append("|---|---|---:|---:|---|")
    for p in meta_files:
        text = read_text(ROOT / p)
        hcount, (lo, hi) = grep_hits(text, META_RX)
        excerpt = " ".join(text.splitlines()[lo - 1 : hi])[:200].replace("|", "\|")
        sha = hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()
        nlines = text.count("\n") + 1
        lines.append(f"| {p} | {sha} | {nlines} | {hcount} | {excerpt} |")
    lines.append("")

    # Section 3: Meta-Commits (last 20)
    lines.append("## 3. Meta-Commits (last 20)")
    lines.append("| Hash | Date | Subject |")
    lines.append("|---|---|---|")
    try:
        res = subprocess.run(
            [
                "bash",
                "-lc",
                "git log --date=short --pretty=format:'%h|%ad|%s' --all | grep -Ei '(ai|meta|agent|gpt|llm|automat|orchestrat|memory|embed|drift|bloat)' | head -20",
            ],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        for line in res.stdout.splitlines():
            parts = line.split("|")
            if len(parts) >= 3:
                h, d, s = parts[0], parts[1], "|".join(parts[2:]).replace("|", "\|")
                lines.append(f"| {h} | {d} | {s} |")
    except Exception:
        pass
    lines.append("")

    # Section 4: Meta-Dependencies (requirements*.txt)
    lines.append("## 4. Meta-Dependencies")
    lines.append("| File | Package | Version |")
    lines.append("|---|---|---|")
    dep_rx = re.compile(
        r"(langchain|llama|openai|anthropic|transformers|torch|tensorflow|embed|vector|chromadb|faiss|weaviate|qdrant|pgvector|milvus|structurizr|c4|dsl|guard|ai-|meta-|memory|drift|bloat)",
        re.IGNORECASE,
    )
    for rf in sorted(
        list(ROOT.glob("requirements*.txt"))
        + list(ROOT.glob("ISA_SuperApp/etl/requirements.txt"))
    ):
        for line in read_text(rf).splitlines():
            if dep_rx.search(line):
                clean = re.sub(r"\s*#.*$", "", line)
                name = re.split(r"[<>=!~;\[]", clean)[0].strip()
                ver = clean[len(name) :].strip() or "(unspecified)"
                lines.append(f"| {rf.relative_to(ROOT)} | {name} | {ver} |")
    lines.append("")

    # Section 5: CI/CD Integration (workflows mentioning meta dirs)
    lines.append("## 5. Meta-CI/CD Integration")
    lines.append("| Workflow/File | Note | ")
    lines.append("|---|---|")
    for wf in ROOT.glob(".github/workflows/*.yml"):
        text = read_text(wf)
        if META_DIR_RX.search(text) or META_RX.search(text):
            lines.append(f"| {wf.relative_to(ROOT)} | mentions meta keywords |")
    lines.append("")

    # Section 6: Runtime services (placeholder)
    lines.append("## 6. Meta-Runtime Services")
    lines.append("| Compose/Helm Service | Image | Meta-Related Command |")
    lines.append("|---|---|---|")
    lines.append("")

    # Section 7: Conceptual Taxonomy
    lines.append("## 7. Conceptual Taxonomy (auto-generated)")
    for fam, rx in CONCEPTS:
        dircnt = sum(1 for d in meta_dirs if re.search(rx, str(d), re.IGNORECASE))
        filecnt = 0
        for p in meta_files:
            t = read_text(ROOT / p)
            if re.search(rx, t, re.IGNORECASE):
                filecnt += 1
        depcnt = 0
        for rf in ROOT.glob("requirements*.txt"):
            if re.search(rx, read_text(rf), re.IGNORECASE):
                depcnt += 1
        cicnt = 0
        for wf in ROOT.glob(".github/workflows/*.yml"):
            if re.search(rx, read_text(wf), re.IGNORECASE):
                cicnt += 1
        risk = ""
        if dircnt == 1:
            risk = "SINGLETON"
        if dircnt >= 3:
            risk = "DUPLICATE"
        promised = (
            re.search(rx, read_text(ROOT / "docs/AI_PROJECT_CHARTER.md"), re.IGNORECASE)
            is not None
        )
        if dircnt == 0 and promised:
            risk = "MISSING"
        lines.append(
            f"- {fam}: folders={dircnt}, files={filecnt}, deps={depcnt}, ci_steps={cicnt}, Risk={risk}"
        )
    lines.append("")

    # Section 8: Redundancy Matrix
    lines.append("## 8. Redundancy Matrix")
    heads = [c for c, _ in CONCEPTS]
    pats = [re.compile(rx, re.IGNORECASE) for _, rx in CONCEPTS]
    # Precompute file matches per concept
    per = []
    for rx in pats:
        matched = set()
        for p in meta_files:
            if rx.search(read_text(ROOT / p)):
                matched.add(str(p))
        per.append(matched)
    lines.append("| Concept " + "| " + " | ".join(heads) + " |")
    lines.append("|---" + "|---:" * len(heads) + "|")
    for i, ci in enumerate(heads):
        row = [ci]
        for j in range(len(heads)):
            inter = len(per[i] & per[j])
            cell = f"HOTSPOT:{inter}" if inter >= 15 else str(inter)
            row.append(cell)
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Section 9: Drift Indicator
    lines.append("## 9. Drift Indicator")
    last_hash = "N/A"
    last_date = "1970-01-01"
    for p in meta_files:
        d = commit_date_for(p)
        if d > last_date:
            last_date = d
    try:
        res = subprocess.run(
            ["git", "log", "-n", "1", "--pretty=%h", "--", str(meta_files[-1])],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        last_hash = res.stdout.strip() or "N/A"
    except Exception:
        pass
    lines.append(f"- Last commit touching any meta-file: {last_hash} {last_date}")
    try:
        last_epoch = int(dt.datetime.strptime(last_date, "%Y-%m-%d").timestamp())
    except Exception:
        last_epoch = 0
    days = (
        int((dt.datetime.utcnow().timestamp() - last_epoch) / 86400)
        if last_epoch
        else 0
    )
    lines.append(f"- Days since last meta-change: {days}")
    if days > 30:
        lines.append("- META-STALENESS WARNING")
    lines.append("")

    # Section 10: Exit Signature
    lines.append("## 10. Exit Signature")
    content = "\n".join(lines)
    sh = sha256_text(content)
    lines.append(f"- SHA256 of this inventory file: {sh}")
    lines.append("- Agent session UUID: (n/a)")
    lines.append(
        "- Human reviewer action: **NONE** – this file is read-only reconnaissance."
    )
    return "\n".join(lines), meta_dirs, meta_files


def build_risk_xray(meta_dirs: List[Path], meta_files: List[Path]) -> str:
    rows: List[str] = []
    files = [ROOT / p for p in meta_files]
    tests = [p for p in files if "test" in str(p) or "tests" in str(p)]
    now = dt.datetime.utcnow().timestamp()
    rows.append(
        "| Concept | Risk Score | Evidence Snippet (≤ 120 chars) | Recommended Owner | Max Acceptable Age (days) |"
    )
    rows.append("|---|---:|---|---|---:|")
    for fam, rx in CONCEPTS:
        rxf = re.compile(rx, re.IGNORECASE)
        dircnt = sum(1 for d in meta_dirs if rxf.search(str(d)))
        # risk flags
        score = 0
        riskflag = ""
        if dircnt >= 3:
            riskflag = "DUPLICATE"
            score += max(0, dircnt - 2)
        elif dircnt == 1:
            riskflag = "SINGLETON"
        elif dircnt == 0:
            if re.search(
                rx, read_text(ROOT / "docs/AI_PROJECT_CHARTER.md"), re.IGNORECASE
            ):
                riskflag = "MISSING"
                score += 2
        if riskflag == "SINGLETON":
            covered = any(rxf.search(read_text(t)) for t in tests)
            if not covered:
                score += 1
        # hotspot
        matched = [p for p in files if rxf.search(read_text(p))]
        max_age = 0
        for p in matched:
            try:
                m = p.stat().st_mtime
                age = int((now - m) / 86400)
                max_age = max(max_age, age)
            except Exception:
                pass
        if max_age > 30:
            score += 2
        elif max_age > 14:
            score += 1
        # simple hotspot bonus if there are many matched files across repo
        if len(matched) >= 15:
            score += 1
        ev = f"{fam}: folders={dircnt}, files={len(matched)}, Risk={riskflag or ''}; max_age={max_age}d"[
            :120
        ]
        owner = {
            "Memory": "data-engineer",
            "Embedding": "data-science",
        }.get(fam, "eng-lead")
        rows.append(f"| {fam} | {score} | {ev} | {owner} | 30 |")
    return "\n".join(rows) + "\n"


def main() -> int:
    inv, meta_dirs, meta_files = build_inventory()
    (ROOT / "meta_inventory.md").write_text(inv, encoding="utf-8")
    risk = build_risk_xray(meta_dirs, meta_files)
    (ROOT / "meta_risk_xray.md").write_text(risk, encoding="utf-8")
    print("meta_inventory.md and meta_risk_xray.md generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
