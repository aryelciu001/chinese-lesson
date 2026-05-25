# Transcribe Chinese Text Skill

Extract and output only the Chinese characters from an image or pasted text.

## Steps

1. Read the argument (image or raw text)
2. Extract only the Chinese characters, preserving line breaks and speaker labels
3. Clean up OCR artifacts, extra spaces, and line-wrap artifacts
4. Output the cleaned Chinese text into `/transcription` folder. use such format `t-count-topic.txt`

## Rules

- No pinyin, no translation, no file writing
- Preserve the original structure (speaker labels, line breaks, punctuation)
- Output the transcribed text in a code block

## Trigger

User invokes `/transcribe [image or chinese text]`
