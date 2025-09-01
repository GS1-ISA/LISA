#!/usr/bin/env python3
import sys
from pathlib import Path
import re

# Targeted sanitizer to remove stray single quotes inside PATH exports
# and normalize common 'Application' Support' fragments that break evals.


def fix_path_line(line):
    m = re.match(r"^(?P<prefix>\s*(?:export\s+)?PATH\s*=\s*)(?P<rhs>.*)$", line)
    if not m:
        return line
    prefix = m.group("prefix")
    rhs = m.group("rhs").rstrip("\n")
    # Remove stray single quotes commonly introduced (only inside RHS)
    rhs = rhs.replace("'", "")
    # Normalize Application Support artifacts
    rhs = rhs.replace("Application Support", "Application Support")
    # remove duplicated spaces
    rhs = re.sub(r"\s+", " ", rhs)
    # remove surrounding quotes
    if (rhs.startswith('"') and rhs.endswith('"')) or (rhs.startswith("'") and rhs.endswith("'")):
        inner = rhs[1:-1]
    else:
        inner = rhs
    parts = inner.split(":")
    fixed_parts = []
    for p in parts:
        p = p.strip()
        if p == "":
            fixed_parts.append(p)
            continue
        if re.match(r"^\$[A-Za-z_][A-Za-z0-9_]*$", p):
            fixed_parts.append(p)
            continue
        # If item contains spaces or special chars, double-quote and escape
        if " " in p or "\t" in p:
            esc = p.replace('"', '\\"')
            fixed_parts.append(f'"{esc}"')
        else:
            fixed_parts.append(p)
    new_rhs = ":".join(fixed_parts)
    new = f'{prefix}"{new_rhs}"\n'
    return new


def process_file(path):
    p = Path(path).expanduser()
    if not p.exists():
        print(f"NOTFOUND: {p}")
        return 2
    text = p.read_text()
    out_lines = []
    changed = False
    for line in text.splitlines(True):
        if "PATH" in line and re.search(r"(?:export\s+)?PATH\s*=", line):
            fixed = fix_path_line(line)
            out_lines.append(fixed)
            if fixed != line:
                changed = True
        else:
            # Also fix accidental lone single quotes like Application' Support elsewhere
            new_line = line.replace("Application' Support", "Application Support")
            if new_line != line:
                changed = True
            out_lines.append(new_line)
    fixed_path = str(p) + ".fixed"
    Path(fixed_path).write_text("".join(out_lines))
    if changed:
        print(f"FIXED: {p} -> {fixed_path}")
        return 0
    else:
        print(f"NOCHANGE: {p}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: targeted_sanitize.py <file1> [file2 ...]")
        sys.exit(3)
    for f in sys.argv[1:]:
        process_file(f)
    sys.exit(0)
