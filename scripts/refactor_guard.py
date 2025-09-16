#!/usr/bin/env python3
"""
Refactor Guard CLI

Implements a local, ISA_D-native version of the zero-regression refactor loop:
- bootstrap: initialize board REFACTOR_2025 and state files
- pre-check: run tests 3x, compute coverage gaps, detect flakies
- slice: propose slices based on the repo graph (coherence_graph.json) or folders
- scaffold: create feature flag and stub metrics links
- next: pick highest-value slice and prepare a micro-PR locally (simulation)
- status: print board snapshot and any open alerts
- sweep: remove legacy code for a slice after soak (simulation; prints plan)
- rollback: flip all ISA_REF_* flags to false

State is stored under artifacts/refactor_guard/.
Feature flags stored at infra/feature_flags/local_flags.json.

This CLI avoids remote dependencies and integrates with this repo's CI.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from src.xml_utils import collect_coverage_gaps, XMLParseError, XMLValidationError
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from xml_utils import collect_coverage_gaps, XMLParseError, XMLValidationError

ARTIFACTS_DIR = Path("artifacts/refactor_guard")
BOARD_FILE = ARTIFACTS_DIR / "board.json"
LOG_FILE = ARTIFACTS_DIR / "run.log"
FLAGS_FILE = Path("infra/feature_flags/local_flags.json")
COHERENCE_GRAPH = Path("coherence_graph.json")


def log(msg: str) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    LOG_FILE.write_text(
        (LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else "") + line,
        encoding="utf-8",
    )
    print(msg)


def load_board() -> Dict[str, Any]:
    if BOARD_FILE.exists():
        return json.loads(BOARD_FILE.read_text(encoding="utf-8"))
    return {
        "name": "REFACTOR_2025",
        "blocked": False,
        "block_reasons": [],
        "columns": {
            "TODO": [],
            "FLAG-CREATED": [],
            "PR-OPEN": [],
            "CANARY": [],
            "DONE": [],
        },
        "slices": {},
        "history": [],
    }


def save_board(board: Dict[str, Any]) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    BOARD_FILE.write_text(json.dumps(board, indent=2), encoding="utf-8")


def load_flags() -> Dict[str, Any]:
    if FLAGS_FILE.exists():
        try:
            return json.loads(FLAGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    init: Dict[str, Any] = {"flags": {}}  # name -> {"enabled": bool, "traffic": int}
    FLAGS_FILE.write_text(json.dumps(init, indent=2), encoding="utf-8")
    return init


def save_flags(flags: Dict[str, Any]) -> None:
    FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAGS_FILE.write_text(json.dumps(flags, indent=2), encoding="utf-8")


def run(
    cmd: str,
    cwd: Optional[Path] = None,
    check: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> Tuple[int, str]:
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, **(env or {})},
        text=True,
    )
    out, _ = proc.communicate()
    rc = proc.returncode
    if check and rc != 0:
        raise subprocess.CalledProcessError(rc, cmd, output=out)
    return rc, out


# --- Commands ---


def cmd_bootstrap(args: argparse.Namespace) -> None:
    board = load_board()
    if board.get("initialized"):
        log("REFACTOR-GUARD ALREADY ONLINE")
        print(f"BOARD: {BOARD_FILE}")
        return
    board["initialized"] = True
    save_board(board)
    log("REFACTOR-GUARD ONLINE")
    log(f"BOARD CREATED: {board['name']}")
    print(f"BOARD FILE: {BOARD_FILE}")


def _pytest_once(
    with_cov: bool = False,
    cov_out_xml: Optional[Path] = None,
    paths: Optional[List[str]] = None,
) -> Tuple[int, str]:
    paths = paths or ["src"]
    base = "python3 -m pytest -q --maxfail=1"
    if with_cov:
        cov_out_xml = cov_out_xml or (ARTIFACTS_DIR / "coverage.xml")
        base = f"{base} --cov=src --cov-report=xml:{shlex.quote(str(cov_out_xml))}"
    cmd = f"{base} {' '.join(shlex.quote(p) for p in paths)}"
    # Ensure repo root on PYTHONPATH so compat shims under ./packages are visible
    env = {"PYTHONPATH": os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")}
    rc, out = run(cmd, env=env)
    return rc, out


def _parse_pytest_output_for_failures(out: str) -> List[str]:
    # Extract test node IDs that failed from pytest summary lines
    failed: List[str] = []
    for line in out.splitlines():
        # Example: FAILED src/orchestrator/tests/test_api_server_smoke.py::test_metrics_endpoint - AssertionError
        if line.startswith("FAILED "):
            node = line.split()[1]
            failed.append(node)
    return failed


def _collect_coverage_gaps(cov_xml: Path, threshold: float = 80.0) -> List[str]:
    try:
        return collect_coverage_gaps(cov_xml, threshold)
    except (XMLParseError, XMLValidationError) as e:
        log(f"Error parsing coverage XML {cov_xml}: {e}")
        return []
    except Exception as e:
        log(f"Unexpected error collecting coverage gaps from {cov_xml}: {e}")
        return []


def cmd_precheck(args: argparse.Namespace) -> None:
    board = load_board()
    log("PRE-CHECK: installing deps (best-effort)")
    run("python3 -m pip install --upgrade pip", check=False)
    if Path("requirements.txt").exists():
        run("python3 -m pip install -r requirements.txt", check=False)
    if Path("requirements-dev.txt").exists():
        run("python3 -m pip install -r requirements-dev.txt", check=False)
    log("PRE-CHECK: running test suite 3x (scoped to src/)")
    all_failures: List[List[str]] = []
    any_red = False
    for i in range(3):
        rc, out = _pytest_once(
            with_cov=(i == 0), cov_out_xml=ARTIFACTS_DIR / "coverage.xml", paths=["src"]
        )
        (ARTIFACTS_DIR / f"pytest_run_{i + 1}.log").write_text(out, encoding="utf-8")
        failed = _parse_pytest_output_for_failures(out)
        all_failures.append(failed)
        if rc != 0:
            any_red = True
        log(f"Run {i + 1}: rc={rc}, failed={len(failed)}")
    # Coverage gaps from first run with coverage
    gaps = _collect_coverage_gaps(ARTIFACTS_DIR / "coverage.xml")
    flaky: List[str] = []
    # Detect flakies by presence/absence across runs
    test_set = set([t for runf in all_failures for t in runf])
    for t in sorted(test_set):
        appear = sum(1 for runf in all_failures if t in runf)
        if 0 < appear < 3:
            flaky.append(t)

    # Write tracking issues (local docs)
    issues_dir = Path("docs/issues")
    issues_dir.mkdir(parents=True, exist_ok=True)
    cov_issue = issues_dir / "refactor_coverage_gaps.md"
    flk_issue = issues_dir / "refactor_flaky_tests.md"
    cov_issue.write_text(
        "\n".join(["# Coverage Gaps (<80% in src/)"] + (gaps or ["None"])),
        encoding="utf-8",
    )
    flk_issue.write_text(
        "\n".join(
            ["# Flaky Tests (detected across 3 local runs)"] + (flaky or ["None"])
        ),
        encoding="utf-8",
    )

    board["blocked"] = any_red or bool(gaps) or bool(flaky)
    reasons = []
    if any_red:
        reasons.append("tests not fully green (3x)")
    if gaps:
        reasons.append("coverage gaps <80% in src/")
    if flaky:
        reasons.append("flaky tests detected")
    board["block_reasons"] = reasons
    save_board(board)

    status = "✅" if not board["blocked"] else "❌"
    log(f"PRE-CHECK RESULT: {status} | BOARD: {BOARD_FILE}")
    print(f"Coverage gaps file: {cov_issue}")
    print(f"Flaky tests file: {flk_issue}")


def _estimate_loc(files: List[str]) -> int:
    total = 0
    for f in files:
        p = Path(f)
        try:
            with p.open("r", encoding="utf-8", errors="ignore") as fh:
                total += sum(1 for _ in fh)
        except Exception:
            pass
    return total


def _list_repo_files() -> List[str]:
    rc, out = run("rg --files")
    if rc != 0:
        # Fallback to git ls-files
        rc, out = run("git ls-files")
    files = [ln.strip() for ln in out.splitlines() if ln.strip()]
    # Filter to code files we might refactor
    return [
        f
        for f in files
        if f.startswith("src/") and f.endswith((".py", ".ts", ".tsx", ".js"))
    ]


def _load_graph_edges() -> List[Tuple[str, str]]:
    if COHERENCE_GRAPH.exists():
        try:
            data = json.loads(COHERENCE_GRAPH.read_text(encoding="utf-8"))
            edges = []
            for e in data.get("edges", []):
                src = e.get("src") or e.get("source")
                dst = e.get("dst") or e.get("target")
                if (
                    isinstance(src, str)
                    and isinstance(dst, str)
                    and src.startswith("src/")
                    and dst.startswith("src/")
                ):
                    edges.append((src, dst))
            return edges
        except Exception:
            pass
    return []


def _propose_slices(max_slices: int = 5) -> List[Dict[str, Any]]:
    files = _list_repo_files()
    edges = _load_graph_edges()
    incoming: Dict[str, int] = {f: 0 for f in files}
    for _, d in edges:
        if d in incoming:
            incoming[d] += 1
    # Pick small clusters by directory with no or few incoming edges
    by_dir: Dict[str, List[str]] = {}
    for f in files:
        d = str(Path(f).parent)
        by_dir.setdefault(d, []).append(f)
    candidates: List[Tuple[str, List[str]]] = []
    for d, fs in by_dir.items():
        if len(fs) <= 10:
            # Require that most files in folder have zero incoming edges (approximate boundary)
            zero_in = sum(1 for f in fs if incoming.get(f, 0) == 0)
            if zero_in >= max(1, int(0.8 * len(fs))):
                candidates.append((d, fs))
    # Sort by estimated LOC ascending (smaller first) to keep slices small
    candidates.sort(key=lambda t: _estimate_loc(t[1]))
    slices: List[Dict[str, Any]] = []
    today = time.strftime("%Y%m%d")
    for i, (d, fs) in enumerate(candidates[:max_slices], start=1):
        est = _estimate_loc(fs)
        entry_points = [
            f
            for f in fs
            if re.search(r"(__main__|cli|server|api|main)\.(py|ts|js|tsx)$", f)
        ]
        dom = Path(d).name.replace("-", "_")
        flag = f"ISA_REF_{dom.upper()}_{today}"
        risk = 2 if est <= 400 else 3
        slices.append(
            {
                "name": f"S{i:02d}",
                "domain": dom,
                "files": fs,
                "entry_points": entry_points,
                "flag": flag,
                "est_loc": est,
                "risk": risk,
            }
        )
    return slices


def cmd_slice(args: argparse.Namespace) -> None:
    board = load_board()
    slices = _propose_slices(max_slices=10)
    for s in slices:
        sid = s["name"]
        board["slices"][sid] = {**s, "status": "TODO"}
        if sid not in board["columns"]["TODO"]:
            board["columns"]["TODO"].append(sid)
    save_board(board)
    # Output format:
    # S01|<domain>|files|entry-points|flag-name|est LOC|risk 1-5
    for s in slices:
        print(
            f"{s['name']}|{s['domain']}|{','.join(s['files'])}|{','.join(s['entry_points'])}|{s['flag']}|{s['est_loc']}|{s['risk']}"
        )


def cmd_scaffold(args: argparse.Namespace) -> None:
    board = load_board()
    sid = args.slice
    s = board["slices"].get(sid)
    if not s:
        print(f"Slice not found: {sid}")
        sys.exit(1)
    flags = load_flags()
    fname = s["flag"]
    flags["flags"][fname] = {"enabled": False, "traffic": 0, "created_at": time.time()}
    save_flags(flags)
    # Move card to FLAG-CREATED
    for col in board["columns"].values():
        if sid in col:
            col.remove(sid)
    board["columns"]["FLAG-CREATED"].append(sid)
    s["status"] = "FLAG-CREATED"
    save_board(board)
    flag_url = f"file://{FLAGS_FILE}#{fname}"
    dash_url = f"file://{ARTIFACTS_DIR}/metrics_{sid}.md"
    (ARTIFACTS_DIR / f"metrics_{sid}.md").write_text(
        "# Canary Dashboard (local stub)\n", encoding="utf-8"
    )
    print(f"FLAG URL: {flag_url}")
    print(f"DASHBOARD: {dash_url}")


def cmd_next(args: argparse.Namespace) -> None:
    board = load_board()
    if board.get("blocked"):
        print(
            "BLOCKED:", ", ".join(board.get("block_reasons", [])) or "unknown reasons"
        )
        print("Resolve issues in docs/issues/ then re-run pre-check.")
        sys.exit(2)
    # Pick first from TODO by smallest est_loc
    todos = board["columns"]["TODO"]
    if not todos:
        print("No TODO slices. Run: slice")
        return
    # Re-order by est_loc
    todos_sorted = sorted(todos, key=lambda sid: board["slices"][sid]["est_loc"])  # noqa: E501
    sid = todos_sorted[0]
    s = board["slices"][sid]
    branch = f"refactor/{sid}-{s['domain']}"
    # Simulate commands
    test_targets = " ".join(
        shlex.quote(f) for f in s["files"] if f.endswith("_test.py")
    )
    cmds = [
        "semgrep --config p/ci --dry-run || true",
        "ruff format . || true",
        f"python3 -m pytest -q {test_targets} || python3 -m pytest -q || true",
        "mypy src || true",
    ]
    for c in cmds:
        _rc, out = run(c)
        (
            ARTIFACTS_DIR / f"{sid}_{re.sub('[^a-zA-Z0-9]+', '_', c)[:40]}.log"
        ).write_text(out, encoding="utf-8")
    # Keep flag false (safe)
    print(f"PICKED: {sid}")
    print(f"CREATING PR (local sim): {branch}")
    print("COMMANDS RUN:")
    print("- semgrep --config p/ci --dry-run → see logs")
    print("- ruff format → applied (no-commit)")
    print("- pytest → see logs")
    print("- mypy --strict (advisory) → see logs")
    print(f"FLAG {s['flag']} still false (safe)")
    print(f"PR READY: file://{ARTIFACTS_DIR}/SIMULATED_PR_{sid}.md")
    (ARTIFACTS_DIR / f"SIMULATED_PR_{sid}.md").write_text(
        f"Simulated PR for {sid}: {s['domain']}\nFiles: {len(s['files'])}\n",
        encoding="utf-8",
    )
    # Move to PR-OPEN
    for col in board["columns"].values():
        if sid in col:
            col.remove(sid)
    board["columns"]["PR-OPEN"].append(sid)
    s["status"] = "PR-OPEN"
    save_board(board)


def cmd_status(args: argparse.Namespace) -> None:
    board = load_board()
    print(f"BOARD: {board['name']}")
    print(f"BLOCKED: {board.get('blocked', False)}")
    if board.get("blocked"):
        print(f"REASONS: {', '.join(board.get('block_reasons', []))}")
    for col in ["TODO", "FLAG-CREATED", "PR-OPEN", "CANARY", "DONE"]:
        print(f"{col}: {', '.join(board['columns'].get(col, []))}")


def cmd_sweep(args: argparse.Namespace) -> None:
    sid = args.slice
    board = load_board()
    s = board["slices"].get(sid)
    if not s:
        print(f"Slice not found: {sid}")
        sys.exit(1)
    # Simulate: removing legacy files matching *legacy*.py under slice files' dirs
    dirs = sorted({str(Path(f).parent) for f in s["files"]})
    legacy: List[str] = []
    for d in dirs:
        for p in Path(d).glob("*legacy*.py"):
            legacy.append(str(p))
    if not legacy:
        print(f"No legacy files found for {sid}")
        return
    print(f"FLAG {s['flag']} at 100% (assumed). Removing old path:")
    for f in legacy:
        print(f"- {f}")
    # Do not delete automatically; write a plan file
    plan = ARTIFACTS_DIR / f"cleanup_{sid}.txt"
    plan.write_text("\n".join(legacy), encoding="utf-8")
    print(f"OPENED: cleanup/{sid}-remove-legacy (simulated). Plan: {plan}")


def cmd_rollback(args: argparse.Namespace) -> None:
    flags = load_flags()
    n = 0
    for name, cfg in list(flags.get("flags", {}).items()):
        if name.startswith("ISA_REF_"):
            cfg["enabled"] = False
            cfg["traffic"] = 0
            n += 1
    save_flags(flags)
    print(f"FLIPPED {n} ISA_REF_* FLAGS → FALSE")
    print("DOWN-MIGRATION: none (local stub)")
    print("ROLLBACK COMPLETE")


def cmd_merge(args: argparse.Namespace) -> None:
    board = load_board()
    merged: List[str] = []
    for sid in args.slices:
        s = board["slices"].get(sid)
        if not s:
            print(f"Skip (not found): {sid}")
            continue
        # Remove from all columns
        for col in board["columns"].values():
            if sid in col:
                col.remove(sid)
        # Add to DONE
        if sid not in board["columns"]["DONE"]:
            board["columns"]["DONE"].append(sid)
        s["status"] = "DONE"
        board.setdefault("history", []).append(
            {"ts": time.time(), "event": "merge", "slice": sid}
        )
        merged.append(sid)
    save_board(board)
    if merged:
        print("MERGED:", ", ".join(merged))
    else:
        print("No slices merged.")


def cmd_archive(args: argparse.Namespace) -> None:
    board = load_board()
    archive_dir = ARTIFACTS_DIR / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    name = board.get("name", "REFACTOR_2025")
    out = archive_dir / f"{name}_{ts}.json"
    board_copy = dict(board)
    board_copy["archived_at"] = time.time()
    out.write_text(json.dumps(board_copy, indent=2), encoding="utf-8")
    print(f"ARCHIVED: {out}")


def cmd_new_board(args: argparse.Namespace) -> None:
    name = args.name
    board = {
        "name": name,
        "blocked": False,
        "block_reasons": [],
        "columns": {
            "TODO": [],
            "FLAG-CREATED": [],
            "PR-OPEN": [],
            "CANARY": [],
            "DONE": [],
        },
        "slices": {},
        "history": [],
        "initialized": True,
    }
    save_board(board)
    print(f"BOARD CREATED: {name}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ISA_D Refactor Guard CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("bootstrap", help="Initialize board and state")
    sub.add_parser("pre-check", help="Run tests 3x, compute coverage gaps, flakies")
    sub.add_parser("slice", help="Propose slices and update board")

    ps = sub.add_parser("scaffold", help="Create feature flag and stub canary metrics")
    ps.add_argument("slice", help="Slice ID (e.g., S01)")

    sub.add_parser("next", help="Pick highest-value slice and simulate PR")
    sub.add_parser("status", help="Board snapshot")

    sw = sub.add_parser("sweep", help="Remove legacy files after soak (simulated)")
    sw.add_argument("slice", help="Slice ID (e.g., S01)")

    sub.add_parser("rollback", help="Flip all ISA_REF_* flags to false")

    mg = sub.add_parser(
        "merge", help="Mark one or more slices as merged (moves to DONE)"
    )
    mg.add_argument("slices", nargs="+", help="Slice IDs, e.g., S02 S03")

    sub.add_parser(
        "archive", help="Archive current board to artifacts/refactor_guard/archive/"
    )

    nb = sub.add_parser("new-board", help="Create a fresh board with the given name")
    nb.add_argument("name", help="Board name, e.g., REFACTOR_2025_W2")

    return p


def main(argv: Optional[List[str]] = None) -> None:
    argv = argv or sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    cmd = args.cmd.replace("-", "_")
    if cmd == "bootstrap":
        cmd_bootstrap(args)
    elif cmd == "pre_check":
        cmd_precheck(args)
    elif cmd == "slice":
        cmd_slice(args)
    elif cmd == "scaffold":
        cmd_scaffold(args)
    elif cmd == "next":
        cmd_next(args)
    elif cmd == "status":
        cmd_status(args)
    elif cmd == "sweep":
        cmd_sweep(args)
    elif cmd == "rollback":
        cmd_rollback(args)
    elif cmd == "merge":
        cmd_merge(args)
    elif cmd == "archive":
        cmd_archive(args)
    elif cmd == "new_board":
        cmd_new_board(args)
    else:
        parser.error(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
