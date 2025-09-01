#!/usr/bin/env python3
"""Check required environment variables and print a compact report.
Run: python3 scripts/check_env.py
"""

import os
from textwrap import indent


def check(keys):
    res = {}
    for k in keys:
        v = os.getenv(k)
        res[k] = bool(v)
    return res


REQUIRED = [
    "ISA_LLM_PROVIDER",
    "OPENROUTER_API_KEY",
    "ISA_API_KEY_OPENROUTER",
    "OPENAI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
]

if __name__ == "__main__":
    report = check(REQUIRED)
    missing = [k for k, v in report.items() if not v]
    print("Environment check:\n")
    for k, v in report.items():
        print(f"  {k}: {'OK' if v else 'MISSING'}")
    print()
    if missing:
        print("Missing variables (edit .env or export in your shell):")
        print(indent("\n".join(missing), "  "))
        raise SystemExit(2)
    print("All required env vars appear present.")
