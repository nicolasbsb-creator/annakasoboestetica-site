#!/usr/bin/env python3
"""Gera index.html (home leve) e kasobo-sculpt/index.html a partir da fonte única
(o HTML com imagens embutidas usado na pré-visualização).

Uso: python3 _tools/build_site.py CAMINHO_DA_FONTE.html
As imagens embutidas (base64) viram arquivos em img/ e as páginas passam a
referenciá-las, com carregamento preguiçoso.
"""
import base64, html as H, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.annakasoboestetica.com'
WA = 'https://wa.me/message/2LP544542QRXH1'

src = open(sys.argv[1], encoding='utf-8').read()

# ---------- 1. imagens embutidas -> arquivos ----------
NOMES = ['dra-anna-kasobo.jpg', 'nutraceuticos-anna-kasobo.jpg', 'dra-anna-avaliacao.jpg']
for caso in ['sculpt-abdomen', 'sculpt-flancos', 'sculpt-costas', '180-abdomen', '180-abdomen-2',
             'slim-abdomen', 'facial-papada', 'facial-pele']:
    NOMES += [f'resultados/{caso}-antes.jpg', f'resultados/{caso}-depois.jpg']
uris = re.findall(r'data:image/jpeg;base64,[A-Za-z0-9+/=]+', src)
assert len(uris) == len(NOMES), (len(uris), len(NOMES))
os.makedirs(os.path.join(ROOT, 'img', 'resultados'), exist_ok=True)
for u, n in zip(uris, NOMES):
    with open(os.path.join(ROOT, 'img', n), 'wb') as f:
        f.write(base64.b64decode(u.split(',', 1)[1]))
def com_arquivos(texto, prefixo):
    for u, n in zip(uris, NOMES):
        texto = texto.replace(u, prefixo + 'img/' + n)
    return texto

# ---------- 2. separar o que vai no <head> ----------
corte = src.index('\n<svg')
topo, corpo = src[:corte], src[corte + 1:]
topo = re.sub(r'<title>.*?</title>\s*', '', topo, flags=re.S)
estilo = re.search(r'<style>(.*?)</style>', topo, re.S).group(1)
fontes = topo[:topo.index('<style>')]

FAQ = json.load(open(os.path.join(ROOT, '_tools', 'faq.json'), encoding='utf-8'))

NEGOCIO = {
    "@context": "https://schema.org",
    "@type": "HealthAndBeautyBusiness",
    "@id": SITE + "/#clinica",
    "name": "Anna Kasobo Estética Avançada",
    "legalName": "43.445.315 Anna Karolina Soares Borges",
    "taxID": "43.445.315/0001-55",
    "url": SITE + "/",
    "image": SITE + "/img/og-anna-kasobo.jpg",
    "logo": SITE + "/img/favicon-512.png",
    "telephone": "+55 61 99594-6554",
    "address": {"@type": "PostalAddress",
                "streetAddress": "SCN Quadra 2, Bloco D, Liberty Mall, Torre B, Sala 729, Asa Norte",
                "addressLocality": "Brasília", "addressRegion": "DF",
                "postalCode": "70712-904", "addressCountry": "BR"},
    "geo": {"@type": "GeoCoordinates", "latitude": -15.7868693, "longitude": -47.8842686},
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification",
         "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
         "opens": "09:00", "closes": "20:00"},
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday",
         "opens": "09:00", "closes": "14:00"}],
    "sameAs": ["https://www.instagram.com/draannakasobo/",
               "https://www.facebook.com/AnnaKasoboEstetica/"]
}
FAQ_LD = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q,
                          "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}

