#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import tempfile


PAUSE = {
    "。": "[[slnc 500]]",
    "！": "[[slnc 500]]",
    "？": "[[slnc 500]]",
    "……": "[[slnc 800]]",
    "；": "[[slnc 400]]",
}

def build_text_from_md(path):
    text = open(path, encoding="utf-8").read()
    match = re.search(r"### Hanzi\s*\n(.*?)\n---", text, re.DOTALL)
    hanzi = match.group(1).strip() if match else ""
    parts = []
    for line in hanzi.splitlines():
        line = line.strip()
        if not line:
            continue
        # insert pauses for sentence-ending punctuation
        for ch, pause in PAUSE.items():
            line = line.replace(ch, ch + " " + pause + " ")
        parts.append(line)
    return " [[slnc 700]] ".join(parts)


def build_text(words):
    parts = []
    current = []
    for w in words:
        h = w["hanzi"]
        if h == "\n":
            if current:
                parts.append("".join(current))
            current = []
        elif h in PAUSE:
            current.append(" " + PAUSE[h] + " ")
        else:
            current.append(h)
    if current:
        parts.append("".join(current))
    return " [[slnc 700]] ".join(parts)


def get_text(path):
    if path.endswith(".md"):
        return build_text_from_md(path)
    with open(path, encoding="utf-8") as f:
        words = json.load(f)
    return build_text(words)


def play(path, rate=120, voice="Tingting"):
    text = get_text(path)
    subprocess.run(["say", "-v", voice, "-r", str(rate), text], check=True)


def export(path, output, rate=120, voice="Tingting"):
    text = get_text(path)

    aiff_fd, aiff_path = tempfile.mkstemp(suffix=".aiff")
    os.close(aiff_fd)
    try:
        subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", aiff_path, text], check=True)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", aiff_path, output], check=True)
    finally:
        os.unlink(aiff_path)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} <scenario.json> [-o output.m4a] [--rate N] [--voice NAME]")
        sys.exit(1)

    path = args.pop(0)
    output = None
    rate = 120
    voice = "Tingting"

    while args:
        a = args.pop(0)
        if a == "-o":
            output = args.pop(0)
        elif a == "--rate":
            rate = int(args.pop(0))
        elif a == "--voice":
            voice = args.pop(0)

    if output:
        export(path, output, rate, voice)
    else:
        play(path, rate, voice)
