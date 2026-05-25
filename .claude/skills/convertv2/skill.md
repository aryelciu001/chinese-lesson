# ConvertV2 Skill

Full pipeline: transcribe an image or text → breakdown → parse JSON → generate audio.

## Steps

1. Run the **transcribe** skill on the argument — saves to `/transcription/t-NNN-topic.txt`
2. Run the **breakdown** skill on the resulting `t-NNN-topic` filename — saves to `/transcription-breakdown/b-NNN-topic.txt`
3. Run `python3 parse_breakdown.py b-NNN-topic.txt` — saves to `/transcription-parsed/p-NNN-topic.json`
4. Run `python3 play.py transcription/t-NNN-topic.txt -o transcription-audio/p-NNN-topic.m4a`

## Rules

- Argument is an image or raw Chinese text, passed directly to the transcribe skill
- Derive the `NNN-topic` portion from the filename the transcribe skill creates
- Run all four steps in order, each depending on the previous
- No extra output — just execute each step

## Trigger

User invokes `/convertv2 [image or chinese text]`
