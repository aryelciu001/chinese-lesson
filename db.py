import json
import os
import subprocess

import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def load_words():
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, hanzi, pinyin FROM words WHERE deleted_at IS NULL ORDER BY id DESC")
        rows = cur.fetchall()
        words = []
        for row in rows:
            cur.execute(
                "SELECT hanzi, pinyin, translation FROM word_examples WHERE word_id = %s ORDER BY id",
                (row["id"],),
            )
            words.append({"hanzi": row["hanzi"], "pinyin": row["pinyin"], "examples": cur.fetchall()})
        return words


def save_word(hanzi, pinyin, examples):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO words (hanzi, pinyin) VALUES (%s, %s) RETURNING id",
            (hanzi, pinyin),
        )
        word_id = cur.fetchone()[0]
        for ex in examples:
            cur.execute(
                "INSERT INTO word_examples (word_id, hanzi, pinyin, translation) VALUES (%s, %s, %s, %s)",
                (word_id, ex["hanzi"], ex["pinyin"], ex["translation"]),
            )
        conn.commit()


def word_exists(hanzi):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM words WHERE hanzi = %s AND deleted_at IS NULL", (hanzi,))
        return cur.fetchone() is not None


def import_words_json():
    with open(os.path.join(os.path.dirname(__file__), "words.json"), encoding="utf-8") as f:
        words = json.load(f)
    inserted = skipped = 0
    with get_conn() as conn, conn.cursor() as cur:
        for w in words:
            cur.execute("SELECT 1 FROM words WHERE hanzi = %s AND deleted_at IS NULL", (w["hanzi"],))
            if cur.fetchone():
                skipped += 1
                continue
            cur.execute(
                "INSERT INTO words (hanzi, pinyin) VALUES (%s, %s) RETURNING id",
                (w["hanzi"], w["pinyin"]),
            )
            word_id = cur.fetchone()[0]
            for ex in w["examples"]:
                cur.execute(
                    "INSERT INTO word_examples (word_id, hanzi, pinyin, translation) VALUES (%s, %s, %s, %s)",
                    (word_id, ex["hanzi"], ex["pinyin"], ex["translation"]),
                )
            inserted += 1
        conn.commit()
    return inserted, skipped


def generate_word_data(hanzi):
    prompt = (
        f'For the Chinese word or phrase "{hanzi}", output ONLY plain text, exactly 10 lines, no labels, no blank lines:\n'
        "Line 1: pinyin of the word\n"
        "Line 2: example sentence 1 (hanzi)\n"
        "Line 3: example sentence 2 (hanzi)\n"
        "Line 4: example sentence 3 (hanzi)\n"
        "Line 5: example sentence 1 (pinyin)\n"
        "Line 6: example sentence 2 (pinyin)\n"
        "Line 7: example sentence 3 (pinyin)\n"
        "Line 8: example sentence 1 (english translation)\n"
        "Line 9: example sentence 2 (english translation)\n"
        "Line 10: example sentence 3 (english translation)\n"
        "Examples must be natural, contextually rich sentences (HSK 4-6 level), ordered simple to complex."
    )
    result = subprocess.run(
        ["claude", "-p", prompt], capture_output=True, text=True, timeout=60
    )
    lines = result.stdout.strip().splitlines()
    if len(lines) < 10:
        raise ValueError(f"unexpected output ({len(lines)} lines): {result.stdout!r}")
    return {
        "pinyin": lines[0],
        "examples": [
            {"hanzi": lines[1 + i], "pinyin": lines[4 + i], "translation": lines[7 + i]}
            for i in range(3)
        ],
    }
