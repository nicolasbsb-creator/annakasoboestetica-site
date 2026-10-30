#!/usr/bin/env python3
"""Gera o Blog do site Anna Kasobo Estética Avançada.

Fonte de verdade: blog/_fonte/*.json (um arquivo por texto).
Saída: blog/<slug>.html, blog/index.html, blog/posts.json e sitemap.xml.
Pastas/arquivos iniciados por "_" não são publicados pelo GitHub Pages.

Uso:  python3 _tools/blog_build.py
"""
import json, os, re, html, datetime, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.annakasoboestetica.com"
WA = "https://wa.me/message/2LP544542QRXH1"
MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
LOGO = open(os.path.join(ROOT, "_tools", "logo.svg.txt"), encoding="utf-8").read()
ALLOWED = {"p","h2","h3","ul","ol","li","strong","em","b","i","blockquote","a","br"}

def data_br(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month-1]} de {d.year}"

def check_body(body, slug):
    tags = set(t.lower() for t in re.findall(r"</?([a-zA-Z0-9]+)", body))
    bad = tags - ALLOWED
    if bad:
        sys.exit(f"[{slug}] tags não permitidas no corpo: {sorted(bad)}")
    if re.search(r"<script|on\w+=", body, re.I):
        sys.exit(f"[{slug}] conteúdo inseguro no corpo")

def minutos(body):
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return max(2, round(words / 200))

