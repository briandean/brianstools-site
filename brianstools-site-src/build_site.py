"""Builds the static brianstools.net site.   python3 build_site.py

Inputs (next to this script): README.md, help.md and version.py copied from the app repo,
plus site.css / site.js. Edit CONFIG, run, then commit the contents of ./site to the
brianstools-site repo (GitHub Pages, branch main, folder / root)."""
import os, re, shutil, html, datetime, importlib.util
from markdown_it import MarkdownIt
import cairosvg
from fontTools import subset

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ CONFIG
SITE_URL   = "https://brianstools.net"
GITHUB     = "https://github.com/briandean/brianstools"        # app source repo
# Compiled apps: (download URL, short description). Hosted as GitHub release assets.
REL_BASE = "https://github.com/briandean/brianstools/releases/download/pre-release"
RELEASE_PAGE = "https://github.com/briandean/brianstools/releases/tag/pre-release"
DL = {
    "windows": (f"{REL_BASE}/BriansTools_Win.zip",   "Standalone .exe, zipped \u2014 no install"),
    "macos":   (f"{REL_BASE}/BriansTools_Mac.zip",   "Standalone .app, zipped"),
    "linux":   (f"{REL_BASE}/BriansTools_Linux.zip", "Standalone binary, zipped"),
}
EMAIL      = "brian@briandean.net"
KIT        = next(p for p in (os.path.join(HERE, "..", "brians-tools-brand"), "/mnt/user-data/outputs/brians-tools-brand") if os.path.isdir(p))  # the brand kit folder
OUT        = os.path.join(HERE, "..", "brianstools-site") if not os.environ.get("BT_OUT") else os.environ["BT_OUT"]
# --------------------------------------------------------------------------

OUT = os.path.abspath(OUT)
spec = importlib.util.spec_from_file_location("appversion", os.path.join(HERE, "version.py"))
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
REL = datetime.date.fromisoformat(V.RELEASE_DATE)
REL_PRETTY = f"{REL:%B} {REL.day}, {REL.year}"
VERSION_LINE = f"Version {V.VERSION} · released {REL_PRETTY}"

dl_url = lambda k: DL[k][0]
# keep real screenshots and download files across rebuilds; everything else is regenerated
KEEP = {}
for keep in ("assets/img/screenshots",):
    d = os.path.join(OUT, keep)
    if os.path.isdir(d):
        KEEP[keep] = {f: open(os.path.join(d, f), "rb").read() for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))}
shutil.rmtree(OUT, ignore_errors=True)
for d in ("assets/css", "assets/js", "assets/img/screenshots", "assets/fonts", "assets/brand", "help"):
    os.makedirs(f"{OUT}/{d}", exist_ok=True)

# ---------- brand assets from the kit ----------
cp = lambda src, dst: shutil.copy(f"{KIT}/{src}", f"{OUT}/{dst}")
for f in ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "android-chrome-192x192.png",
          "android-chrome-512x512.png", "maskable-icon-512x512.png", "site.webmanifest"):
    cp(f"icon/web/{f}", f)
cp("logo/horizontal/brians-tools-horizontal-notag-reversed.svg", "assets/brand/logo-reversed.svg")
cp("logo/horizontal/brians-tools-horizontal-notag-full-color.svg", "assets/brand/logo.svg")
cp("logo/mark/bt-mark-reversed.svg", "assets/brand/mark-reversed.svg")
cp("logo/mark/bt-mark-full-color.svg", "assets/brand/mark.svg")
cp("icon/app/bt-icon.svg", "assets/brand/app-icon.svg")
cp("social/open-graph-dark-1200x630.png", "assets/brand/og-image.png")

# ---------- self-hosted Inter (Latin subset, woff2) ----------
EXTRA = [0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x2190, 0x2192, 0x2212, 0x00D7, 0x2605, 0x2606,
         0x25B6, 0x25B8, 0x2630, 0x21C4, 0x25B2, 0x25BC, 0x2039, 0x203A, 0x2318, 0x21E7, 0x25A6, 0x2715, 0x26A0, 0x2264, 0x2265]
