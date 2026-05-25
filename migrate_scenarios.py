#!/usr/bin/env python3
"""Migrate scenarios/ and scenarios-parsed/ to transcription format."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCENARIOS_DIR = Path("scenarios")
PARSED_DIR = Path("scenarios-parsed")
TRANSCRIPTION_DIR = Path("transcription")
TRANSCRIPTION_PARSED_DIR = Path("transcription-parsed")
AUDIO_DIR = Path("transcription-audio")

for d in (TRANSCRIPTION_DIR, TRANSCRIPTION_PARSED_DIR, AUDIO_DIR):
    d.mkdir(exist_ok=True)


def extract_hanzi(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    match = re.search(r"### Hanzi\s*\n(.*?)\n---", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def next_transcription_id() -> int:
    existing = [
        int(re.match(r"t-(\d+)-", f.name).group(1))
        for f in TRANSCRIPTION_DIR.glob("t-*.txt")
        if re.match(r"t-(\d+)-", f.name)
    ]
    return max(existing, default=0) + 1


def migrate(dry_run=False):
    md_files = sorted(SCENARIOS_DIR.glob("*.md"))
    counter = next_transcription_id()

    for md in md_files:
        # strip numeric prefix from scenario name, e.g. "001-at-supermarket" -> "at-supermarket"
        topic = re.sub(r"^\d+-", "", md.stem)
        new_stem = f"{counter:03d}-{topic}"
        counter += 1

        # 1. transcription/t-NNN-topic.txt
        txt_dest = TRANSCRIPTION_DIR / f"t-{new_stem}.txt"
        if not txt_dest.exists():
            hanzi = extract_hanzi(md)
            if not dry_run:
                txt_dest.write_text(hanzi + "\n", encoding="utf-8")
            print(f"  txt  {txt_dest}")
        else:
            print(f"  skip {txt_dest} (exists)")

        # 2. transcription-parsed/p-NNN-topic.json
        json_src = PARSED_DIR / f"{md.stem}.json"
        json_dest = TRANSCRIPTION_PARSED_DIR / f"p-{new_stem}.json"
        if json_src.exists() and not json_dest.exists():
            if not dry_run:
                shutil.copy2(json_src, json_dest)
            print(f"  json {json_dest}")
        elif json_dest.exists():
            print(f"  skip {json_dest} (exists)")
        else:
            print(f"  WARN {json_src} not found, skipping json")

        # 3. transcription-audio/p-NNN-topic.m4a
        audio_dest = AUDIO_DIR / f"p-{new_stem}.m4a"
        if not audio_dest.exists():
            if not dry_run:
                subprocess.run(
                    ["python3", "play.py", str(txt_dest), "-o", str(audio_dest)],
                    check=True,
                )
            print(f"  audio {audio_dest}")
        else:
            print(f"  skip {audio_dest} (exists)")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN — no files written\n")
    migrate(dry_run=dry_run)
    print("\nDone.")
