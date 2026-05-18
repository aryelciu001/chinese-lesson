CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    hanzi TEXT NOT NULL UNIQUE,
    pinyin TEXT NOT NULL,
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS word_examples (
    id SERIAL PRIMARY KEY,
    word_id INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    hanzi TEXT NOT NULL,
    pinyin TEXT NOT NULL,
    translation TEXT NOT NULL
);