for w in ("Regular", "Medium", "SemiBold", "Bold", "ExtraBold"):
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga", "tnum", "calt"]
    font = subset.load_font(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", opts)
    s = subset.Subsetter(opts); s.populate(unicodes=list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) + EXTRA)
    s.subset(font); subset.save_font(font, f"{OUT}/assets/fonts/Inter-{w}.woff2", opts)

# ---------- screenshot placeholders (overwrite these PNGs with real screenshots) ----------
SHOTS = {
    "main":           "Main window — Home tab",
    "route-table":    "Route Table — show ip route summary",
    "irr-rpki":       "IRR / RPKI — prefix filter builder",
    "ping":           "Ping — multi-target monitor",
    "dns-digr":       "DNS Digr — trace from root",
    "bandwidth-cost": "Bandwidth Cost — quote comparison",
}
for keep, files in KEEP.items():
    os.makedirs(os.path.join(OUT, keep), exist_ok=True)
    for f, data in files.items():
        open(os.path.join(OUT, keep, f), "wb").write(data)
for key, label in SHOTS.items():
    if os.path.exists(f"{OUT}/assets/img/screenshots/{key}.png"):
        continue                      # keep your real screenshot (or the existing placeholder)
    w, h = 1600, 1000
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect width="{w}" height="{h}" fill="#1e293b"/>
<rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" fill="none" stroke="#475569" stroke-width="4" stroke-dasharray="22 16"/>
<image href="file://{KIT}/logo/mark/bt-mark-reversed.svg" x="{w/2-150}" y="300" width="300" height="200"/>
<text x="{w/2}" y="590" text-anchor="middle" font-family="Inter" font-weight="700" font-size="56" fill="#ffffff">Screenshot placeholder</text>
<text x="{w/2}" y="660" text-anchor="middle" font-family="Inter" font-weight="500" font-size="38" fill="#22c3ee">{html.escape(label)}</text>
<text x="{w/2}" y="730" text-anchor="middle" font-family="Inter" font-weight="500" font-size="30" fill="#94a3b8">Replace assets/img/screenshots/{key}.png  ·  1600 × 1000</text>
</svg>'''
    cairosvg.svg2png(bytestring=svg.encode(), write_to=f"{OUT}/assets/img/screenshots/{key}.png", unsafe=True)

# ---------- page template ----------
NAV = [("/", "Home"), ("/help/", "Help"), ("/details.html", "Details"), ("/#download", "Download"), ("/contact.html", "Contact")]
GH_SVG = ('<svg viewBox="0 0 16 16" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 '
          '3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52'
          '-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36'
          '-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 '
          '2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')

def page(path, title, desc, body, active):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if lbl == active else ""}>{lbl}</a>' for h, lbl in NAV)
    canon = SITE_URL + path
    year = datetime.date.today().year
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0f172a">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Brian’s Tools">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE_URL}/assets/brand/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/Inter-ExtraBold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="/" aria-label="Brian’s Tools home"><img src="/assets/brand/logo-reversed.svg" alt="Brian’s Tools" width="190" height="42"></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav id="nav" class="nav">{links}<a class="gh" href="{GITHUB}" rel="noopener">{GH_SVG}<span>GitHub</span></a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap foot">
    <div class="foot-brand"><img src="/assets/brand/mark-reversed.svg" alt="" width="54" height="36"><div><strong>Brian’s Tools</strong><span>Network Toolbox · {V.VERSION}</span></div></div>
    <nav class="foot-nav"><a href="/">Home</a><a href="/help/">Help</a><a href="/details.html">Details</a><a href="/#download">Download</a><a href="/contact.html">Contact</a><a href="{GITHUB}" rel="noopener">GitHub</a></nav>
    <p class="fine">© {year} Brian Dean · brianstools.net</p>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>'''

def shot(key, cls=""):
    return (f'<figure class="shot {cls}"><div class="chrome"><span></span><span></span><span></span><em>Brian’s Tools</em></div>'
            f'<img src="/assets/img/screenshots/{key}.png" alt="{html.escape(SHOTS[key])}" width="1600" height="1000" loading="lazy">'
            + (f'<figcaption>{html.escape(SHOTS[key])}</figcaption>' if cls != "shot-hero" else "") + '</figure>')

