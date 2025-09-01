#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


CI_FILE = Path('.github/workflows/ci.yml')
NIGHTLY_FILE = Path('.github/workflows/nightly.yml')
WEEKLY_FILE = Path('.github/workflows/weekly.yml')


@dataclass
class Gate:
    name: str
    pattern: str
    file: Path
    enforced: Optional[bool] = None
    present: bool = False
    line: int = 0
    snippet: str = ''
    notes: str = ''


def find_in_file(file: Path, substr: str) -> tuple[bool, int, str]:
    if not file.exists():
        return False, 0, ''
    try:
        lines = file.read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception:
        return False, 0, ''
    for i, line in enumerate(lines, start=1):
        if substr in line:
            return True, i, line.strip()
    return False, 0, ''


def detect_enforced(file: Path, line_no: int) -> Optional[bool]:
    """Heuristic: if a nearby step has continue-on-error: true then not enforced."""
    if not file.exists() or line_no <= 0:
        return None
    lines = file.read_text(encoding='utf-8', errors='ignore').splitlines()
    span = lines[max(0, line_no-1): min(len(lines), line_no+10)]
    for ln in span:
        if 'continue-on-error:' in ln:
            return 'true' not in ln.lower()
    return True


def collect_gates() -> List[Gate]:
    gates: List[Gate] = []
    gates.append(Gate('Lint (ruff)', 'ruff check', CI_FILE))
    gates.append(Gate('Format (ruff)', 'ruff format --check', CI_FILE))
    gates.append(Gate('Typecheck (mypy)', 'mypy ', CI_FILE))
    gates.append(Gate('Tests (pytest)', 'pytest -q', CI_FILE))
    gates.append(Gate('Coverage XML', '--cov-report=xml', CI_FILE))
    gates.append(Gate('Coverage delta', 'scripts/check_coverage_delta.py', CI_FILE))
    gates.append(Gate('Bandit', 'bandit ', CI_FILE))
    gates.append(Gate('pip-audit', 'pip-audit', CI_FILE))
    gates.append(Gate('Radon', 'radon cc', CI_FILE))
    gates.append(Gate('Semgrep (deep)', 'semgrep', CI_FILE))
    gates.append(Gate('Significance trigger', 'significance_trigger.py', CI_FILE))
    gates.append(Gate('Gitleaks', 'gitleaks/gitleaks-action', CI_FILE))
    gates.append(Gate('Mutation/fuzz/bench (on-demand)', 'mutmut', NIGHTLY_FILE))
    gates.append(Gate('CrossHair (on-demand)', 'crosshair', WEEKLY_FILE))
    gates.append(Gate('SBOM/Trivy (on-demand)', 'trivy-action', WEEKLY_FILE))
    return gates


def main() -> int:
    out_dir = Path('docs/audit')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / 'gates_status.csv'
    gates = collect_gates()
    rows = []
    for g in gates:
        present, line, snippet = find_in_file(g.file, g.pattern)
        g.present = present
        g.line = line
        g.snippet = snippet
        g.enforced = detect_enforced(g.file, line) if present else None
        if g.name == 'Semgrep (deep)':
            g.notes = 'Conditional on significance'
        if g.name in ('Mutation/fuzz/bench (on-demand)', 'CrossHair (on-demand)', 'SBOM/Trivy (on-demand)'):
            g.notes = 'On-demand workflow (no cron)'
        rows.append(g)
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Gate', 'File', 'Present', 'Enforced', 'Line', 'Evidence', 'Notes'])
        for g in rows:
            w.writerow([g.name, str(g.file), g.present, g.enforced, g.line, g.snippet, g.notes])
    print(f'Wrote {out_csv}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