CSS = """
:root{--cacau:#413131;--bordo:#840000;--terracota:#BE6142;--rose:#CD928C;--nude:#EFC2BD;--creme:#F6E3C9;--creme-claro:#FBF1E4;--cacau-soft:#5a4646;
--display:"Cormorant Garamond",Garamond,"Times New Roman",serif;--body:"Jost","Helvetica Neue",Arial,sans-serif;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--creme-claro);color:var(--cacau);font-family:var(--body);font-weight:300;font-size:17px;line-height:1.75;-webkit-font-smoothing:antialiased}
a{color:var(--bordo)}
:focus-visible{outline:2px solid var(--bordo);outline-offset:3px}
.wrap{max-width:780px;margin-inline:auto;padding-inline:clamp(16px,4vw,40px)}
.wide{max-width:1180px}
header.top{border-bottom:1px solid rgba(205,146,140,.45);background:var(--creme-claro);position:sticky;top:0;z-index:5}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:16px}
.logo{width:84px;height:auto;display:block}
.nav-links{display:flex;gap:10px;align-items:center}
.pill{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;text-decoration:none;color:var(--cacau);border:1px solid var(--rose);border-radius:999px;padding:10px 16px;white-space:nowrap}
.pill:hover{background:var(--cacau);color:var(--creme);border-color:var(--cacau)}
.pill.solid{background:var(--bordo);border-color:var(--bordo);color:var(--creme)}
.pill.solid:hover{background:var(--cacau);border-color:var(--cacau)}
@media (max-width:560px){.pill.hide-sm{display:none}.pill{padding:9px 12px;font-size:.66rem;letter-spacing:.1em}.logo{width:66px}}
.hero{background:var(--nude);padding-block:clamp(44px,8vw,86px)}
.eyebrow{font-size:.74rem;font-weight:500;letter-spacing:.24em;text-transform:uppercase;color:var(--terracota);display:flex;align-items:center;gap:14px;margin:0}
.eyebrow::before{content:"";width:34px;height:1px;background:currentColor}
h1,h2,h3{font-family:var(--display);font-weight:500;line-height:1.12;margin:0;letter-spacing:-.01em;text-wrap:balance}
h1{font-size:clamp(2.3rem,5.6vw,3.6rem);margin-top:16px}
h1 em{font-style:italic;color:var(--bordo)}
.meta{margin-top:16px;font-size:.88rem;color:var(--cacau-soft);display:flex;flex-wrap:wrap;gap:6px 16px}
.lead{margin-top:18px;font-size:1.12rem;max-width:58ch}
article{padding-block:clamp(36px,6vw,70px)}
article h2{font-size:clamp(1.7rem,3.2vw,2.2rem);margin:42px 0 12px}
article h3{font-size:1.4rem;margin:28px 0 8px}
article p{margin:0 0 16px}
article ul,article ol{margin:0 0 16px;padding-left:1.2em}
article li{margin-bottom:8px}
article li::marker{color:var(--terracota)}
article blockquote{margin:26px 0;padding:18px 24px;border-left:3px solid var(--terracota);background:var(--creme);border-radius:0 16px 16px 0;font-family:var(--display);font-size:1.35rem;line-height:1.35;font-style:italic}
.author{display:grid;grid-template-columns:auto 1fr;gap:18px;align-items:center;margin-top:44px;padding:24px;background:var(--creme);border-radius:20px}
.author svg{width:56px;height:56px}
.author b{font-family:var(--display);font-size:1.3rem;font-weight:500}
.author small{display:block;color:var(--cacau-soft);font-size:.85rem}
.cta{margin-top:26px;padding:clamp(26px,4vw,38px);background:var(--cacau);color:var(--creme);border-radius:22px;display:grid;gap:14px}
.cta h3{font-size:clamp(1.5rem,3vw,1.9rem)}
.cta a{justify-self:start;background:var(--creme);color:var(--bordo);text-decoration:none;font-size:.78rem;font-weight:500;letter-spacing:.16em;text-transform:uppercase;padding:14px 22px;border-radius:999px}
.sources{margin-top:36px;font-size:.88rem;color:var(--cacau-soft)}
.sources ol{padding-left:1.2em}
.note{margin-top:22px;font-size:.84rem;color:var(--cacau-soft);border-top:1px solid rgba(205,146,140,.4);padding-top:16px}
.more{margin-top:44px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;margin-top:18px}
.card{display:grid;gap:10px;align-content:start;background:var(--creme);border-radius:20px;padding:24px;text-decoration:none;color:var(--cacau);transition:transform .25s,box-shadow .25s}
.card:hover{transform:translateY(-3px);box-shadow:0 18px 36px -24px rgba(65,49,49,.55)}
.card .cat{font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:var(--terracota);font-weight:500}
.card h3{font-size:1.45rem}
.card p{margin:0;font-size:.95rem;color:var(--cacau-soft)}
.card small{color:var(--cacau-soft);font-size:.8rem}
.list{padding-block:clamp(36px,6vw,70px)}
.featured{display:grid;gap:12px;background:var(--cacau);color:var(--creme);border-radius:24px;padding:clamp(26px,5vw,48px);text-decoration:none;margin-bottom:26px}
.featured .cat{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--rose);font-weight:500}
.featured h2{font-size:clamp(1.9rem,4vw,2.8rem)}
.featured p{margin:0;color:rgba(246,227,201,.82);max-width:62ch}
.featured span.go{font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;color:var(--nude)}
footer{background:#342727;color:rgba(246,227,201,.7);padding-block:30px;font-size:.82rem;margin-top:20px}
footer .wrap{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px 30px}
footer a{color:inherit;text-decoration:none;border-bottom:1px solid rgba(205,146,140,.5)}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Jost:wght@300;400;500&display=swap">')

MONO = '<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="47" fill="none" stroke="#BE6142" stroke-width="2"/><text x="50" y="62" text-anchor="middle" font-family="Cormorant Garamond,serif" font-style="italic" font-size="38" fill="#840000">AK</text></svg>'

def header(rel):
    return (f'<header class="top"><div class="wrap wide"><a href="{rel}" aria-label="Página inicial">{LOGO}</a>'
            f'<nav class="nav-links" aria-label="Blog"><a class="pill hide-sm" href="{rel}blog/">Blog</a>'
            f'<a class="pill solid" href="{WA}" target="_blank" rel="noopener">Agendar</a></nav></div></header>')

def footer(rel):
    return (f'<footer><div class="wrap wide"><span>© {datetime.date.today().year} Anna Kasobo Estética Avançada · CNPJ 43.445.315/0001-55 · Brasília – DF</span>'
            f'<span>Responsável técnica: Dra. Anna Kasobo · COREN nº 516.318</span>'
            f'<a href="{rel}privacidade.html">Política de Privacidade</a></div></footer>')

def card(p, rel=""):
    return (f'<a class="card" href="{rel}{p["slug"]}.html"><span class="cat">{html.escape(p["category"])}</span>'
            f'<h3>{html.escape(p["title"])}</h3><p>{html.escape(p["summary"])}</p>'
            f'<small>{data_br(p["date"])} · {p["read_min"]} min de leitura</small></a>')

def page(title, desc, canonical, body, extra_head=""):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="article">
<meta property="og:locale" content="pt_BR">
{FONTS}
<style>{CSS}</style>
{extra_head}
</head>
<body>
{body}
<script>/* Metricool: só para quem aceitou os cookies no site (LGPD) */
try{{if(localStorage.getItem('ak_consent')==='sim'){{var i=new Image(1,1);i.alt='';i.src='https://tracker.metricool.com/c3po.jpg?hash=cfef056ff1777595951f0740a65c2356';}}}}catch(e){{}}</script>
</body>
</html>
"""