# ---------- markdown helpers ----------
MD = MarkdownIt("commonmark", {"html": False}).enable("table")
def strip_tags(t): return html.unescape(re.sub(r"<[^>]+>", "", t))
def slug(t): return re.sub(r"[^a-z0-9]+", "-", strip_tags(t).lower()).strip("-")
def post(body):
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener"', body)

# ---------- tool catalogue (groups and order as in the app's Tools menu / help) ----------
TOOLS = [
    ("IP", [("IP Calc", "IPv4/IPv6 subnet math, splits, multicast details and copy-ready subnet summaries for tickets."),
            ("IP Summarize", "Collapse prefixes, ip/mask pairs or ranges into the minimal aggregate and covering supernet."),
            ("Bits & Bytes", "Exact unit conversion across bits, bytes and kilo through peta, in binary or SI."),
            ("Bandwidth Cost", "What a circuit really costs per Mbps, per Gbps and per user, with a saved quote comparison.")]),
    ("Time", [("Time Zones", "Convert one time into every zone on your list, with DST gaps and overlaps flagged."),
              ("Time Calc", "Add or subtract calendar time, count business days, repeat intervals, get epochs.")]),
    ("MAC", [("MAC Format", "Pull MACs out of any pasted text and rewrite them dotted, dashed or colon-separated."),
             ("MAC Lookup", "Vendor lookup from the IEEE list (downloaded for you), plus HSRP, VRRP, GLBP and multicast MACs.")]),
    ("Text & logs", [("Compare", "Side-by-side and unified diffs of configs, with noise filters and unique-line views."),
                     ("Log Times", "Find every timestamp in a log and rewrite it into another time zone in place.")]),
    ("Network", [("DNS Digr", "Built-in dig-style DNS client: full trace from the root, DNSSEC, TCP, every common record type."),
                 ("Ping", "Ping up to 256 hosts at once with live loss, RTT, jitter, outages, notes and full history."),
                 ("Ping Sweep", "Sweep subnets, ranges or pasted ARP output and see what’s alive in seconds."),
                 ("Traceroute", "Live hop table from the system traceroute, with address types, loss and MPLS labels."),
                 ("Whois", "ARIN IP/ASN lookups, AS-path owners, other RIRs via RDAP, and domain whois."),
                 ("Route Table", "Paste show ip route / show route from IOS, XR, NX-OS, Junos or EOS and get the summary."),
                 ("IRR / RPKI", "bgpq4-style prefix filters from the IRR with RPKI validation, for XR, XE, Junos, EOS and Nokia.")]),
]
N_TOOLS = sum(len(g[1]) for g in TOOLS)

# ================================================================== help/index.html  (from help.md)
help_src = open(os.path.join(HERE, "help.md"), encoding="utf-8").read()
help_src = help_src.replace("{{version_line}}", f"{VERSION_LINE} · [brianstools.net]({SITE_URL})").replace("{{version}}", V.VERSION)
help_src = re.sub(r"^# .*\n", "", help_src, count=1)
hbody = MD.render(help_src)
htoc, used = [], set()
def hid(m):
    lvl, t = m.group(1), m.group(2); s = slug(t)
    while s in used: s += "-2"
    used.add(s)
    if lvl == "2": htoc.append([s, strip_tags(t), []])
    elif htoc: htoc[-1][2].append((s, strip_tags(t)))
    return f'<h{lvl} id="{s}">{t}</h{lvl}>'
hbody = post(re.sub(r"<h([23])>(.*?)</h\1>", hid, hbody))
help_intro = re.search(r"<p>.*?</p>", hbody, re.S).group(0); hbody = hbody.replace(help_intro, "", 1)
HELP_IDS = {sub[0] for sec in htoc for sub in sec[2]}
toc = '<ul class="toc">' + "".join(
    f'<li><a href="#{s}">{t}</a>' + ("<ul>" + "".join(f'<li><a href="#{a}">{n}</a></li>' for a, n in subs) + "</ul>" if subs else "") + "</li>"
    for s, t, subs in htoc) + "</ul>"
