"""개인 홈페이지 빌드. src/ 자산 + career_site 템플릿 + posts/*.md → docs/ (GitHub Pages가 docs 폴더를 서빙)

실행: python3 build.py
- docs/index.html            홈 (소개, 최근 글, Work, Side)
- docs/writing/index.html    글 목록
- docs/writing/<slug>/       글 하나
- docs/why/anthropic/, docs/why/palantir/   지원용 페이지 (메뉴에 없음, 검색 제외)
"""
import html, re, shutil
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


def md_to_html(md, prefix):
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
            out.append(f'<h3 class="essay-h">{inline(first[3:])}</h3>')
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
  <a href="{prefix}">home</a><a href="{prefix}#work">work</a><a href="{prefix}writing/">writing</a><a href="{prefix}side/">side</a>
</nav>
<main class="post-main">
{inner}
<footer class="post-foot"><a href="{prefix}">← Home</a><span>Soungwoo Lee</span></footer>
</main>'''


# ---------- 홈 ----------

def build_home(posts):
    t = (CAREER / "build" / "page_parts.html").read_text()
    t = t.split("<!--BODY-->")[1].split("<!--/BODY-->")[0]
    t = t.replace('<a href="#why">why-anthropic</a><a href="#work">work</a><a href="#side">side</a>', '<a href="#work">work</a><a href="writing/">writing</a><a href="side/">side</a>')
    t = t.replace('<li><a href="#side">side/</a></li>\n      <li class="sub"><a href="#s-wedding">pre-wedding</a></li>\n      <li class="sub"><a href="#s-pauze">pauze-trip</a></li>', '<!--WRITING_TOC-->\n      <li><a href="side/">side/</a></li>')
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
    items = "".join(
        f'<li><a href="{p["slug"]}/"><span class="post-date">{p["date"]}</span><b>{html.escape(p["title"])}</b><span class="post-desc">{html.escape(p.get("description",""))}</span></a></li>'
        for p in posts)
    inner = f'<section class="col"><span class="eyebrow">writing/</span><h2>Writing</h2><ul class="post-list">{items}</ul></section>'
    (OUT / "writing").mkdir(parents=True, exist_ok=True)
    (OUT / "writing" / "index.html").write_text(page("Writing · Soungwoo Lee", "Book notes and essays by Soungwoo Lee.", simple_shell("../", inner), "../", url="writing/"))
    for p in posts:
        d = OUT / "writing" / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        inner = f'''<article class="col why post">
<span class="eyebrow">{p["date"]}</span>
<h1 class="post-title">{html.escape(p["title"])}</h1>
{md_to_html(p["body"], "../../")}
</article>'''
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


def build_why():
    for name, src in [("anthropic", CAREER / "site" / "index.html"), ("palantir", CAREER / "site_palantir" / "index.html")]:
        t = src.read_text()
        t = t.replace('href="css/', 'href="../../css/').replace('src="js/', 'src="../../js/').replace('src="img/', 'src="../../img/')
        t = t.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
        d = OUT / "why" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(t)


POST_CSS = """
/* writing */
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
    build_why()
    print(f"built: {len(posts)} posts")


if __name__ == "__main__":
    main()
