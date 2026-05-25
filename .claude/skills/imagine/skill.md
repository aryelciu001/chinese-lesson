# Imagine Skill

Generate a Chinese conversation or text from a user description, then run the full convertv2 pipeline on it.

## Steps

1. **Determine the next file number** by listing `/transcription/` and finding the highest `t-NNN` number, then incrementing by 1 (zero-padded to 3 digits).
2. **Derive a short topic slug** from the user's input (lowercase, hyphen-separated, max 4 words, English). e.g. "shopping at the market" → `shopping-at-market`.
3. **Generate Chinese text** based on the user's input:
   - If the input implies a conversation (e.g. "dialogue", "two people", "conversation", "A and B"), generate a dialogue with speaker labels (A: / B:)
   - Otherwise generate a short narrative or descriptive paragraph
   - Length: 8–15 lines for dialogue, 5–10 sentences for narrative
   - Use natural, everyday Mandarin Chinese
   - Include only Chinese characters and punctuation — no pinyin, no translation
4. **Write the generated text** to `/transcription/t-NNN-topic.txt`
5. **Run the convertv2 skill** passing the raw generated Chinese text as the argument (not a file path)

## Rules

- Do not ask for confirmation — generate immediately
- The generated text must be plausible, natural Chinese (not a direct word-for-word translation)
- Speaker labels in dialogues use format: `A：` / `B：` (with Chinese colon)
- After writing the file, invoke `/convertv2` with the Chinese text content directly

## Trigger

User invokes `/imagine [description or topic in any language]`
