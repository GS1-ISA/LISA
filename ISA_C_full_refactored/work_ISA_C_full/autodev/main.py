from __future__ import annotations

import argparse
import json
import time

from .agent import run_once


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loop", action="store_true", help="run continuous loop")
    ap.add_argument("--sleep", type=int, default=10, help="seconds between loops")
    args = ap.parse_args()
    if args.loop:
        while True:
            res = run_once()
            print(
                json.dumps(
                    {"decision": res.get("decision"), "next": res.get("next_action")},
                    ensure_ascii=False,
                )
            )
            time.sleep(args.sleep)
    else:
        res = run_once()
        print(
            json.dumps(
                {"decision": res.get("decision"), "next": res.get("next_action")},
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