help_page = f'''
<section class="page-head"><div class="wrap">
  <p class="eyebrow">Help</p>
  <h1>Brian’s Tools Help</h1>
  <div class="lede">{help_intro}</div>
  <p class="ver-chip">{VERSION_LINE}</p>
  <p class="cta"><a class="btn btn-primary" href="/#download">Download</a> <a class="btn btn-ghost" href="/details.html">Technical details</a></p>
</div></section>
<div class="wrap doc-layout">
  <aside class="doc-toc" aria-label="On this page"><p class="toc-title">On this page</p>{toc}</aside>
  <article class="doc help">{hbody}<p class="print-note">In the app: <strong>☰ Tools → Brian’s Tools Help</strong> or <strong>F1</strong> opens this guide offline.</p></article>
</div>
'''
open(f"{OUT}/help/index.html", "w").write(page("/help/", "Help — Brian’s Tools",
     "The Brian’s Tools user guide: every tool, shortcut, setting, and what the app connects to.", help_page, "Help"))

def tool_link(name):
    s = slug(name)
    return f"/help/#{s}" if s in HELP_IDS else "/help/"

# ================================================================== index.html
tools_html = "".join(
    f'<section class="tool-group"><h3>{g}</h3><ul>' +
    "".join(f'<li><a href="{tool_link(n)}"><strong>{html.escape(n)}</strong><span>{d}</span></a></li>' for n, d in items) +
    "</ul></section>" for g, items in TOOLS)
OS_ICON = {
 "windows": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 5.5 10.5 4.4v7.1H3zm8.5-1.2L21 3v8.5h-9.5zM3 12.5h7.5v7.1L3 18.5zm8.5 0H21V21l-9.5-1.3z"/></svg>',
 "macos":   '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.4 12.6c0-2.4 2-3.6 2.1-3.7-1.2-1.7-3-1.9-3.6-2-1.5-.2-3 .9-3.8.9-.8 0-2-.9-3.3-.9-1.7 0-3.3 1-4.2 2.5-1.8 3.1-.5 7.7 1.3 10.2.9 1.2 1.9 2.6 3.2 2.6 1.3-.1 1.8-.8 3.3-.8 1.5 0 2 .8 3.3.8 1.4 0 2.3-1.3 3.1-2.5 1-1.4 1.4-2.8 1.4-2.9 0 0-2.8-1.1-2.8-4.2zM13.9 5.2c.7-.9 1.2-2 1-3.2-1 0-2.3.7-3 1.6-.7.8-1.2 2-1.1 3.1 1.2.1 2.3-.6 3.1-1.5z"/></svg>',
 "linux":   '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2c-2.2 0-3.5 1.8-3.5 4.3 0 1.4.3 2.3-.6 3.6-1.2 1.6-2.8 3.6-2.8 6.1 0 .8.2 1.4.5 2-.9.4-1.8 1-1.6 1.9.3 1.2 2.4 1 3.7 1.6 1.2.5 2.1.6 2.8-.2.6.2 1.4.3 2.2.3s1.6-.1 2.2-.3c.7.8 1.6.7 2.8.2 1.3-.6 3.4-.4 3.7-1.6.2-.9-.7-1.5-1.6-1.9.3-.6.5-1.2.5-2 0-2.5-1.6-4.5-2.8-6.1-.9-1.3-.6-2.2-.6-3.6C15.5 3.8 14.2 2 12 2zm-1.5 4a.9 1.1 0 1 1 0 2.2.9 1.1 0 0 1 0-2.2zm3 0a.9 1.1 0 1 1 0 2.2.9 1.1 0 0 1 0-2.2zM12 8.6c.8 0 1.9.5 1.9.9s-1.1 1.1-1.9 1.1-1.9-.7-1.9-1.1.9-.9 1.9-.9z"/></svg>',
}
OS_NAME = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}
dl_cards = "".join(
    f'''<article class="dl-card" data-os="{k}">
      <div class="dl-ico">{OS_ICON[k]}</div>
      <h3>{OS_NAME[k]}</h3>
      <p class="req">{DL[k][1]}</p>
      <a class="btn btn-primary" href="{dl_url(k)}">Download for {OS_NAME[k]}</a>
      <code class="file">{DL[k][0].rsplit("/", 1)[1]}</code>
    </article>''' for k in ("windows", "macos", "linux"))