def build():
    posts = []
    for f in sorted(glob.glob(os.path.join(ROOT, "blog", "_fonte", "*.json"))):
        p = json.load(open(f, encoding="utf-8"))
        for k in ("slug","title","date","category","summary","body"):
            if not p.get(k): sys.exit(f"{f}: campo obrigatório ausente: {k}")
        if not re.fullmatch(r"[a-z0-9-]+", p["slug"]): sys.exit(f"{f}: slug inválido")
        check_body(p["body"], p["slug"])
        p["read_min"] = minutos(p["body"])
        posts.append(p)
    today = datetime.date.today().isoformat()
    posts = [p for p in posts if p["date"] <= today]
    posts.sort(key=lambda p: (p["date"], p.get("order", 0)), reverse=True)
    out = os.path.join(ROOT, "blog")

    for i, p in enumerate(posts):
        others = [q for q in posts if q["slug"] != p["slug"]][:3]
        src = ""
        if p.get("sources"):
            items = "".join(f'<li><a href="{html.escape(s["url"])}" target="_blank" rel="noopener">{html.escape(s["title"])}</a></li>' for s in p["sources"])
            src = f'<div class="sources"><b>Fontes consultadas</b><ol>{items}</ol></div>'
        more = ""
        if others:
            more = f'<section class="more"><p class="eyebrow">Continue lendo</p><div class="cards">{"".join(card(q) for q in others)}</div></section>'
        ld = json.dumps({"@context":"https://schema.org","@type":"BlogPosting","headline":p["title"],"description":p["summary"],
              "datePublished":p["date"],"inLanguage":"pt-BR","mainEntityOfPage":f'{SITE}/blog/{p["slug"]}.html',
              "author":{"@type":"Organization","name":"Anna Kasobo Estética Avançada"},
              "publisher":{"@type":"Organization","name":"Anna Kasobo Estética Avançada"}}, ensure_ascii=False)
        body = f"""{header('../')}
<div class="hero"><div class="wrap">
  <p class="eyebrow">{html.escape(p["category"])}</p>
  <h1>{html.escape(p["title"])}</h1>
  <p class="lead">{html.escape(p["summary"])}</p>
  <div class="meta"><span>{data_br(p["date"])}</span><span>{p["read_min"]} min de leitura</span><span>Por Equipe Anna Kasobo</span></div>
</div></div>
<main class="wrap"><article>
{p["body"]}
<div class="author">{MONO}<div><b>Equipe Anna Kasobo</b><small>Clínica da Dra. Anna Kasobo, enfermeira esteta (COREN nº 516.318), especialista em harmonização corporal em Brasília</small></div></div>
<div class="cta"><h3>Quer saber o que funciona para o seu corpo?</h3><p style="margin:0">Cada caso é avaliado individualmente na consulta estética personalizada.</p><a href="{WA}" target="_blank" rel="noopener">Agendar pelo WhatsApp</a></div>
{src}
<p class="note">Conteúdo informativo. Não substitui a avaliação individual de um profissional habilitado. Indicações, número de sessões e resultados variam de pessoa para pessoa.</p>
{more}
</article></main>
{footer('../')}"""
        open(os.path.join(out, f'{p["slug"]}.html'), "w", encoding="utf-8").write(
            page(f'{p["title"]} · Blog Anna Kasobo', p["summary"], f'{SITE}/blog/{p["slug"]}.html', body,
                 f'<script type="application/ld+json">{ld}</script>'))

    feat = ""
    rest = posts
    if posts:
        f0 = posts[0]
        feat = (f'<a class="featured" href="{f0["slug"]}.html"><span class="cat">Mais recente · {html.escape(f0["category"])}</span>'
                f'<h2>{html.escape(f0["title"])}</h2><p>{html.escape(f0["summary"])}</p>'
                f'<span class="go">Ler agora →</span></a>')
        rest = posts[1:]
    grid = f'<div class="cards">{"".join(card(p) for p in rest)}</div>' if rest else ""
    empty = "" if posts else "<p>Em breve, novos textos por aqui.</p>"
    body = f"""{header('../')}
<div class="hero"><div class="wrap wide">
  <p class="eyebrow">Blog</p>
  <h1>Estética <em>sem mistério</em></h1>
  <p class="lead">Textos curtos e diretos sobre procedimentos não invasivos, cuidados e o que a ciência diz, escritos para quem quer decidir com informação. Novo texto de segunda a sexta.</p>
</div></div>
<main class="wrap wide list">{feat}{grid}{empty}</main>
{footer('../')}"""
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(
        page("Blog · Anna Kasobo Estética Avançada", "Estética sem mistério: textos sobre procedimentos não invasivos, cuidados e resultados, da clínica da Dra. Anna Kasobo.", f"{SITE}/blog/", body))

    meta = [{k: p[k] for k in ("slug","title","date","category","summary","read_min")} for p in posts]
    json.dump(meta, open(os.path.join(out, "posts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    urls = [f"{SITE}/", f"{SITE}/kasobo-sculpt/", f"{SITE}/blog/", f"{SITE}/privacidade.html"] + [f'{SITE}/blog/{p["slug"]}.html' for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    print(f"OK: {len(posts)} texto(s) publicados")

if __name__ == "__main__":
    build()
