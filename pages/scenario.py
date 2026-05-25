import json
import os

PARSED_DIR = os.path.join(os.path.dirname(__file__), "..", "transcription-parsed")


def load_scenario(name):
    path = os.path.join(PARSED_DIR, f"{name}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_scenarios():
    return sorted(f[:-5] for f in os.listdir(PARSED_DIR) if f.endswith(".json"))


def display_name(scenario_name):
    parts = scenario_name.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit():
        return f"{parts[0]} - {parts[1]}"
    return scenario_name


def render(scenario_name, words, show_pinyin, show_translation):
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
  .container {{ max-width: 800px; margin: 0 auto; display: flex; display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 20px 0px; }}
  header {{ display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
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
    margin: 0 2px 18px;
    vertical-align: bottom;
    cursor: pointer;
  }}
  .hanzi {{ font-size: 28px; font-weight: bold; color: #111; border-bottom: 2px solid #ddd; }}
  .word:hover .hanzi {{ border-color: #888; }}
  .pinyin {{ display: none; font-size: 12px; color: #e07b00; margin-bottom: 2px; }}
  .translation {{ display: none; font-size: 11px; color: #888; margin-top: 4px; white-space: nowrap; }}
  .show-pinyin .pinyin {{ display: block; }}
  .show-translation .translation {{ display: block; }}
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
  <a href="/words">Words →</a>
</header>
<audio controls src="/transcription-audio/{scenario_name}.m4a"></audio>
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
<div class="add-bar">
  <input id="add-input" type="text" placeholder="汉字…" autocomplete="off">
  <button id="add-btn">Add</button>
  <span class="add-status" id="add-status"></span>
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
        setTimeout(() => {{ addStatus.textContent = ''; addStatus.className = 'add-status'; }}, 2000);
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
