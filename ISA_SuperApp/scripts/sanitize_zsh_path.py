#!/usr/bin/env python3
import sys
from pathlib import Path
import re

def fix_path_line(line):
    m = re.match(r"^(?P<prefix>\s*(?:export\s+)?PATH\s*=\s*)(?P<rhs>.*)$", line)
    if not m:
        return line
    prefix = m.group('prefix')
    rhs = m.group('rhs').rstrip('\n')
    # remove surrounding quotes if any
    if (rhs.startswith('"') and rhs.endswith('"')) or (rhs.startswith("'") and rhs.endswith("'")):
        inner = rhs[1:-1]
    else:
        inner = rhs
    parts = inner.split(':')
    fixed_parts = []
    for p in parts:
        p = p.strip()
        if p == '':
            fixed_parts.append(p)
            continue
        if re.match(r"^\$[A-Za-z_][A-Za-z0-9_]*$", p):
            fixed_parts.append(p)
            continue
        if ' ' in p or "'" in p or '"' in p:
            esc = p.replace('"', '\\"')
            fixed_parts.append(f'"{esc}"')
        else:
            fixed_parts.append(p)
    new_rhs = ':'.join(fixed_parts)
    new = f"{prefix}\"{new_rhs}\"\n"
    return new


def process_file(path):
    p = Path(path).expanduser()
    if not p.exists():
        return 2
    text = p.read_text()
    out_lines = []
    changed = False
    for line in text.splitlines(True):
        if 'PATH' in line and re.search(r"(?:export\s+)?PATH\s*=", line):
            fixed = fix_path_line(line)
            out_lines.append(fixed)
            if fixed != line:
                changed = True
        else:
            out_lines.append(line)
    fixed_path = str(p) + '.fixed'
    Path(fixed_path).write_text(''.join(out_lines))
    return 0 if changed else 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: sanitize_zsh_path.py <file1> [file2 ...]')
        sys.exit(3)
    results = {}
    for f in sys.argv[1:]:
        res = process_file(f)
        results[f] = res
    for k,v in results.items():
        if v == 2:
            print(f'NOTFOUND: {k}')
        elif v == 1:
            print(f'NOCHANGE: {k}')
        else:
            print(f'FIXED: {k} -> {k}.fixed')
    sys.exit(0)
