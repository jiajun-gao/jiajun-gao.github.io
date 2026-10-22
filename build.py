"""Assemble the multi-page site from shared partials.

Usage: python3 build.py _source . [ARTIFACT_HOME]

Writes every page as a full HTML document into the site folder. With ARTIFACT_HOME, also
writes the home page as a bare fragment there for a Claude artifact preview (its viewer
adds the document skeleton).
"""
import hashlib
import sys
from html import escape
from pathlib import Path
from urllib.parse import quote

src, site = Path(sys.argv[1]), Path(sys.argv[2])
artifact_home = Path(sys.argv[3]) if len(sys.argv) > 3 else None

# (file name, nav label, <title>, meta description), in reading order
PAGES = [
    ("index", "Home", "Jiajun Gao",
     "Jiajun Gao (高嘉骏) is a computer engineer and M.S. ECE student at the University of Illinois "
     "Urbana-Champaign working on robotics, embodied AI, AI agents, and LLMs."),
    ("projects", "Projects", "Projects · Jiajun Gao",
     "Projects by Jiajun Gao: the Jarvis companion robot (ECE 445 Hall of Fame), retrieval-augmented "
     "QA under knowledge edits, a self-driving GEM vehicle, and loan approval prediction."),
    ("experience", "Experience", "Experience · Jiajun Gao",
     "Jiajun Gao's experience: ECE 385 teaching assistant at the University of Illinois, algorithm "
     "intern at Shanghai AI Laboratory, and FPGA systems at the UIUC Digital Systems Design Lab."),
    ("research", "Research", "Research · Jiajun Gao",
     "Jiajun Gao's research comparing WGAN-GP and WGAN-CP for image generation."),
    ("education", "Education", "Education · Jiajun Gao",
     "Jiajun Gao's education: M.S. ECE and B.S. Computer Engineering (High Honors) at the "
     "University of Illinois Urbana-Champaign."),
    ("skills", "Skills", "Skills · Jiajun Gao",
     "Jiajun Gao's skills in LLMs and AI agents, machine learning, robotics, data, and hardware."),
]
SUBPAGES = PAGES[1:]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900'
    '&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">\n'
    # only the three characters of the Chinese name, so the CJK font stays a few KB
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@500'
    f'&text={quote("高嘉骏")}&display=swap">'
)
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='8' fill='%2308100D'/%3E"
    "%3Crect x='8' y='9' width='6' height='14' rx='2' fill='%2393F2CF'/%3E"
    "%3Crect x='18' y='9' width='6' height='14' rx='2' fill='%2393F2CF'/%3E%3C/svg%3E"
)


def document_head(title, desc):
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{escape(desc)}">
<meta name="author" content="Jiajun Gao">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta name="theme-color" content="#F2F4F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0D1311" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{FAVICON}">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}</style>
"""


def asset_url(name):
    # content fingerprint, so browsers holding a cached copy fetch the new file after a change
    digest = hashlib.sha256((src / "assets" / name).read_bytes()).hexdigest()[:8]
    return f"assets/{name}?v={digest}"


def pager(slug):
    names = [p[0] for p in SUBPAGES]
    i = names.index(slug)
    prev = SUBPAGES[i - 1] if i > 0 else PAGES[0]
    nxt = SUBPAGES[i + 1] if i + 1 < len(SUBPAGES) else PAGES[0]
    return f"""<nav class="pager wrap" aria-label="More pages">
  <div class="inner">
    <a class="prev" href="{prev[0]}.html"><span class="dir">← Previous</span><span class="to">{prev[1]}</span></a>
    <a class="next" href="{nxt[0]}.html"><span class="dir">Next →</span><span class="to">{nxt[1]}</span></a>
  </div>
</nav>
"""


nav = (src / "nav.html").read_text()
footer = (src / "footer.html").read_text()

for slug, _, title, desc in PAGES:
    body = (src / "pages" / f"{slug}.html").read_text()
    page_nav = nav.replace(f'<a href="{slug}.html">', f'<a href="{slug}.html" aria-current="page">')
    core = (
        f"<title>{escape(title)}</title>\n"
        '<meta name="claude:viewport-fit-sides" content="cover">\n'
        f"{FONTS}\n"
        f'<link rel="stylesheet" href="{asset_url("site.css")}">\n\n'
        f"{page_nav}\n{body}\n"
        f"{'' if slug == 'index' else pager(slug)}"
        f"{footer}\n"
        f'<script src="{asset_url("site.js")}"></script>\n'
    )
    (site / f"{slug}.html").write_text(document_head(title, desc) + core + "</html>\n")
    if slug == "index" and artifact_home:
        artifact_home.write_text(core)

(site / "assets").mkdir(exist_ok=True)
for asset in (src / "assets").iterdir():
    (site / "assets" / asset.name).write_bytes(asset.read_bytes())

print("built:", ", ".join(f"{p[0]}.html" for p in PAGES))
