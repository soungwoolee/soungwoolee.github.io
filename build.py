"""개인 홈페이지 빌드. src/ 자산 + career_site 템플릿 + posts/*.md → docs/ (GitHub Pages가 docs 폴더를 서빙)

실행: python3 build.py
- docs/index.html            홈 (소개, 최근 글, Work, Side)
- docs/writing/index.html    글 목록
- docs/writing/<slug>/       글 하나
- docs/why/anthropic/, docs/why/palantir/   지원용 페이지 (메뉴에 없음, 검색 제외)
"""
import html, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAREER = ROOT.parent / "career_site"
OUT = ROOT / "docs"
SITE_URL = "https://soungwoolee.github.io"

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;600&family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&display=swap">'''


# ---------- 글 ----------

def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"==(.+?)==", r"<mark>\1</mark>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def md_to_html(md, prefix, toc=None):
    out, lst = [], None
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        first = lines[0].strip()
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", first)
        if m:
            out.append(f'<figure class="post-img"><img src="{prefix}{m.group(2)}" alt="{html.escape(m.group(1))}"></figure>')
            lines = lines[1:]
            if not lines:
                continue
            first = lines[0].strip()
        if first.startswith("## "):
            hid = f"s{len(toc) + 1}" if toc is not None else ""
            if toc is not None:
                toc.append((hid, inline(first[3:])))
            out.append(f'<h3 class="essay-h" id="{hid}">{inline(first[3:])}</h3>')
            lines = lines[1:]
            if not lines:
                continue
            first = lines[0].strip()
        if re.match(r"^(\d+\.|-) ", first):
            tag = "ol" if first[0].isdigit() else "ul"
            items = [re.sub(r"^(\d+\.|-) ", "", l.strip()) for l in lines]
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
        else:
            out.append("<p>" + "<br>".join(inline(l.strip()) for l in lines) + "</p>")
    return "\n".join(out)


def read_posts():
    posts = []
    for f in sorted((ROOT / "posts").glob("*.md"), reverse=True):
        raw = f.read_text()
        fm, body = raw.split("---", 2)[1], raw.split("---", 2)[2]
        meta = dict(re.findall(r"^(\w+):\s*(.+)$", fm, re.M))
        meta["slug"] = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
        meta["body"] = body
        posts.append(meta)
    return posts


def page(title, desc, body, prefix, lang="en", image=None, noindex=False, url=""):
    og = ""
    if image:
        og = f'<meta property="og:image" content="{SITE_URL}/{image}">'
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE_URL}/{url}">
{og}
{'<meta name="robots" content="noindex">' if noindex else ''}
{FONTS}
<link rel="stylesheet" href="{prefix}css/style.css">
</head>
<body>
{body}
<script src="{prefix}js/app.js"></script>
</body>
</html>
'''


def simple_shell(prefix, inner):
    return f'''<nav class="topbar simple" aria-label="Sections">
  <a href="{prefix}">home</a><a href="{prefix}#work">work</a><a href="{prefix}writing/">writing</a><a href="{prefix}side/">side</a><a href="{prefix}map/">map</a>
