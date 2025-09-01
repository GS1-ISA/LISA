#!/usr/bin/env python3
"""
Normalize PATH assignments across specified shell init files:
- Collect path tokens from all PATH= or export PATH= lines
- Remove duplicates while preserving order
- Quote entries that contain spaces
- Rebuild a single safe export: export PATH="<joined_tokens>:$PATH"
- Write .fixed files and leave backups of originals as .bak_TIMESTAMP
"""
import sys
from pathlib import Path
import re
import time

FILES = [Path.home()/'.zprofile', Path.home()/'.zshrc']

def extract_tokens(rhs):
    # strip surrounding quotes
    rhs = rhs.strip()
    if (rhs.startswith('"') and rhs.endswith('"')) or (rhs.startswith("'") and rhs.endswith("'")):
        rhs = rhs[1:-1]
    # remove stray single quotes
    rhs = rhs.replace("'", "")
    parts = rhs.split(':')
    tokens = []
    for p in parts:
        t = p.strip()
        if not t:
            continue
        # normalize ~
        if t.startswith('~'):
            t = str(Path.home()) + t[1:]
        tokens.append(t)
    return tokens


def quote_token(t):
    if ' ' in t or '\t' in t:
        # escape any double quotes
        t_esc = t.replace('"', '\\"')
        return f'"{t_esc}"'
    return t


def normalize_file(p: Path):
    if not p.exists():
        return False, None
    s = p.read_text()
    pattern = re.compile(r'(?:export\s+)?PATH\s*=\s*(.+)')
    collected = []
    for m in pattern.finditer(s):
        rhs = m.group(1)
        tokens = extract_tokens(rhs)
        for t in tokens:
            if t not in collected and t != '$PATH' and t != '${PATH}':
                collected.append(t)
    # ensure common places at front? keep collected order
    # append $PATH at end
    new_rhs = ':'.join([quote_token(x) for x in collected] + ['$PATH'])
    new_line = f'export PATH="{new_rhs}"\n'
    # remove existing PATH lines
    out_lines = []
    for line in s.splitlines(True):
        if pattern.search(line):
            continue
        out_lines.append(line)
    # insert new line at top after any initial comments/header
    insert_at = 0
    for i, l in enumerate(out_lines[:12]):
        if l.strip() == '' or l.strip().startswith('#'):
            insert_at = i+1
        else:
            break
    out_lines.insert(insert_at, new_line)
    fixed_path = str(p) + '.fixed'
    Path(fixed_path).write_text(''.join(out_lines))
    return True, fixed_path


def apply_fixed(p: Path, fixed_path: str):
    ts = time.strftime('%Y%m%d%H%M%S')
    bak = str(p) + f'.bak_{ts}'
    p.rename(bak)
    Path(fixed_path).rename(p)
    return bak


def redacted_diff(orig_path: Path, new_path: Path):
    import difflib
    o = orig_path.read_text().splitlines()
    n = new_path.read_text().splitlines()
    diff = list(difflib.unified_diff(o, n, fromfile=str(orig_path), tofile=str(new_path), lineterm=''))
    # redact tokens that look like long keys or API values
    redacted = []
    for line in diff:
        line = re.sub(r'([A-Z0-9_]*API_KEY[A-Z0-9_]*)=\S+', r'\1=[REDACTED]', line)
        line = re.sub(r'=["\'].*["\']', '=[REDACTED]', line)
        redacted.append(line)
    return '\n'.join(redacted)


def main():
    changes = []
    for p in FILES:
        ok, fixed = normalize_file(p)
        if not ok:
            print(f'NOFILE: {p}')
            continue
        # show redacted diff
        diff = redacted_diff(p, Path(fixed))
        if diff.strip():
            print('--- DIFF for', p)
            print(diff)
        else:
            print('NO CHANGES NEEDED for', p)
        # apply fixed
        bak = apply_fixed(p, fixed)
        print(f'APPLIED: {p} (backup at {bak})')
        changes.append((p, bak))
    if not changes:
        print('Nothing changed')
    else:
        print('Normalization complete')

if __name__ == '__main__':
    main()
