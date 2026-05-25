#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def parse_breakdown(src: Path) -> list[dict]:
    tokens = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if line == "<newline>":
            tokens.append({"hanzi": "\n", "pinyin": "", "translation": ""})
            continue
        parts = line.split("|")
        if len(parts) != 3:
            continue
        tokens.append({
            "hanzi": parts[0],
            "pinyin": parts[1],
            "translation": parts[2],
        })
    return tokens


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <b-xxx.txt> [<b-xxx.txt> ...]")
        sys.exit(1)

    breakdown_dir = Path("transcription-breakdown")
    out_dir = Path("transcription-parsed")
    out_dir.mkdir(exist_ok=True)

    for arg in sys.argv[1:]:
        src = Path(arg)
        if not src.exists():
            src = breakdown_dir / arg
        if not src.exists():
            print(f"Not found: {arg}", file=sys.stderr)
            continue

        tokens = parse_breakdown(src)
        dest = out_dir / ("p-" + src.stem.removeprefix("b-") + ".json")
        dest.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Written: {dest}")


if __name__ == "__main__":
    main()
