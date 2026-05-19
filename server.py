#!/usr/bin/env python3
import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import psycopg2
import psycopg2.extras

PARSED_DIR = os.path.join(os.path.dirname(__file__), "scenarios-parsed")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def load_scenario(name):
    path = os.path.join(PARSED_DIR, f"{name}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_scenarios():
    names = sorted(f[:-5] for f in os.listdir(PARSED_DIR) if f.endswith(".json"))
    return names


def display_name(scenario_name):
    parts = scenario_name.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit():
        return f"{parts[0]} - {parts[1]}"
    return scenario_name


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
        for i, ex in enumerate(examples):
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


def render_words_html(words):
    cards = ""
    for w in words:
        examples_html = "".join(
            f"<li>"
            f'<div class="ex-row"><span class="ex-hanzi">{e["hanzi"]}</span>'
            f'<button class="speak-btn" data-text="{e["hanzi"]}">🔊</button>'
            f'<button class="speak-slow-btn" data-text="{e["hanzi"]}">🐢</button></div>'
            f'<span class="ex-pinyin">{e["pinyin"]}</span>'
            f'<span class="ex-trans">{e["translation"]}</span>'
            f"</li>"
            for e in w["examples"]
        )
        cards += f"""<div class="card" data-hanzi="{w["hanzi"]}">
  <div class="card-head">
    <span class="w-hanzi">{w["hanzi"]}</span>
    <span class="w-pinyin">{w["pinyin"]}</span>
    <button class="speak-btn" data-text="{w["hanzi"]}">🔊</button>
    <button class="speak-slow-btn" data-text="{w["hanzi"]}">🐢</button>
    <button class="del-btn" data-hanzi="{w["hanzi"]}" title="Delete">✕</button>
  </div>
  <ol class="examples">{examples_html}</ol>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Words</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: sans-serif; background: #f5f5f5; padding: 24px; }}
  .container {{ max-width: 800px; margin: 0 auto; }}
  header {{ display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }}
  header a {{ font-size: 14px; color: #555; text-decoration: none; }}
  header a:hover {{ color: #111; }}
  h1 {{ font-size: 20px; font-weight: bold; }}
  .grid {{ display: grid; gap: 16px; }}
  .card {{ background: white; border: 1px solid #ddd; border-radius: 10px; padding: 20px; }}
  .card-head {{ display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }}
  .w-hanzi {{ font-size: 28px; font-weight: bold; color: #111; }}
  .w-pinyin {{ font-size: 14px; color: #e07b00; }}
  .examples {{ padding-left: 18px; display: flex; flex-direction: column; gap: 10px; }}
  .examples li {{ font-size: 14px; line-height: 1.5; }}
  .ex-row {{ display: flex; align-items: center; gap: 6px; }}
  .ex-hanzi {{ color: #111; font-size: 16px; }}
  .ex-pinyin {{ display: block; color: #e07b00; font-size: 16px; }}
  .ex-trans {{ display: block; color: #777; font-size: 16px; }}
  .speak-btn, .speak-slow-btn {{ background: none; border: none; cursor: pointer; font-size: 14px; padding: 2px 4px; opacity: 0.6; }}
  .speak-btn:hover, .speak-slow-btn:hover {{ opacity: 1; }}
  .card-head {{ position: relative; }}
  .del-btn {{ margin-left: auto; background: none; border: none; cursor: pointer; font-size: 14px; color: #bbb; padding: 2px 4px; }}
  .del-btn:hover {{ color: #c0392b; }}
  .add-bar {{ position: fixed; bottom: 24px; right: 24px; display: flex; align-items: center; gap: 8px; background: white; border: 1px solid #ddd; border-radius: 12px; padding: 10px 14px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); }}
  .add-bar input {{ font-size: 18px; border: none; outline: none; width: 120px; background: transparent; }}
  .add-bar button {{ font-size: 13px; padding: 4px 10px; border-radius: 6px; border: 1px solid #ccc; background: #f5f5f5; cursor: pointer; }}
  .add-bar button:disabled {{ opacity: 0.5; cursor: default; }}
  .add-status {{ font-size: 12px; color: #888; }}
  .add-status.saved {{ color: #2a9d2a; }}
  .add-status.exists {{ color: #888; }}
  .add-status.err {{ color: #c0392b; }}
</style>
</head>
<body>
<div class="container">
<header>
  <a href="/">← Scenarios</a>
  <h1>Words</h1>
</header>
<div class="grid">
{cards}
</div>
</div>
<div class="add-bar">
  <input id="add-input" type="text" placeholder="汉字…" autocomplete="off">
  <button id="add-btn">Add</button>
  <span class="add-status" id="add-status"></span>
</div>
<script>
  function speak(text, rate) {{
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = 'zh-CN';
    utt.rate = rate || 0.8;
    speechSynthesis.cancel();
    speechSynthesis.speak(utt);
  }}
  document.querySelectorAll('.speak-btn').forEach(btn => {{
    btn.addEventListener('click', () => speak(btn.dataset.text));
  }});
  document.querySelectorAll('.speak-slow-btn').forEach(btn => {{
    btn.addEventListener('click', () => speak(btn.dataset.text, 0.4));
  }});

  document.querySelectorAll('.del-btn').forEach(btn => {{
    btn.addEventListener('click', async () => {{
      const hanzi = btn.dataset.hanzi;
      btn.disabled = true;
      const res = await fetch('/api/delete-word', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{hanzi}})
      }});
      const data = await res.json();
      if (data.status === 'deleted') {{
        btn.closest('.card').remove();
      }} else {{
        btn.disabled = false;
      }}
    }});
  }});

  const addInput = document.getElementById('add-input');
  const addBtn = document.getElementById('add-btn');
  const addStatus = document.getElementById('add-status');

  async function addWord() {{
    const hanzi = addInput.value.trim();
    if (!hanzi) return;
    addBtn.disabled = true;
    addBtn.textContent = 'Adding…';
    addStatus.textContent = '';
    addStatus.className = 'add-status';
    try {{
      const res = await fetch('/api/add-word', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{hanzi}})
      }});
      const data = await res.json();
      if (data.status === 'added') {{
        addStatus.textContent = 'Saved!';
        addStatus.classList.add('saved');
        addInput.value = '';
        setTimeout(() => location.reload(), 800);
      }} else if (data.status === 'exists') {{
        addStatus.textContent = 'Already saved';
        addStatus.classList.add('exists');
      }} else {{
        addStatus.textContent = data.message || 'Error';
        addStatus.classList.add('err');
      }}
    }} catch(e) {{
      addStatus.textContent = 'Error';
      addStatus.classList.add('err');
    }} finally {{
      addBtn.disabled = false;
      addBtn.textContent = 'Add';
    }}
  }}

  addBtn.addEventListener('click', addWord);
  addInput.addEventListener('keydown', e => {{ if (e.key === 'Enter') addWord(); }});
</script>
</body>
</html>"""


def render_html(scenario_name, words, show_pinyin, show_translation):
    options_html = "".join(
        f'<option value="{s}" {"selected" if s == scenario_name else ""}>{display_name(s)}</option>'
        for s in list_scenarios()
    )

    def render_word(w):
        if w["hanzi"] == "\n":
            return "<br>"
        return f"""<span class="word"><span class="pinyin">{w["pinyin"]}</span><span class="hanzi">{w["hanzi"]}</span><span class="translation">{w["translation"]}</span></span>"""

    cards_html = "".join(render_word(w) for w in words)

    pinyin_checked = "checked" if show_pinyin else ""
    trans_checked = "checked" if show_translation else ""

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chinese Lesson</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: sans-serif; background: #f5f5f5; padding: 24px; line-height: 1; width: 100%; }}
  .container {{ max-width: 800px; margin: 0 auto; }}
  header {{ display: flex; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 32px; }}
  header a {{ font-size: 14px; color: #555; text-decoration: none; }}
  header a:hover {{ color: #111; }}
  select {{ font-size: 14px; padding: 6px 10px; border-radius: 6px; border: 1px solid #ccc; }}
  button {{ font-size: 14px; padding: 6px 14px; border-radius: 6px; border: 1px solid #ccc; background: white; cursor: pointer; }}
  button:hover {{ background: #f0f0f0; }}
  .toggles {{ display: flex; gap: 16px; }}
  label {{ display: flex; align-items: center; gap: 6px; font-size: 14px; cursor: pointer; user-select: none; }}
  .text {{ font-size: 0; line-height: 1; }}
  .word {{
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    margin: 0 3px 8px;
    vertical-align: bottom;
  }}
  .hanzi {{ font-size: 28px; font-weight: bold; color: #111; }}
  .pinyin {{ display: none; font-size: 12px; color: #e07b00; margin-bottom: 2px; }}
  .translation {{ display: none; font-size: 11px; color: #888; margin-top: 2px; white-space: nowrap; }}
  .show-pinyin .pinyin {{ display: block; }}
  .show-translation .translation {{ display: block; }}
  .word {{ cursor: pointer; border: 1px solid #ddd; border-radius: 6px; padding: 4px 6px; background: white; }}
  .word:hover {{ border-color: #bbb; background: #fafafa; }}
  .popup-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 100; }}
  .popup-overlay.open {{ display: flex; align-items: center; justify-content: center; }}
  .popup {{ background: white; border-radius: 12px; padding: 28px 36px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.18); min-width: 200px; }}
  .popup-hanzi {{ font-size: 48px; font-weight: bold; color: #111; }}
  .popup-pinyin {{ font-size: 18px; color: #e07b00; margin-top: 8px; }}
  .popup-translation {{ font-size: 14px; color: #555; margin-top: 8px; }}
  .popup-actions {{ display: flex; gap: 10px; margin-top: 16px; justify-content: center; align-items: center; }}
  .popup-status {{ font-size: 12px; color: #888; }}
  .popup-status.saved {{ color: #4caf50; }}
  .popup-status.exists {{ color: #e07b00; }}
  .popup-status.error {{ color: #e53935; }}
</style>
</head>
<body>
<div class="container">
<header>
  <form method="get" action="/">
    <select name="scenario" onchange="this.form.submit()">
      {options_html}
    </select>
  </form>
  <div class="toggles">
    <label>
      <input type="checkbox" id="toggle-pinyin" {pinyin_checked}> Pinyin
    </label>
    <label>
      <input type="checkbox" id="toggle-translation" {trans_checked}> Translation
    </label>
  </div>
  <audio controls src="/audio/{scenario_name}.m4a"></audio>
  <a href="/words">Words →</a>
</header>
<div class="popup-overlay" id="overlay">
  <div class="popup">
    <div class="popup-hanzi" id="popup-hanzi"></div>
    <div class="popup-pinyin" id="popup-pinyin"></div>
    <div class="popup-translation" id="popup-translation"></div>
    <div class="popup-actions">
      <button id="popup-speak" style="font-size:18px; padding:6px 16px;">🔊</button>
      <button id="popup-save">＋ Save word</button>
      <span class="popup-status" id="popup-status"></span>
    </div>
  </div>
</div>
<div class="text">
{cards_html}
</div>
</div>
<script>
  const text = document.querySelector('.text');
  function apply() {{
    text.classList.toggle('show-pinyin', document.getElementById('toggle-pinyin').checked);
    text.classList.toggle('show-translation', document.getElementById('toggle-translation').checked);
  }}
  document.getElementById('toggle-pinyin').addEventListener('change', apply);
  document.getElementById('toggle-translation').addEventListener('change', apply);
  apply();

  const overlay = document.getElementById('overlay');
  const popupStatus = document.getElementById('popup-status');
  const popupSave = document.getElementById('popup-save');

  document.querySelectorAll('.word').forEach(word => {{
    word.addEventListener('click', () => {{
      document.getElementById('popup-hanzi').textContent = word.querySelector('.hanzi').textContent;
      document.getElementById('popup-pinyin').textContent = word.querySelector('.pinyin').textContent;
      document.getElementById('popup-translation').textContent = word.querySelector('.translation').textContent;
      popupStatus.textContent = '';
      popupStatus.className = 'popup-status';
      popupSave.disabled = false;
      popupSave.textContent = '＋ Save word';
      overlay.classList.add('open');
    }});
  }});
  overlay.addEventListener('click', e => {{
    if (!e.target.closest('.popup')) overlay.classList.remove('open');
  }});
  document.getElementById('popup-speak').addEventListener('click', () => {{
    const hanzi = document.getElementById('popup-hanzi').textContent;
    const utt = new SpeechSynthesisUtterance(hanzi);
    utt.lang = 'zh-CN';
    utt.rate = 0.8;
    speechSynthesis.cancel();
    speechSynthesis.speak(utt);
  }});

  popupSave.addEventListener('click', async () => {{
    const hanzi = document.getElementById('popup-hanzi').textContent;
    popupSave.disabled = true;
    popupSave.textContent = 'Saving…';
    popupStatus.textContent = '';
    popupStatus.className = 'popup-status';
    try {{
      const res = await fetch('/api/add-word', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{hanzi}})
      }});
      const data = await res.json();
      if (data.status === 'added') {{
        popupStatus.textContent = 'Saved!';
        popupStatus.classList.add('saved');
      }} else if (data.status === 'exists') {{
        popupStatus.textContent = 'Already saved';
        popupStatus.classList.add('exists');
      }} else {{
        popupStatus.textContent = 'Error';
        popupStatus.classList.add('error');
      }}
    }} catch (e) {{
      popupStatus.textContent = 'Error';
      popupStatus.classList.add('error');
    }}
    popupSave.textContent = '＋ Save word';
  }});

</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == "/api/add-word":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            hanzi = body.get("hanzi", "").strip()
            if not hanzi:
                self._send_json({"status": "error", "message": "no hanzi"}, 400)
                return
            if word_exists(hanzi):
                self._send_json({"status": "exists"})
                return
            try:
                data = generate_word_data(hanzi)
                save_word(hanzi, data["pinyin"], data["examples"])
                self._send_json({"status": "added"})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        elif self.path == "/api/import-words":
            try:
                inserted, skipped = import_words_json()
                self._send_json({"status": "ok", "inserted": inserted, "skipped": skipped})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        elif self.path == "/api/delete-word":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            hanzi = body.get("hanzi", "").strip()
            if not hanzi:
                self._send_json({"status": "error", "message": "no hanzi"}, 400)
                return
            try:
                with get_conn() as conn, conn.cursor() as cur:
                    cur.execute(
                        "UPDATE words SET deleted_at = NOW() WHERE hanzi = %s AND deleted_at IS NULL RETURNING id",
                        (hanzi,),
                    )
                    updated = cur.fetchone()
                    conn.commit()
                if updated:
                    self._send_json({"status": "deleted"})
                else:
                    self._send_json({"status": "not_found"}, 404)
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path.startswith("/audio/"):
            audio_path = os.path.join(AUDIO_DIR, os.path.basename(parsed.path))
            if not os.path.exists(audio_path):
                self.send_response(404)
                self.end_headers()
                return
            size = os.path.getsize(audio_path)
            range_header = self.headers.get("Range")
            if range_header:
                start, end = range_header.replace("bytes=", "").split("-")
                start = int(start)
                end = int(end) if end else size - 1
                length = end - start + 1
                with open(audio_path, "rb") as f:
                    f.seek(start)
                    data = f.read(length)
                self.send_response(206)
                self.send_header("Content-Type", "audio/mp4")
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                self.wfile.write(data)
            else:
                with open(audio_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "audio/mp4")
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                self.wfile.write(data)
            return

        if parsed.path == "/words":
            html = render_words_html(load_words())
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        scenarios = sorted(list_scenarios())
        scenario_name = qs.get("scenario", [scenarios[0]])[0]
        show_pinyin = qs.get("pinyin", ["0"])[0] != "0"
        show_translation = qs.get("translation", ["0"])[0] != "0"

        try:
            words = load_scenario(scenario_name)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return

        html = render_html(scenario_name, words, show_pinyin, show_translation)
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("", port), Handler)
    print(f"http://localhost:{port}")
    server.serve_forever()