def head(titulo, desc, url, og, extra_ld, prefixo, css_extra=''):
    lds = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>\n'
                  for x in extra_ld)
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{H.escape(titulo)}</title>
<meta name="description" content="{H.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#413131">
<meta name="facebook-domain-verification" content="yk5st4zi053ulisycx8pppvm3vg4m7">
<link rel="icon" type="image/png" sizes="48x48" href="{prefixo}img/favicon-48.png">
<link rel="icon" type="image/png" sizes="512x512" href="{prefixo}img/favicon-512.png">
<link rel="apple-touch-icon" href="{prefixo}img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Anna Kasobo Estética Avançada">
<meta property="og:title" content="{H.escape(titulo)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{H.escape(titulo)}">
<meta name="twitter:description" content="{H.escape(desc)}">
<meta name="twitter:image" content="{SITE}/img/{og}">
<link rel="preload" as="image" href="{prefixo}img/{'dra-anna-kasobo.jpg' if not prefixo else 'dra-anna-avaliacao.jpg'}">
{fontes.strip()}
<style>{estilo}{css_extra}</style>
{lds}</head>
<body>
'''

# ---------- 3. home ----------
home_corpo = com_arquivos(corpo, '')
home = head('Anna Kasobo Estética Avançada | Harmonização corporal em Brasília',
            'Estética avançada e harmonização corporal em Brasília (Asa Norte). Protocolo exclusivo '
            'Kasobo Sculpt, Kasobo 180º e Kasobo Slim. Agende sua consulta estética personalizada.',
            SITE + '/', 'og-anna-kasobo.jpg', [NEGOCIO, FAQ_LD], '') + home_corpo.rstrip() + '\n</body>\n</html>\n'
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(home)

# ---------- 4. página do Kasobo Sculpt ----------
def bloco(regex):
    m = re.search(regex, corpo, re.S)
    assert m, regex
    return m.group(0)

defs = bloco(r'<svg[^>]*>\s*<defs>.*?</defs>\s*</svg>')
header = bloco(r'<header>.*?</header>')
header = re.sub(r'(<a\b[^>]*?)href="#([a-z-]+)"', r'\1href="../#\2"', header).replace('href="../#inicio"', 'href="../"')
sculpt = bloco(r'<section class="sculpt" id="kasobo-sculpt">.*?</section>')
sculpt = re.sub(r'\s*<a class="btn btn-ghost" href="[^"]*kasobo-sculpt/">.*?</a>', '', sculpt)
sculpt = sculpt.replace('<h2>Kasobo Sculpt<span>remodelagem sob medida</span></h2>',
                        '<h2>Como funciona<span>três etapas, um protocolo seu</span></h2>')
assinaturas = bloco(r'<section class="signatures">.*?</section>').replace(
    'Protocolos exclusivos Kasobo', 'Outros protocolos Kasobo')
resultados = bloco(r'<section class="results" id="antes-e-depois">.*?</section>').replace(
    'Resultados de pacientes reais', 'Resultados do Kasobo Sculpt')
consulta = bloco(r'<section class="consulta" id="consulta">.*?</section>')
sobre = bloco(r'<section class="about" id="sobre">.*?</section>')
faq = bloco(r'<section class="faq" id="duvidas".*?</section>')
contato = bloco(r'<section class="contact" id="contato">.*?</section>')
rodape = bloco(r'<footer>.*?</footer>').replace('href="privacidade.html"', 'href="../privacidade.html"')
flutuante = bloco(r'<a class="float".*?</a>')
aviso = bloco(r'<div class="consent".*?</div>\s*</div>').replace('href="privacidade.html"', 'href="../privacidade.html"')
scripts = re.findall(r'<script>.*?</script>', corpo, re.S)
medicao = next(s for s in scripts if 'MEDIÇÃO' in s)
antes_depois = next(s for s in scripts if 'var RESULTADOS' in s)
antes_depois = re.sub(r"\n  \{ tratamento:'(?!Kasobo Sculpt)[^\n]*", '', antes_depois)
antes_depois = re.sub(r",\n\];", "\n];", antes_depois)
mapa = next(s for s in scripts if 'map-load' in s)

hero = f'''  <section class="hero lp-hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow reveal">Protocolo exclusivo · Asa Norte, Brasília</p>
        <h1 class="reveal d2">Kasobo Sculpt: remodelagem <em>sob medida.</em></h1>
        <p class="lede reveal d3">Remodelagem não invasiva da gordura localizada e do contorno corporal, montada para o seu corpo e com cada etapa acompanhada de perto pela Dra. Anna.</p>
        <div class="hero-actions reveal d3">
          <a class="btn btn-primary" href="{WA}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#wa"/></svg>Agendar minha avaliação</a>
          <a class="btn btn-ghost" href="#antes-e-depois">Ver resultados</a>
        </div>
        <div class="hero-meta">
          <span><i></i>Não invasivo</span>
          <span><i></i>Dra. Anna Kasobo · COREN nº 516.318</span>
          <span><i></i>Liberty Mall · Asa Norte</span>
        </div>
      </div>
      <figure class="about-photo reveal d2">
        <div class="about-frame"><img src="../img/dra-anna-avaliacao.jpg" alt="Dra. Anna Kasobo realizando avaliação de medidas corporais com adipômetro" width="1000" height="905" fetchpriority="high"></div>
      </figure>
    </div>
  </section>
'''
css_lp = '''
.lp-hero h1{font-size:clamp(2.7rem,6.2vw,5.2rem)}
.lp-hero .about-photo{max-width:500px}
'''
corpo_lp = f'''{defs}

{header}

<main id="inicio">
{hero}
  {sculpt}

  {resultados}

  {consulta}

  {assinaturas}

  {sobre}

{faq}

  {contato}
</main>

{rodape}

{flutuante}

{aviso}

{medicao}

{antes_depois}

{mapa}
'''
corpo_lp = com_arquivos(corpo_lp, '../')
lp = head('Kasobo Sculpt | Remodelagem corporal não invasiva em Brasília',
          'Kasobo Sculpt: protocolo exclusivo e não invasivo da Dra. Anna Kasobo para gordura localizada e '
          'contorno corporal, montado para o seu corpo. Liberty Mall, Asa Norte, Brasília.',
          SITE + '/kasobo-sculpt/', 'og-kasobo-sculpt.jpg', [NEGOCIO, FAQ_LD], '../', css_lp) + corpo_lp + '</body>\n</html>\n'
os.makedirs(os.path.join(ROOT, 'kasobo-sculpt'), exist_ok=True)
open(os.path.join(ROOT, 'kasobo-sculpt', 'index.html'), 'w', encoding='utf-8').write(lp)
print('home', len(home) // 1024, 'KB | sculpt', len(lp) // 1024, 'KB')
