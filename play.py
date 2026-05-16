#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile


def build_text(words):
    parts = []
    current = []
    for w in words:
        if w["hanzi"] == "\n":
            if current:
                parts.append("".join(current))
            current = []
        else:
            current.append(w["hanzi"])
    if current:
        parts.append("".join(current))
    return " [[slnc 700]] ".join(parts)


def play(path, rate=120, voice="Tingting"):
    with open(path, encoding="utf-8") as f:
        words = json.load(f)
    text = build_text(words)
    subprocess.run(["say", "-v", voice, "-r", str(rate), text], check=True)


def export(path, output, rate=120, voice="Tingting"):
    with open(path, encoding="utf-8") as f:
        words = json.load(f)
    text = build_text(words)

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
