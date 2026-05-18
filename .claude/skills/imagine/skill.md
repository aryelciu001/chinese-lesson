# Imagine Conversation Skill

Generate a short, realistic Chinese conversation scenario based on the topic provided by the user.

## Format

Output three separate sections in this exact order:

---

### Hanzi

[Full conversation in Chinese characters only]

---

### Pinyin

[Full conversation in pinyin with tone marks, line by line matching the Hanzi section]

---

### Translation

[Full conversation translated to English, line by line matching the Hanzi section]

---

## Rules

- Each section must contain the same number of lines/exchanges
- Label each speaker consistently (e.g. A: / B:)
- Conversation should be 6–10 lines total (3–5 exchanges)
- Vocabulary and grammar should match advanced level (HSK 4–6)
- Do not use any idioms, unless it is appropriate. the goal of the study is to have conversational skill
- Topic is provided as the skill argument — use it as the setting or subject of the conversation
- Write the skill output in English (labels, section headers), Chinese for the content
- write the conversation to /scenarios folder. name it in english with a numeric prefix: check `ls scenarios-parsed/` to find the highest current NNN, increment by 1, and name the file `NNN-topic-name.md`. no output on terminal

## Trigger

User invokes `/imagine [topic]`
