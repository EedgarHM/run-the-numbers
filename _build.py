# Genera las páginas de episodio y el sitemap del sitio a partir de episodios.json.
# Uso: python sitio/_build.py   (después, git add/commit/push dentro de sitio/)
import json, html, pathlib
from datetime import date

ROOT = pathlib.Path(__file__).parent
BASE = "https://eedgarhm.github.io/run-the-numbers/"
SERIES = {"taxes": ("Taxes", "var(--taxes)"), "debt": ("Debt", "var(--debt)"), "retirement": ("Retirement", "var(--retire)"),
          "credit": ("Credit", "var(--credit)"), "income": ("Income", "var(--income)"), "housing": ("Housing", "var(--housing)"),
          "health": ("Health", "var(--health)")}
H = html.escape

def page(ep):
    name, color = SERIES[ep["series"]]
    url = BASE + f"episodes/{ep['slug']}.html"
    faq = "".join(f"<details><summary>{H(q)}</summary><p>{H(a)}</p></details>" for q, a in ep["faq"])
    srcs = "".join(f'<li>{H(t)}: <a href="{H(u)}">{H(u.split("/")[2])}</a></li>' for t, u in ep["sources"])
    takeaways = "".join(f"<li>{t}</li>" for t in ep["takeaways"])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "VideoObject", "name": ep["title"], "description": ep["description"],
         "thumbnailUrl": [BASE + ep["og"]], "uploadDate": ep["upload"],
         "embedUrl": f"https://www.youtube.com/embed/{ep['yt']}", "contentUrl": f"https://www.youtube.com/watch?v={ep['yt']}"},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in ep["faq"]]}]}
    calc = (f'<div class="box"><b>Run your own numbers</b><p class="note" style="margin:6px 0 0">{H(ep["calc"][1])}</p>'
            f'<a class="btn yt" style="background:var(--c);color:#15171C;box-shadow:none" href="../calculators/{ep["calc"][0]}">Open the calculator →</a></div>') if ep.get("calc") else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H(ep['title'])} | Run the Numbers</title>
<meta name="description" content="{H(ep['description'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="video.other"><meta property="og:title" content="{H(ep['title'])}"><meta property="og:description" content="{H(ep['description'])}">
<meta property="og:image" content="{BASE + ep['og']}"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0E1116">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body style="--c:{color}">
<header class="bar"><div class="wrap"><a class="logo" href="../">RUN THE <b>NUMBERS</b></a>
<nav><a class="hide-sm" href="../#videos">Videos</a><a class="hide-sm" href="../#calculators">Calculators</a><a class="btn yt" href="https://www.youtube.com/@RunTheNumbersO?sub_confirmation=1">Subscribe</a></nav></div></header>
<div class="page-hero"><div class="wrap"><div class="crumb"><a href="../">Home</a> · <span class="tag">{name}</span></div><h1>{H(ep['title'])}</h1></div></div>
<div class="wrap">
<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{ep['yt']}" title="{H(ep['title'])}" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
<div class="cols"><div>
 <div class="eyebrow">The short answer</div>
 <p class="answer">{ep['answer']}</p>
 <h2 style="font-size:28px;margin-top:34px">Key numbers</h2><ul>{takeaways}</ul>
 {ep.get('extra','')}
 <h2 style="font-size:28px;margin-top:34px">Questions people ask</h2>{faq}
 <h2 style="font-size:28px;margin-top:34px">Assumptions</h2><p class="note">{H(ep['assumptions'])}</p>
 <h2 style="font-size:28px;margin-top:34px">Sources</h2><ul class="src">{srcs}</ul>
</div><aside class="side">{calc}
 <div class="box"><b>Like this?</b><p class="note" style="margin:6px 0 0">A new money question three times a week, plus a short every day.</p><a class="btn yt" href="https://www.youtube.com/@RunTheNumbersO?sub_confirmation=1">▶ Subscribe</a></div>
</aside></div></div>
<footer class="site" style="margin-top:64px"><div class="wrap">Education, not financial advice · Examples use fictional people · Narration voice is AI-generated · <a href="../">More videos and calculators</a></div></footer>
</body></html>"""

eps = json.loads((ROOT / "episodios.json").read_text(encoding="utf-8"))
for ep in eps:
    (ROOT / "episodes" / f"{ep['slug']}.html").write_text(page(ep), encoding="utf-8")
urls = [""] + [f"episodes/{e['slug']}.html" for e in eps] + [f"calculators/{p.name}" for p in sorted((ROOT / "calculators").glob("*.html"))]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{date.today()}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
print("páginas:", len(eps), "· urls en sitemap:", len(urls))
