# Parse Scenario Skill

Parse a scenario `.md` file from the `/scenarios` folder and extract every meaningful word/phrase as a JSON array.

## Output Format

```json
[
  {
    "hanzi": "办理",
    "pinyin": "bàn lǐ",
    "translation": "to handle / to process"
  },
  ...
]
```

## Rules

- Argument is the scenario filename (with or without `.md` extension), e.g. `/parse hotel-checkin` or `/parse hotel-checkin.md`
- Read the file from `/scenarios/<filename>.md`
- Extract every **content word** from the Hanzi section
- For each word, align pinyin from the Pinyin section and derive a concise English translation
- Output must be **valid JSON only** — no prose, no markdown fences, no explanation
- Write the JSON output to `/scenarios-parsed/<filename>.json` (same base name as the input)
- when combined, json should form back the original md file
- also handle newline (\n) by setting hanzi as "\n"
- also handle sentence-ending punctuation (。！？……) as separate tokens with hanzi set to the punctuation character, pinyin and translation as ""
- **Write the JSON via a Python script** (not the Write tool) to avoid curly-quote/encoding corruption. Build the token list as a Python list of dicts and use `json.dump(..., ensure_ascii=False)` to write the file.
- After writing the JSON, run via Bash: `python3 play.py scenarios-parsed/<filename>.json -o audio/<filename>.m4a` (create `/audio/` dir if needed)

## Trigger

User invokes `/parse <filename>`