</nav>
<main class="post-main">
{inner}
<footer class="post-foot"><a href="{prefix}">← Home</a><span>Soungwoo Lee</span></footer>
</main>'''


# ---------- 홈 ----------

def build_home(posts):
    posts = [p for p in posts if p.get("listed", "yes") != "no"]
    t = (CAREER / "build" / "page_parts.html").read_text()
    t = t.split("<!--BODY-->")[1].split("<!--/BODY-->")[0]
    t = t.replace('<a href="#why">why-anthropic</a><a href="#work">work</a><a href="#side">side</a>', '<a href="#work">work</a><a href="writing/">writing</a><a href="side/">side</a><a href="map/">map</a>')
    t = t.replace('<li><a href="#side">side/</a></li>\n      <li class="sub"><a href="#s-wedding">pre-wedding</a></li>\n      <li class="sub"><a href="#s-pauze">pauze-trip</a></li>', '<!--WRITING_TOC-->\n      <li><a href="side/">side/</a></li>\n      <li><a href="map/">map</a></li>')
    t = t.replace('<li><a href="#why">why-anthropic<span class="t">.md</span></a></li>\n', '')
    t = t.replace('<!--WRITING_TOC-->', '<li><a href="writing/">writing/</a></li>' + "".join(
                      f'<li class="sub"><a href="writing/{p["slug"]}/">{html.escape(p["slug"])}</a></li>' for p in posts[:3]))
    t = t.replace('<span>Applicant · Applied AI Architect, Anthropic Seoul</span>', '<span>Seoul, Korea</span>')
    why = re.search(r"\s*<!-- WHY ANTHROPIC -->.*?</section>\n", t, re.S).group(0)
    items = "".join(
        f'<li><a href="writing/{p["slug"]}/"><span class="post-date">{p["date"]}</span><b>{html.escape(p["title"])}</b><span class="post-desc">{html.escape(p.get("description",""))}</span></a></li>'
        for p in posts[:3])
    writing = f'''
    <!-- WRITING -->
    <section class="col" id="writing">
      <span class="eyebrow">writing/</span>
      <h2>Recent writing</h2>
      <ul class="post-list">{items}</ul>
      <p class="more-link"><a href="writing/">All writing →</a></p>
    </section>
'''
    t = t.replace(why, "\n")
    side = re.search(r"\s*<section class=\"wide\" id=\"side\">.*?</section>\n", t, re.S).group(0)
    footer = re.search(r"<footer>.*?</footer>", side, re.S).group(0)
    t = t.replace(side, writing + "\n    <section class=\"col\" id=\"side-link\">\n      <span class=\"eyebrow\">side/</span>\n      <h2>Side projects</h2>\n      <p class=\"more-link\"><a href=\"side/\">A pre-wedding party service and an offline community →</a></p>\n      " + footer + "\n    </section>\n")
    (OUT / "_side_section.html").write_text(side)
    head = '''<title>Soungwoo Lee</title>
<meta name="description" content="Soungwoo Lee, data and business consultant in Seoul. Selected work, writing, and side projects.">'''
    full = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head}
<meta property="og:title" content="Soungwoo Lee">
<meta property="og:url" content="{SITE_URL}/">
{FONTS}
<link rel="stylesheet" href="css/style.css">
</head>
<body>
{t}
</body>
</html>
'''
    (OUT / "index.html").write_text(full)


# ---------- 글 목록·글 ----------

def build_writing(posts):
    listed = [p for p in posts if p.get("listed", "yes") != "no"]
    items = "".join(
        f'<li><a href="{p["slug"]}/"><span class="post-date">{p["date"]}</span><b>{html.escape(p["title"])}</b><span class="post-desc">{html.escape(p.get("description",""))}</span></a></li>'
        for p in listed)
    inner = f'<section class="col"><span class="eyebrow">writing/</span><h2>Writing</h2><ul class="post-list">{items}</ul></section>'
    (OUT / "writing").mkdir(parents=True, exist_ok=True)
    (OUT / "writing" / "index.html").write_text(page("Writing · Soungwoo Lee", "Book notes and essays by Soungwoo Lee.", simple_shell("../", inner), "../", url="writing/"))
    for p in posts:
        d = OUT / "writing" / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        toc = []
        body_html = md_to_html(p["body"], "../../", toc)
        toggle = ""
        if p.get("translation"):
            other = next(q for q in posts if q["slug"] == p["translation"])
            ko, en = (p, other) if p.get("lang") == "ko" else (other, p)
            cur = p.get("lang", "en")
            toggle = (f'<div class="lang-toggle" role="group" aria-label="Language">'
                      f'<a href="../{en["slug"]}/" class="{"on" if cur == "en" else ""}" lang="en">English</a>'
                      f'<a href="../{ko["slug"]}/" class="{"on" if cur == "ko" else ""}" lang="ko">한국어</a></div>')
        toc_html = ""
        if toc:
            toc_html = ('<aside class="post-toc" aria-label="On this page"><div class="post-toc-in"><span class="eyebrow">'
                        + ("이 글의 목차" if p.get("lang") == "ko" else "On this page") + '</span><ol>'
                        + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc) + '</ol>' + local_graph(posts, p, "../../") + '</div></aside>')
        inner = f'''<div class="post-wrap">
{toc_html}
<article class="col why post">
<span class="eyebrow">{p["date"]}</span>
<h1 class="post-title">{html.escape(p["title"])}</h1>
{toggle}
{body_html}
<div class="post-local-m">{local_graph(posts, p, "../../")}</div>
</article>
</div>
<script>
(function(){{const links=[...document.querySelectorAll('.post-toc ol a')];if(!links.length)return;
const heads=links.map(a=>document.querySelector(a.getAttribute('href')));
const on=()=>{{let k=0;heads.forEach((h,i)=>{{if(h.getBoundingClientRect().top<120)k=i}});links.forEach((a,i)=>a.classList.toggle('on',i===k))}};
addEventListener('scroll',on,{{passive:true}});on();}})();
</script>'''
        (d / "index.html").write_text(page(f'{p["title"]} · Soungwoo Lee', p.get("description", ""), simple_shell("../../", inner), "../../",
                                           lang=p.get("lang", "en"), image=p.get("image"), url=f'writing/{p["slug"]}/'))


