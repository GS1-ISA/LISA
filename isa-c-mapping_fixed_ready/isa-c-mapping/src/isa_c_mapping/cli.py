import json, sys, argparse, pathlib
from .mapping import to_isa_c


def main(argv=None):
    ap = argparse.ArgumentParser(prog="isa-c-mapping")
    ap.add_argument("input", help="Input JSON file path")
    ap.add_argument("-o", "--output", default="out/isa_c.json", help="Output JSON file path")
    args = ap.parse_args(argv)

    in_path = pathlib.Path(args.input)
    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    isa = to_isa_c(data)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(isa, f, ensure_ascii=False, indent=2)

    print(str(out_path))


if __name__ == "__main__":
    main()
