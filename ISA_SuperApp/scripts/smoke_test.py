import sys

import requests


def main():
    base = "http://127.0.0.1:8787"
    paths = ["/healthz", "/ui/users", "/static/styles.css", "/static/tokens.css"]
    ok = True
    for p in paths:
        try:
            r = requests.get(base + p, timeout=5)
            print(p, r.status_code)
            if r.status_code != 200:
                ok = False
        except Exception as e:
            print(p, "ERROR", e)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