HIGHLIGHTS = [
    ("Route Table", "route-table", "Paste <code>show ip route</code> or <code>show route</code> from IOS, IOS-XE, IOS-XR, NX-OS, Junos or EOS. Get routes by protocol, interface and next hop, ECMP, recent changes and suspicious metrics."),
    ("IRR / RPKI", "irr-rpki", "Expand AS-SETs from the IRR like bgpq4, validate every route object against RPKI, and output prefix filters for IOS-XR, IOS-XE / NX-OS, Junos, EOS and Nokia SR OS / SR Linux."),
    ("Bandwidth Cost", "bandwidth-cost", "Cost per Mbps, per Gbps, per user and per GB moved, with install costs spread or up front, and a saved table for comparing quotes."),
    ("Send to", "right-click-menu-and-send-to", "Right-click any IP, MAC, host name or table cell and send it to another tool, which runs it straight away."),
]
hl_html = "".join(f'<article><h3><a href="/help/#{a}">{n}</a></h3><p>{d}</p></article>' for n, a, d in HIGHLIGHTS)

index = f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Network Toolbox</p>
      <h1>Brian’s <span>Tools</span></h1>
      <p class="lede">A local, lightweight network toolkit for Windows, macOS and Linux. Subnet math, DNS, ping, traceroute, whois, route tables, IRR and RPKI prefix filters, MAC lookups, time zones and log timestamps — {N_TOOLS} everyday tools for network engineers, in one small desktop app that runs on your own machine.</p>
      <div class="cta">
        <a class="btn btn-primary" id="primary-dl" href="#download">Download</a>
        <a class="btn btn-ghost" href="/help/">Read the help</a>
      </div>
      <p class="hero-meta">{VERSION_LINE} · No account, no telemetry, no ads</p>
    </div>
    <img class="hero-icon" src="/assets/brand/app-icon.svg" alt="" width="220" height="220">
  </div>
  <div class="wrap">{shot("main", "shot-hero")}</div>
</section>

<section class="pillars wrap">
  <article><h3>Local</h3><p>Runs on your computer with no account, telemetry or ads. Calculators, Compare, Log Times, Route Table and Bandwidth Cost work fully offline; the rest only contact the servers you point them at. <a href="/help/#network-use-and-privacy">What it connects to</a></p></article>
  <article><h3>Lightweight</h3><p>Built on the Python standard library and shipped as one standalone app per platform. The help is built in (F1), and your favorites, tabs and settings are remembered.</p></article>
  <article><h3>Made for the job</h3><p>Paste <code>show</code> output, firewall logs or AS paths and the tools pick out what they need. Right-click → <strong>Send to</strong> moves anything between tools, and every Copy gives neatly aligned text for tickets.</p></article>
</section>

<section class="highlights">
  <div class="wrap">
    <h2>Highlights</h2>
    <p class="section-lede">Some of the heavier lifting the toolbox does.</p>
    <div class="hl-grid">{hl_html}</div>
  </div>
</section>

<section class="tools">
  <div class="wrap">
    <h2>{N_TOOLS} tools, one window</h2>
    <p class="section-lede">Start from the Home tab, star the ones you use as favorites, and find the rest in the ☰ Tools menu.</p>
    <div class="tool-grid">{tools_html}</div>
    <p class="more"><a href="/help/">Full help for every tool →</a></p>
  </div>
</section>

<section class="gallery wrap">
  <h2>Screenshots</h2>
  <div class="gallery-grid">{"".join(shot(k) for k in ("route-table", "irr-rpki", "ping", "dns-digr", "bandwidth-cost"))}</div>
</section>