# ---------- 지원용 Why 페이지 ----------

def build_side():
    side = (OUT / "_side_section.html").read_text()
    (OUT / "_side_section.html").unlink()
    side = side.replace('src="img/', 'src="../img/')
    side = re.sub(r"\s*<footer>.*?</footer>", "", side, flags=re.S)
    d = OUT / "side"
    d.mkdir(parents=True, exist_ok=True)
    inner = side.replace('<section class="wide" id="side">', '<section class="wide side-page" id="side">')
    (d / "index.html").write_text(page("Side projects · Soungwoo Lee", "Side projects by Soungwoo Lee: a pre-wedding party service and an offline community.",
                                      simple_shell("../", inner), "../", url="side/"))


MAP_NODES = [
    ("work", "Profit driver alerts", "#w-margin", "Profit alerts for an auto parts maker"),
    ("work", "Customer lifetime value", "#w-clv", "Moving marketing budget to the customers worth keeping"),
    ("work", "D2C lead time", "#w-d2c", "Cutting development lead time on a U.S. online store"),
    ("work", "Shared AI context", "#w-context", "One rulebook so a whole team analyzed the same way"),
    ("side", "INVITO", "side/#s-wedding", "Turning twenty pre-wedding dinners into one party"),
    ("side", "PAUZE TRIP", "side/#s-pauze", "A phone-free hiking and book club trip"),
]

