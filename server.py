#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PARSED_DIR = os.path.join(os.path.dirname(__file__), "scenarios-parsed")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")


def load_scenario(name):
    path = os.path.join(PARSED_DIR, f"{name}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_scenarios():
    return [f[:-5] for f in os.listdir(PARSED_DIR) if f.endswith(".json")]


def render_html(scenario_name, words, show_pinyin, show_translation):
    options_html = "".join(
        f'<option value="{s}" {"selected" if s == scenario_name else ""}>{s}</option>'
        for s in sorted(list_scenarios())
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
  select {{ font-size: 14px; padding: 6px 10px; border-radius: 6px; border: 1px solid #ccc; }}
  button {{ font-size: 14px; padding: 6px 14px; border-radius: 6px; border: 1px solid #ccc; background: white; cursor: pointer; }}
  button:hover {{ background: #f0f0f0; }}
  button.playing {{ background: #fff3e0; border-color: #e07b00; color: #e07b00; }}
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
  <button id="btn-read">▶ Play</button>
</header>
<audio id="audio" src="/audio/{scenario_name}.m4a"></audio>
<div class="popup-overlay" id="overlay">
  <div class="popup">
    <div class="popup-hanzi" id="popup-hanzi"></div>
    <div class="popup-pinyin" id="popup-pinyin"></div>
    <div class="popup-translation" id="popup-translation"></div>
    <button id="popup-speak" style="margin-top:16px; font-size:18px; padding:6px 16px;">🔊</button>
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
  document.querySelectorAll('.word').forEach(word => {{
    word.addEventListener('click', () => {{
      document.getElementById('popup-hanzi').textContent = word.querySelector('.hanzi').textContent;
      document.getElementById('popup-pinyin').textContent = word.querySelector('.pinyin').textContent;
      document.getElementById('popup-translation').textContent = word.querySelector('.translation').textContent;
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

  const audio = document.getElementById('audio');
  const btn = document.getElementById('btn-read');
  btn.addEventListener('click', () => {{
    if (audio.paused) {{
      audio.play();
      btn.textContent = '■ Pause';
      btn.classList.add('playing');
    }} else {{
      audio.pause();
      btn.textContent = '▶ Resume';
      btn.classList.remove('playing');
    }}
  }});
  audio.onended = () => {{
    audio.currentTime = 0;
    btn.textContent = '▶ Play';
    btn.classList.remove('playing');
  }};
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path.startswith("/audio/"):
            audio_path = os.path.join(AUDIO_DIR, os.path.basename(parsed.path))
            if not os.path.exists(audio_path):
                self.send_response(404)
                self.end_headers()
                return
            with open(audio_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "audio/mp4")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
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
