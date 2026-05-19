def render(words):
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
  <a href="/flashcards">Flashcards →</a>
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