# (페이지 라벨, 키워드) → 그 페이지에서 그 키워드가 어떻게 나오는지 한 줄. 본문에 있는 내용만.
MAP_HOOKS = {
    "Brain Accel notes": {
        "Digital detox": "Delete the apps outright. I still end up reinstalling them.",
        "Attention": "Endless Shorts are a self-inflicted DDoS on your own brain.",
        "Habits": "A reward you can't predict is exactly what locks a habit in.",
        "Book notes": "Zoning out is when your brain tidies up.",
    },
    "Four consulting books": {
        "Hypothesis thinking": "Without a hypothesis, data is a swamp. I've been back in it plenty of times.",
        "MECE": "\"Make it MECE\" isn't an instruction.",
        "Structuring": "Most lists don't fail on gaps. They fail on level.",
        "Storytelling with data": "Every chart needs a point, even if the title doesn't spell it out.",
        "Estimation": "No client has ever asked how many lattes a Starbucks sells. I estimate every day anyway.",
        "Working with AI": "AI now beats me at a lot of what I spent years learning.",
        "Book notes": "Four books from my first year, reread five years in.",
    },
    "\"Make it MECE\"": {
        "MECE": "No overlaps, no gaps is what a list looks like once it's done.",
        "Structuring": "Put interior design next to services and the list stops splitting cleanly.",
        "Customer segmentation": "The way to split customers came from what we wanted to do with the split.",
    },
    "Profit driver alerts": {
        "Hypothesis thinking": "Bet that a handful of accounts drove the swings. 10 of 309 explained 70.8%.",
        "Profitability": "Margin rate, not volume, drove almost every monthly profit swing.",
        "Data analysis": "60 months of P&L across 309 cost accounts.",
        "Decision support": "Alerts so management can act within the month, not after the close.",
    },
    "Customer lifetime value": {
        "Customer segmentation": "Repeat buyers spend 30% more and cost a third as much to acquire.",
        "Data modeling": "Rebuilt the client's data model without access to their database.",
        "Working with AI": "Gave AI the business context to map how the tables connect.",
        "Data analysis": "A lifetime value model on BigQuery that moved the marketing budget.",
    },
    "D2C lead time": {
        "Process design": "Merged fragmented reviews into one joint review.",
        "Data migration": "Defined target data structures and source-to-target mapping for a U.S. store.",
        "E-commerce": "Cut development lead time by 12% across 40+ subsidiaries.",
    },
    "Shared AI context": {
        "Working with AI": "Shared AI context so every analyst used the same definitions.",
        "Structuring": "Definitions, procedures and guardrails written down as one set of rules.",
    },
    "INVITO": {
        "Demand testing": "Ran one pilot party before fixing packages and prices.",
        "Working with AI": "Built the landing page and a Claude API chatbot without a developer.",
        "Community": "A team quiz got guests who had never met talking to each other.",
    },
    "PAUZE TRIP": {
        "Digital detox": "A snow-covered summit with every phone switched off.",
        "Community": "People only opened up once the form asked them to describe their work in plain words.",
        "Outdoors": "A dawn bus, a summit hike, an evening book club, a morning barre class.",
    },
}


def map_data(posts):
    nodes, links, kw = [], [], {}
    def add(kind, label, url, desc):
        i = len(nodes)
        nodes.append({"id": i, "kind": kind, "label": label, "url": url, "desc": desc})
        for t, hook in MAP_HOOKS.get(label, {}).items():
            if t not in kw:
                kw[t] = len(nodes)
                nodes.append({"id": kw[t], "kind": "tag", "label": t})
            links.append({"source": i, "target": kw[t], "hook": hook})
    for p in posts:
        if p.get("listed", "yes") != "no" and p.get("short") in MAP_HOOKS:
            add("post", p["short"], f'writing/{p["slug"]}/', p.get("description", ""))
    for kind, label, url, desc in MAP_NODES:
        add(kind, label, url, desc)
    deg = {}
    for l in links:
        deg[l["target"]] = deg.get(l["target"], 0) + 1
    for n in nodes:
        n["deg"] = deg.get(n["id"], 1) if n["kind"] == "tag" else 0
    return nodes, links


