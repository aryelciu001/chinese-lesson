# Breakdown Transcription Skill

Read a transcription `.txt` file, break each line into natural phrases, and for each phrase output hanzi, pinyin, and English translation separated by `|`.

## Steps

1. Read the transcription file from `/transcription/<filename>.txt`
2. Split each line into natural spoken phrases
3. For each phrase, generate pinyin (with tone marks) and a concise English translation
4. Write one phrase per line in the output file
5. Actual line breaks in the transcription become a literal `<newline>` line

## Output Format

One phrase per line: `hanzi|pinyin|translation`

```
小林：|Xiǎo Lín：|Xiao Lin:
听说|tīng shuō|I heard that
你|nǐ|you
又|yòu|again
换工作了？|huàn gōngzuò le？|changed jobs?
<newline>
小李：|Xiǎo Lǐ：|Xiao Li:
别提了！|bié tí le！|do not mention it!
```

## Rules

- Argument is the transcription filename (with or without `.txt`), e.g. `/breakdown t-002-job-switching`
- Preserve ALL characters: speaker labels, colons, punctuation — nothing is dropped
- Split at natural spoken boundaries — meaningful words and short phrases, not individual characters
- Keep punctuation attached to the phrase it closes
- Each newline in the source becomes a `<newline>` line in the output
- Output file goes to `/transcription-breakdown/b-<rest-of-name>.txt` (strip `t-` prefix, add `b-`)
- Create `/transcription-breakdown/` if it does not exist
- Write the file using the Write tool

## Trigger

User invokes `/breakdown <filename>`
