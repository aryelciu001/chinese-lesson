# Breakdown Transcription Skill

Read a transcription `.txt` file, break each line into individual words, and for each word output hanzi, pinyin, and English translation separated by `|`.

## Steps

1. Read the transcription file from `/transcription/<filename>.txt`
2. Split each line into individual words (word-level segmentation)
3. For each word, generate pinyin (with tone marks) and a concise English translation
4. Write one word per line in the output file
5. Actual line breaks in the transcription become a literal `<newline>` line

## Output Format

One word per line: `hanzi|pinyin|translation`

```
小林：|Xiǎo Lín：|Xiao Lin:
听说|tīng shuō|heard that
你|nǐ|you
又|yòu|again
换|huàn|change
工作|gōngzuò|job
了？|le？|(completed action)?
<newline>
小李：|Xiǎo Lǐ：|Xiao Li:
别|bié|don't
提|tí|mention
了！|le！|(exclamation)
```

## Rules

- Argument is the transcription filename (with or without `.txt`), e.g. `/breakdown t-002-job-switching`
- Preserve ALL characters: speaker labels, colons, punctuation — nothing is dropped
- Split at the **word level** — each entry is a single Chinese word or morpheme (e.g. 换工作 → 换 / 工作)
- Multi-character words that function as a unit stay together (e.g. 地铁站, 支付宝, 高峰期)
- Particles and sentence-final particles (了, 吗, 吧, 呢, 啊) are their own line, with closing punctuation attached
- Speaker labels (e.g. `A：`, `B：`, `小林：`) are kept as a single line unchanged
- Keep punctuation attached to the word it closes
- Each newline in the source becomes a `<newline>` line in the output
- Output file goes to `/transcription-breakdown/b-<rest-of-name>.txt` (strip `t-` prefix, add `b-`)
- Create `/transcription-breakdown/` if it does not exist
- Write the file using the Write tool

## Trigger

User invokes `/breakdown <filename>`