def local_graph(posts, p, prefix):
    """글 하나와 바로 연결된 키워드, 그 키워드를 공유하는 다른 페이지만 그린 작은 지도 (Quartz의 local graph)."""
    import math
    short = p.get("short") or next((q.get("short") for q in posts if q["slug"] == p.get("translation")), None)
    if not short:
        return ""
    nodes, links = map_data(posts)
    me = next((n for n in nodes if n["label"] == short and n["kind"] != "tag"), None)
    if not me:
        return ""
    tags = [nodes[l["target"]] for l in links if l["source"] == me["id"]]
    S, C = 240, 120
    col = {"post": "var(--accent)", "work": "#2f8f6a", "side": "#d9822b"}
    out, placed = [], {}
    for i, t in enumerate(tags):
        a = -math.pi / 2 + 2 * math.pi * i / len(tags)
        tx, ty = C + 54 * math.cos(a), C + 54 * math.sin(a)
        out.append(f'<line x1="{C}" y1="{C}" x2="{tx:.1f}" y2="{ty:.1f}" class="lg-l"/>')
        others = [nodes[l["source"]] for l in links if l["target"] == t["id"] and l["source"] != me["id"]]
        for j, o in enumerate(others):
            if o["id"] in placed:
                ox, oy = placed[o["id"]]
            else:
                b = a + (j - (len(others) - 1) / 2) * 0.42
                ox, oy = C + 102 * math.cos(b), C + 102 * math.sin(b)
                placed[o["id"]] = (ox, oy)
            out.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{ox:.1f}" y2="{oy:.1f}" class="lg-l"/>')
        out.append(f'<g class="lg-n lg-tag"><circle cx="{tx:.1f}" cy="{ty:.1f}" r="5"/><text x="{tx:.1f}" y="{ty - 10:.1f}">{html.escape(t["label"])}</text></g>')
    for oid, (ox, oy) in placed.items():
        o = nodes[oid]
        out.append(f'<a href="{prefix}{o["url"]}" class="lg-n"><circle cx="{ox:.1f}" cy="{oy:.1f}" r="6" fill="{col[o["kind"]]}"/><text x="{ox:.1f}" y="{oy + 18:.1f}">{html.escape(o["label"])}</text></a>')
    out.append(f'<g class="lg-n lg-me"><circle cx="{C}" cy="{C}" r="8" fill="{col[me["kind"]]}"/></g>')
    svg = f'<svg viewBox="0 0 {S} {S}" class="local-graph" role="img" aria-label="Pages connected to this one">' + "".join(out) + "</svg>"
    label = "연결된 글" if p.get("lang") == "ko" else "Connected"
    return (f'<div class="local-graph-box"><span class="eyebrow">{label}</span>{svg}'
            f'<a class="lg-more" href="{prefix}map/">{"전체 지도 보기" if p.get("lang") == "ko" else "Open the full map"} →</a></div>')


