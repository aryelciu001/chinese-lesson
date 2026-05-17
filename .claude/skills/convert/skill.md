# Convert Chinese Text Skill

Convert raw Chinese text into a scenario file and parse it in one step.

## Steps

1. Take the Chinese text from the argument
2. Generate pinyin (with tone marks) and English translation for the full text
3. Write a scenario `.md` to `/scenarios/<english-filename>.md` using the standard format (Hanzi / Pinyin / Translation sections)
4. Run the **parse** skill on that filename

## Scenario File Format

```
### Hanzi

[original Chinese text, cleaned up]

---

### Pinyin

[full pinyin with tone marks, matching the Hanzi line by line]

---

### Translation

[English translation, matching the Hanzi line by line]
```

## Rules

- Argument is raw Chinese text (any length, paragraph or dialogue)
- Choose an English filename that reflects the topic/theme of the text (e.g. `romance`, `family-dinner`, `job-interview`)
- Clean up any OCR artifacts or spacing issues in the Hanzi before writing
- Pinyin must use proper tone marks and match the Hanzi exactly, line by line
- No terminal output — all output goes to files

## Trigger

User invokes `/convert [chinese text]`