<section class="download" id="download">
  <div class="wrap">
    <h2>Download</h2>
    <p class="section-lede">Pre-built apps for each platform — no Python needed. {VERSION_LINE}.</p>
    <div class="dl-grid">{dl_cards}</div>
    <div class="dl-notes">
      <p><strong>First run:</strong> builds aren’t code-signed yet. On Windows choose <em>More info → Run anyway</em> in SmartScreen; on macOS right-click the app and choose <em>Open</em>.</p>
      <p><a href="{RELEASE_PAGE}" rel="noopener">Release notes &amp; files</a> \u00b7 <a href="{GITHUB}" rel="noopener">Source code on GitHub</a> · <a href="/details.html#run-it">Run from source with Python 3.9+</a> · <a href="/help/">Help</a></p>
    </div>
  </div>
</section>
'''
open(f"{OUT}/index.html", "w").write(page("/", "Brian’s Tools — Network Toolbox",
     "A local, lightweight network toolkit for Windows, macOS and Linux: subnet calculator, DNS dig, ping, traceroute, whois, route table analyzer, IRR/RPKI prefix filters and more.",
     index, "Home"))

# ================================================================== details.html  (from README.md)
src = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
src = re.sub(r"^# .*\n", "", src, count=1)
body = MD.render(src)
h2s = []
def h2(m):
    t = m.group(1); h2s.append((slug(t), strip_tags(t))); return f'<h2 id="{slug(t)}">{t}</h2>'
body = re.sub(r"<h2>(.*?)</h2>", h2, body)
feats = []
def li(m):
    name = strip_tags(m.group(2)).rstrip(":")
    if not re.match(r"^[A-Z][\w &/\-]*$", name) or len(name) > 34 or name.startswith(("Ctrl", "Mouse")):
        return m.group(0)
    a = "f-" + slug(re.sub(r" tab$", "", name))
    if any(a == x for x, _ in feats): return m.group(0)
    feats.append((a, re.sub(r" tab$", "", name)))
    return f'<li id="{a}" class="feature">{m.group(1)}<strong>{m.group(2)}</strong>'
# only top-level feature bullets (inside the Features section)
fstart = body.find('<h2 id="features">'); fend = body.find("<h2", fstart + 5)
fsec = re.sub(r"<li>(\s*(?:<p>)?)<strong>([^<]+?:)</strong>", li, body[fstart:fend], count=0)
# un-mark nested ones: a feature li must be a direct child of the top-level <ul>
depth, out, i = 0, [], 0
for tok in re.split(r"(<ul>|</ul>|<li id=\"f-[^\"]+\" class=\"feature\">)", fsec):
    if tok == "<ul>": depth += 1
    elif tok == "</ul>": depth -= 1
    elif tok.startswith('<li id="f-') and depth > 1:
        fid = re.search(r'id="([^"]+)"', tok).group(1); feats[:] = [f for f in feats if f[0] != fid]; tok = "<li>"
    out.append(tok)
body = body[:fstart] + "".join(out) + body[fend:]
body = post(body)
paras = re.findall(r"<p>.*?</p>", body[:body.find("<h2")], re.S)
for p in paras: body = body.replace(p, "", 1)
intro = next((p for p in paras if "desktop toolkit" in p), paras[-1])
tagline = next((p for p in paras if p.startswith("<p><em>")), "")
dtoc = '<ul class="toc">' + "".join(
    f'<li><a href="#{s}">{t}</a>' + (("<ul>" + "".join(f'<li><a href="#{a}">{n}</a></li>' for a, n in feats) + "</ul>") if s == "features" else "") + "</li>"
    for s, t in h2s) + "</ul>"
details = f'''
<section class="page-head"><div class="wrap">
  <p class="eyebrow">Details · README</p>
  <h1>Brian’s Tools</h1>
  <div class="lede">{intro}</div>
  <p class="ver-chip">{VERSION_LINE}</p>
  {tagline.replace("<p>", '<p class="tagline">', 1)}
  <p class="cta"><a class="btn btn-primary" href="/#download">Download</a> <a class="btn btn-ghost" href="/help/">Help</a> <a class="btn btn-ghost" href="{GITHUB}" rel="noopener">{GH_SVG} GitHub</a></p>