def build_map(posts):
    nodes, links = map_data(posts)
    data = json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False)
    inner = f"""<section class="col map-intro"><span class="eyebrow">map/</span><h2>How my work connects</h2>
<p>Every page on this site, linked by the ideas they share. Hover or tap a keyword to see where it shows up.</p>
<div class="map-legend"><span class="mlg k-post">Writing</span><span class="mlg k-work">Work</span><span class="mlg k-side">Side projects</span><span class="mlg k-tag">Keyword</span></div></section>
<div id="map" class="map-canvas" aria-label="Site map graph"><div id="mapTip" class="map-tip" hidden></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script>
const DATA={data};
(function(){{
const el=document.getElementById('map'),tip=document.getElementById('mapTip');
const W=1000,H=640;
const css=getComputedStyle(document.documentElement);
const col={{post:css.getPropertyValue('--accent').trim()||'#3446c4',work:'#2f8f6a',side:'#d9822b',tag:css.getPropertyValue('--ink-2').trim()||'#666'}};
const sim=d3.forceSimulation(DATA.nodes)
 .force('link',d3.forceLink(DATA.links).id(d=>d.id).distance(80).strength(0.6))
 .force('charge',d3.forceManyBody().strength(d=>d.kind==='tag'?-220:-700))
 .force('center',d3.forceCenter(W/2,H/2)).force('x',d3.forceX(W/2).strength(0.05)).force('y',d3.forceY(H/2).strength(0.08))
 .force('collide',d3.forceCollide(d=>d.kind==='tag'?22+d.deg*3:12+d.label.length*3.2)).stop();
for(let i=0;i<400;i++)sim.tick();
const xs=DATA.nodes.map(d=>d.x),ys=DATA.nodes.map(d=>d.y),pad=70;
const vb=[Math.min(...xs)-pad,Math.min(...ys)-pad,Math.max(...xs)-Math.min(...xs)+pad*2,Math.max(...ys)-Math.min(...ys)+pad*2];
const svg=d3.select(el).append('svg').attr('viewBox',vb).attr('preserveAspectRatio','xMidYMid meet');
const link=svg.append('g').selectAll('line').data(DATA.links).join('line').attr('class',d=>'m-link k-'+d.source.kind);
const node=svg.append('g').selectAll('g').data(DATA.nodes).join('g').attr('class',d=>'m-node k-'+d.kind)
 .style('cursor','pointer');
node.append('circle').attr('r',d=>d.kind==='tag'?5+d.deg*2.2:11).attr('fill',d=>d.kind==='tag'?'var(--bg)':col[d.kind]).attr('stroke',d=>d.kind==='tag'?col.tag:'var(--bg)').attr('stroke-width',d=>d.kind==='tag'?2:3);
node.append('text').text(d=>d.label).attr('x',0).attr('y',d=>d.kind==='tag'?-(10+d.deg*2.2):28).attr('text-anchor','middle');
const place=()=>{{link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);node.attr('transform',d=>`translate(${{d.x}},${{d.y}})`)}};
place();
const esc=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
let pinned=null;
function focus(d){{
  const touch=new Set([d]);DATA.links.forEach(l=>{{if(l.source===d)touch.add(l.target);if(l.target===d)touch.add(l.source)}});
  node.classed('dim',n=>!touch.has(n));link.classed('hot',l=>l.source===d||l.target===d).classed('dim',l=>!(l.source===d||l.target===d));
  let html='';
  if(d.kind==='tag'){{html=`<b class="t-key">${{esc(d.label)}}</b><ul>`+DATA.links.filter(l=>l.target===d).map(l=>`<li><a href="../${{l.source.url}}"><span class="t-${{l.source.kind}}">${{esc(l.source.label)}}</span>${{esc(l.hook)}}</a></li>`).join('')+'</ul>';}}
  else{{html=`<a class="t-head t-${{d.kind}}" href="../${{d.url}}">${{esc(d.label)}} →</a><p>${{esc(d.desc)}}</p>`;}}
  tip.innerHTML=html;tip.hidden=false;
  const r=el.getBoundingClientRect(),pt=svg.node().createSVGPoint();pt.x=d.x;pt.y=d.y;const s=pt.matrixTransform(svg.node().getScreenCTM());
  const nx=s.x-r.left,ny=s.y-r.top,tw=tip.offsetWidth,th=tip.offsetHeight,gap=22;
  let side=(ny-th-gap>8)?'top':'bottom';let y=side==='top'?ny-th-gap:ny+gap;
  let x=Math.max(8,Math.min(r.width-tw-8,nx-tw/2));
  tip.dataset.side=side;tip.style.setProperty('--ax',(nx-x)+'px');tip.style.left=x+'px';tip.style.top=y+'px';
  tip.classList.remove('pop');void tip.offsetWidth;tip.classList.add('pop');
}}
let ht=null;function clear(){{if(pinned)return;node.classed('dim',false);link.classed('hot',false).classed('dim',false);tip.hidden=true}}
const later=()=>{{clearTimeout(ht);ht=setTimeout(clear,280)}};
node.on('mouseenter',(e,d)=>{{clearTimeout(ht);if(!pinned)focus(d)}}).on('mouseleave',later)
 .on('click',(e,d)=>{{e.stopPropagation();if(d.kind!=='tag'&&pinned===null&&matchMedia('(hover:hover)').matches){{location.href='../'+d.url;return}}pinned=(pinned===d)?null:d;if(pinned)focus(d);else{{pinned=null;clear()}}}});
tip.addEventListener('mouseenter',()=>clearTimeout(ht));tip.addEventListener('mouseleave',later);
el.addEventListener('click',e=>{{if(e.target.closest('.map-tip'))return;pinned=null;clear()}});
node.call(d3.drag().on('drag',(e,d)=>{{d.x=e.x;d.y=e.y;place()}}));
}})();
</script>"""
    d = OUT / "map"
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(page("Map · Soungwoo Lee", "A keyword map of Soungwoo Lee's work, writing and side projects.", simple_shell("../", inner), "../", url="map/"))


def build_why():
    for name, src in [("anthropic", CAREER / "site" / "index.html"), ("palantir", CAREER / "site_palantir" / "index.html")]:
        t = src.read_text()
        t = t.replace('href="css/', 'href="../../css/').replace('src="js/', 'src="../../js/').replace('src="img/', 'src="../../img/')
        t = t.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
        d = OUT / "why" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(t)


