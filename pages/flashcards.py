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
  </div>
  <ol class="examples">{examples_html}</ol>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flashcards</title>
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
  .shuffle-btn {{ margin-left: auto; font-size: 13px; padding: 6px 12px; border-radius: 6px; border: 1px solid #ccc; background: white; cursor: pointer; }}
  .shuffle-btn:hover {{ background: #f0f0f0; }}
</style>
</head>
<body>
<div class="container">
<header>
  <a href="/">← Scenarios</a>
  <h1>Flashcards</h1>
  <a href="/flashcards" class="shuffle-btn">Shuffle</a>
</header>
<div class="grid">
{cards}
</div>
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
</script>
</body>
</html>"""