</div></section>
<div class="wrap doc-layout">
  <aside class="doc-toc" aria-label="On this page"><p class="toc-title">On this page</p>{dtoc}</aside>
  <article class="doc">{body}</article>
</div>
'''
open(f"{OUT}/details.html", "w").write(page("/details.html", "Details — Brian’s Tools",
     "Technical details for Brian’s Tools from the README: running from source, every feature, settings, building, and the source files.",
     details, "Details"))

# ================================================================== contact.html
contact = f'''
<section class="page-head"><div class="wrap">
  <p class="eyebrow">Contact</p>
  <h1>Get in touch</h1>
  <p class="lede-plain">Questions, ideas for a new tool, or something not working the way you expect? Send me a note.</p>
</div></section>
<div class="wrap contact-grid">
  <article class="contact-card">
    <h2>Email</h2>
    <p><a class="email" href="mailto:{EMAIL}">{EMAIL}</a></p>
    <h2>Bugs &amp; feature requests</h2>
    <p>For something reproducible, a GitHub issue is the quickest way to get it fixed. In the app, <strong>☰ Tools → About Brian’s Tools → Copy version info</strong> copies the version and OS details to include.</p>
    <p><a class="btn btn-ghost-dark" href="{GITHUB}/issues" rel="noopener">{GH_SVG} Open an issue</a></p>
    <h2>Help first?</h2>
    <p>The <a href="/help/">help guide</a> has a <a href="/help/#troubleshooting">troubleshooting</a> section covering the common snags.</p>
  </article>
  <form class="contact-form" id="contact-form" novalidate>
    <h2>Write a message</h2>
    <p class="muted">This opens your email app with the message filled in — nothing is sent from this website.</p>
    <label>Subject<select name="topic"><option>General question</option><option>Bug report</option><option>Feature idea</option><option>Other</option></select></label>
    <label>Your name<input name="name" autocomplete="name"></label>
    <label>Message<textarea name="message" rows="7" required></textarea></label>
    <button class="btn btn-primary" type="submit">Open in email app</button>
  </form>
</div>
'''
open(f"{OUT}/contact.html", "w").write(page("/contact.html", "Contact — Brian’s Tools",
     "Contact Brian about Brian’s Tools: questions, bug reports and feature ideas.", contact, "Contact"))

# ================================================================== 404.html
nf = '''<section class="page-head"><div class="wrap"><p class="eyebrow">404</p><h1>Request timed out</h1>
<p class="lede-plain">That page didn’t answer. 100% packet loss.</p>
<p class="cta"><a class="btn btn-primary" href="/">Back to home</a> <a class="btn btn-ghost" href="/help/">Help</a></p></div></section>'''
open(f"{OUT}/404.html", "w").write(page("/404.html", "Not found — Brian’s Tools", "Page not found.", nf, ""))

# ================================================================== CSS / JS / hosting files
shutil.copy(os.path.join(HERE, "site.css"), f"{OUT}/assets/css/site.css")
open(f"{OUT}/assets/js/site.js", "w").write(open(os.path.join(HERE, "site.js")).read().replace("__EMAIL__", EMAIL))
open(f"{OUT}/CNAME", "w").write("brianstools.net\n")
open(f"{OUT}/.nojekyll", "w").write("")
open(f"{OUT}/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
today = datetime.date.today().isoformat()
open(f"{OUT}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE_URL}/{p}</loc><lastmod>{today}</lastmod></url>\n" for p in ("", "help/", "details.html", "contact.html")) + "</urlset>\n")
open(f"{OUT}/README.md", "w").write(f"""# brianstools-site

Source of **{SITE_URL}**, the website for [Brian's Tools]({GITHUB}), served by GitHub Pages from this repo's `main` branch (root).
Generated by `build_site.py` from the app's README.md, help.md and version.py ({V.VERSION}).

- Screenshots: replace the PNGs in `assets/img/screenshots/` (same names, 1600x1000). Rebuilds keep them.
- Downloads: buttons point to the GitHub release assets in `DL` (build_site.py).
""")
print(f"built {OUT}  ({N_TOOLS} tools, help sections: {len(htoc)}, README features: {len(feats)})")