POST_CSS = """
/* map */
.post-main:has(.map-canvas){max-width:1180px}
.map-intro p{color:var(--ink-2);max-width:62ch}
.map-legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;font-family:var(--mono);font-size:12px;color:var(--ink-2)}
.map-legend .mlg::before{content:"";display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
.mlg.k-post::before{background:var(--accent)}.mlg.k-work::before{background:#2f8f6a}.mlg.k-side::before{background:#d9822b}.mlg.k-tag::before{border:2px solid var(--ink-2);width:7px;height:7px}
.map-canvas{position:relative;margin-top:20px;border:1px solid var(--rule);border-radius:14px;overflow:hidden;height:min(68vh,620px);min-height:420px}
.map-canvas svg{width:100%;height:100%;display:block}
.m-link{stroke-width:1.8;opacity:.55}
.m-link.k-post{stroke:var(--accent)}.m-link.k-work{stroke:#2f8f6a}.m-link.k-side{stroke:#d9822b}
.m-link.hot{opacity:1;stroke-width:3;stroke-dasharray:6 6;animation:flow 1s linear infinite}
@keyframes flow{to{stroke-dashoffset:-12}}
.map-canvas .dim{opacity:.12;transition:opacity .15s}
.m-node{transition:opacity .15s}
.map-canvas text{font-size:14px;fill:var(--ink);paint-order:stroke;stroke:var(--bg);stroke-width:5px;stroke-linejoin:round;pointer-events:none;font-weight:600}
.m-node.k-tag text{font-family:var(--mono);font-size:12.5px;fill:var(--ink-2);font-weight:500}
.m-node:hover circle{filter:drop-shadow(0 0 6px rgba(0,0,0,.25))}
.map-tip{position:absolute;z-index:3;width:300px;max-width:calc(100% - 16px);background:var(--bg);border:1.5px solid var(--ink);border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.14);padding:12px 16px;font-size:13.5px;line-height:1.45}
.map-tip::after{content:"";position:absolute;left:calc(var(--ax,50%) - 9px);width:16px;height:16px;background:var(--bg);border:1.5px solid var(--ink);transform:rotate(45deg)}
.map-tip[data-side="top"]::after{bottom:-9.5px;border-top:0;border-left:0}
.map-tip[data-side="bottom"]::after{top:-9.5px;border-bottom:0;border-right:0}
.map-tip.pop{animation:pop .18s cubic-bezier(.3,1.6,.6,1)}
@keyframes pop{from{transform:scale(.85);opacity:0}to{transform:scale(1);opacity:1}}
.map-tip ul{list-style:none;margin:8px 0 0;padding:0;display:flex;flex-direction:column;gap:8px}
.map-tip a{color:var(--ink);text-decoration:none;display:block}
.map-tip a:hover{color:var(--accent)}
.map-tip li span{display:block;font-family:var(--mono);font-size:11.5px;margin-bottom:2px}
.t-key{font-family:var(--mono);font-size:12.5px}
.t-post{color:var(--accent)}.t-work{color:#2f8f6a}.t-side{color:#d9822b}
.t-head{font-weight:600}.map-tip p{margin:6px 0 0;color:var(--ink-2)}
/* local graph */
.local-graph-box{margin-top:28px}
.local-graph{width:100%;max-width:240px;height:auto;display:block;margin-top:6px;overflow:visible}
.lg-l{stroke:var(--rule);stroke-width:1.4}
.lg-n circle{transition:r .15s}
.lg-tag circle{fill:var(--bg);stroke:var(--ink-2);stroke-width:1.6}
.lg-me circle{stroke:var(--bg);stroke-width:3}
.lg-n text{font-size:11px;fill:var(--ink);text-anchor:middle;opacity:0;transition:opacity .15s;paint-order:stroke;stroke:var(--bg);stroke-width:4px;pointer-events:none}
.lg-tag text{font-family:var(--mono);fill:var(--ink-2)}
.lg-n:hover text{opacity:1!important}
.lg-more{display:inline-block;margin-top:6px;font-size:12px;font-family:var(--mono);color:var(--accent);text-decoration:none}
.post-local-m{display:block;margin-top:40px}
@media (min-width:1080px){.post-local-m{display:none}}
/* writing */
.post-main:has(.post-toc){max-width:1120px}
.post-wrap{display:block}
.post-toc{display:none}
@media (min-width:1080px){
  .post-wrap:has(.post-toc){display:grid;grid-template-columns:220px minmax(0,760px);gap:56px;justify-content:center}
  .post-toc{display:block}
  .post-toc-in{position:sticky;top:72px;font-size:13px;line-height:1.45}
  .post-toc ol{list-style:none;margin:10px 0 0;padding:0;display:flex;flex-direction:column;gap:2px;border-left:2px solid var(--rule)}
  .post-toc a{display:block;padding:6px 0 6px 12px;margin-left:-2px;border-left:2px solid transparent;color:var(--ink-2);text-decoration:none}
  .post-toc a:hover{color:var(--ink)}
  .post-toc a.on{color:var(--accent);border-left-color:var(--accent);font-weight:600}
}
.essay-h{scroll-margin-top:72px}
.lang-toggle{display:inline-flex;border:1px solid var(--rule);border-radius:999px;padding:3px;margin:0 0 20px;font-family:var(--mono);font-size:13px}
.lang-toggle a{padding:4px 12px;border-radius:999px;color:var(--ink-2);text-decoration:none}
.lang-toggle a.on{background:var(--ink);color:var(--bg)}
.post mark{background:linear-gradient(transparent 55%,#ffe58a 55%);color:inherit;padding:0 2px}
:root[data-theme="dark"] .post mark{background:linear-gradient(transparent 55%,#6b5a1e 55%)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .post mark{background:linear-gradient(transparent 55%,#6b5a1e 55%)}}
.topbar.simple{display:flex;gap:20px;padding:14px max(16px,calc((100% - 1120px)/2));border-bottom:1px solid var(--rule);background:var(--bg);font-family:var(--mono);font-size:13px;position:sticky;top:0;z-index:5}
.topbar.simple a{color:var(--ink-2);text-decoration:none}.topbar.simple a:hover{color:var(--accent)}
.post-list{list-style:none;padding:0;margin:16px 0 0;display:flex;flex-direction:column;gap:4px}
.post-list a{display:grid;grid-template-columns:96px 1fr;column-gap:16px;padding:14px 0;border-top:1px solid var(--rule);color:var(--ink);text-decoration:none}
.post-list a:hover b{color:var(--accent)}
.post-date{font-family:var(--mono);font-size:13px;color:var(--ink-2);grid-row:span 2}
.post-desc{grid-column:2;color:var(--ink-2);font-size:15px;margin-top:4px}
.more-link a{color:var(--accent)}
.post-main:has(.side-page){max-width:1120px}
.post-main{max-width:760px;margin:0 auto;padding:48px 16px 64px}
.post-title{font-size:30px;line-height:1.3;margin:8px 0 20px;text-wrap:balance}
.post p,.post li{font-family:"IBM Plex Sans KR",var(--sans,system-ui),sans-serif;line-height:1.85}
.post ol{margin:12px 0 0;padding-left:22px;display:flex;flex-direction:column;gap:6px;max-width:68ch}
.post-img{margin:8px 0 24px}.post-img img{width:100%;height:auto;border-radius:10px;display:block}
.post-foot{display:flex;justify-content:space-between;margin-top:48px;padding-top:16px;border-top:1px solid var(--rule);font-family:var(--mono);font-size:13px}
.post-foot a{color:var(--accent);text-decoration:none}
@media (max-width:600px){.post-list a{grid-template-columns:1fr}.post-date{grid-row:auto}.post-desc{grid-column:1}.post-title{font-size:24px}}
"""


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(ROOT / "src", OUT)
    css = OUT / "css" / "style.css"
    css.write_text(css.read_text() + POST_CSS)
    (OUT / ".nojekyll").write_text("")
    posts = read_posts()
    build_home(posts)
    build_writing(posts)
    build_side()
    build_map(posts)
    build_why()
    print(f"built: {len(posts)} posts")


if __name__ == "__main__":
    main()
