#!/usr/bin/env python3
"""Build the designed PDF: markdown -> HTML (pandoc) -> PDF (Chromium) -> page numbers."""
import re, subprocess, sys, os, io, warnings
from pathlib import Path
warnings.filterwarnings('ignore')
from bs4 import BeautifulSoup, NavigableString
sys.path.insert(0, str(Path(__file__).parent))
from figures import FIGURES

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / 'essay-led-creator-playbook.md'
OUT = ROOT / 'essay-led-creator-playbook.pdf'
TMP = Path('/tmp/claude-0/pdfbuild'); TMP.mkdir(parents=True, exist_ok=True)

TAGLINES = {
    'front': 'How the whole system fits together, and how to use this book.',
    1: 'Know what you stand for, who you serve, and what you want to be known for.',
    2: 'Collect, test and name ideas so you never face a blank page.',
    3: 'Reach new readers with daily writing and honest distribution.',
    4: 'Make one weekly essay the engine of everything else.',
    5: 'Decide what people can pay you for, and in what order.',
    6: 'Design, test and pre-sell your first course or digital product.',
    7: 'Write the page, set the date, run a three-week launch.',
    8: 'Thirteen weeks, one dashboard, three decision gates.',
    'appx': 'Reference material: exercise index, glossary, AI recipes, reality check.',
}

# ------------------------------------------------------------------ parse markdown
def split_segments(md):
    lines = md.split('\n')
    # drop title block before first "## How to use"
    start = next(i for i, l in enumerate(lines) if l.startswith('## How to use'))
    lines = lines[start:]
    segs = []; cur = {'head': None, 'lines': []}; fence = False
    for l in lines:
        if l.startswith('```'): fence = not fence
        if not fence and re.match(r'^# (?!#)', l):
            segs.append(cur); cur = {'head': l[2:].strip(), 'lines': []}
        else:
            cur['lines'].append(l)
    segs.append(cur)
    out = []
    for i, s in enumerate(segs):
        h = s['head']; body = '\n'.join(s['lines']).strip()
        body = re.sub(r'(\n---\s*)+$', '', body).strip()
        if h is None: out.append(dict(kind='front', key='front', num=None, title='Start here', md=body)); continue
        m = re.match(r'(?i)^part\s*(\d+)\s*:\s*(.*)$', h)
        if m: out.append(dict(kind='part', key=f'p{int(m.group(1))}', num=int(m.group(1)), title=m.group(2).strip().title() if m.group(2).isupper() else m.group(2).strip(), md=body)); continue
        m = re.match(r'(?i)^appendix\s+([A-E])\s*:\s*(.*)$', h)
        if m: out.append(dict(kind='appx', key=f'a{m.group(1).upper()}', num=m.group(1).upper(), title=m.group(2).strip(), md=body)); continue
        out.append(dict(kind='final', key='final', num=None, title='Your next 7 days', md=body))
    return out

def pandoc(md):
    r = subprocess.run(['pandoc', '-f', 'markdown+smart', '-t', 'html5', '--wrap=none'], input=md, capture_output=True, text=True, check=True)
    return r.stdout

# ------------------------------------------------------------------ html processing
FIG_PLAN = {  # segment key -> list of (h2 prefix, figure id, anchor mode)
    'front': [('The Koe model on one page', 'model', 'replace_pre')],
    'p1': [('Lesson 1.2', 'map', 'after_p')],
    'p3': [('Lesson 5', 'ecosystem', 'after_p')],
    'p4': [('Lesson 2', 'essay', 'after_p')],
    'p5': [('Lesson 1', 'ladder', 'after_list')],
    'p7': [('Lesson 2', 'landing', 'after_p'), ('Lesson 6', 'launch', 'after_list')],
    'p8': [('The thirteen weeks', 'timeline', 'after_p')],
}
fig_counter = [0]

def make_figure(fid, soup):
    fn, cap = FIGURES[fid]
    fig_counter[0] += 1
    f = BeautifulSoup(f'<figure class="diagram">{fn()}<figcaption><b>Figure {fig_counter[0]}.</b> {cap}</figcaption></figure>', 'html.parser')
    return f.figure

def h2_by_prefix(soup, prefix):
    for h in soup.find_all('h2'):
        if h.get_text().strip().startswith(prefix): return h
    return None

def process(seg):
    html = pandoc(seg['md'])
    soup = BeautifulSoup(html, 'html.parser')
    # lesson list for divider
    items = []
    for h in soup.find_all('h2'):
        t = h.get_text().strip()
        if re.match(r'(?i)^(exercises|challenge your|recap|part \d recap|introduction|intro$|before you begin|legend)', t): continue
        t = re.sub(r'^(Lesson\s+[\w.]+:\s*)', '', t)
        items.append(t)
    seg['items'] = items
    # figures
    for prefix, fid, mode in FIG_PLAN.get(seg['key'], []):
        h = h2_by_prefix(soup, prefix)
        if h is None: print('!! missing anchor', seg['key'], prefix); continue
        fig = make_figure(fid, soup)
        if mode == 'replace_pre':
            pre = h.find_next('pre')
            pre.replace_with(fig)
        else:
            sib = h.find_next_sibling()
            anchor = None
            if mode == 'after_list':
                n = h; steps = 0
                while n is not None and steps < 6:
                    n = n.find_next_sibling(); steps += 1
                    if n is not None and n.name in ('ol', 'ul'): anchor = n; break
                    if n is not None and n.name == 'h2': break
            if anchor is None: anchor = sib if sib is not None and sib.name == 'p' else h
            anchor.insert_after(fig)
    # tags [DEMO] / [OPINION]
    pat = re.compile(r'\[((?:DEMO|OPINION)[^\]\n]*)\]')
    for tn in list(soup.find_all(string=True)):
        if tn.find_parent(['pre', 'code']): continue
        s = str(tn)
        if not pat.search(s): continue
        frag = []; last = 0
        for m in pat.finditer(s):
            frag.append(NavigableString(s[last:m.start()]))
            inner = m.group(1); cls = 'demo' if inner.startswith('DEMO') else 'opinion'
            sp = soup.new_tag('span', attrs={'class': f'tag {cls}'}); sp.string = inner
            frag.append(sp); last = m.end()
        frag.append(NavigableString(s[last:]))
        for f in reversed(frag): tn.insert_after(f)
        tn.extract()
    # checkboxes
    for inp in soup.find_all('input'):
        sp = soup.new_tag('span', attrs={'class': 'cb'}); inp.replace_with(sp)
    for tn in list(soup.find_all(string=re.compile(r'\[ \]'))):
        if tn.find_parent(['pre', 'code']): continue
        parts = re.split(r'\[ \]', str(tn)); new = []
        for i, p in enumerate(parts):
            new.append(NavigableString(p))
            if i < len(parts) - 1:
                new.append(soup.new_tag('span', attrs={'class': 'cb'}))
        for f in reversed(new): tn.insert_after(f)
        tn.extract()
    # wrap boxes
    for h in list(soup.find_all('h2')):
        t = h.get_text().strip().lower()
        cls = None
        if t.startswith('exercises') or t.startswith('offer worksheet'): cls = 'exercises'
        elif t.startswith('challenge your'): cls = 'challenge'
        elif 'recap' in t: cls = 'recap'
        if not cls: continue
        wrap = soup.new_tag('div', attrs={'class': f'box {cls}'})
        h.insert_before(wrap)
        nodes = [h]; n = h.next_sibling
        while n is not None and not (getattr(n, 'name', None) in ('h1', 'h2')):
            nodes.append(n); n = n.next_sibling
        for x in nodes: wrap.append(x.extract())
    # strip trailing hr inside
    for hr in soup.find_all('hr'):
        if hr.find_next_sibling() is None: hr.decompose()
    return str(soup)

# ------------------------------------------------------------------ html shell
CSS = r'''
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Bitstream Charter", "Charter", Georgia, serif; font-size: 10pt; line-height: 1.52; color: #0a0a0a; background: #fff; }
.black { width: 210mm; height: 296.6mm; background: #0a0a0a; color: #fff; padding: 24mm 22mm 22mm 22mm; break-after: page; overflow: hidden; position: relative; display: flex; flex-direction: column; font-family: Inter, Helvetica, Arial, sans-serif; }
.zz { position: absolute; left: 0; top: 0; font-size: 1px; color: rgba(0,0,0,0); }
.black .zz { color: rgba(0,0,0,0); }
.wsec { break-before: page; }
.wsec.first { break-before: auto; }
.wsec .zz, .sec .zz { position: static; display: block; height: 2px; font-size: 2px; line-height: 2px; overflow: hidden; }
/* cover */
.cover .kick { font-size: 8.5pt; letter-spacing: .32em; text-transform: uppercase; color: #9a9a9a; font-weight: 600; }
.cover .titleblock { margin-top: auto; margin-bottom: auto; }
.cover h1 { font-size: 66pt; line-height: .96; letter-spacing: -.035em; font-weight: 800; margin: 0 0 9mm 0; text-transform: uppercase; }
.cover .rule { width: 34mm; height: 1.4mm; background: #fff; margin: 0 0 8mm 0; }
.cover .sub { font-size: 15pt; line-height: 1.35; color: #d6d6d6; font-weight: 400; max-width: 120mm; }
.cover .foot { font-size: 9.5pt; color: #bdbdbd; line-height: 1.6; }
.cover .foot b { color: #fff; font-weight: 600; }
.cover .ring { position: absolute; right: -60mm; top: -50mm; width: 150mm; height: 150mm; border: .5mm solid #262626; border-radius: 50%; }
.cover .ring2 { position: absolute; right: -35mm; top: -25mm; width: 100mm; height: 100mm; border: .5mm solid #1c1c1c; border-radius: 50%; }
/* toc */
.toc h2 { font-size: 8.5pt; letter-spacing: .32em; text-transform: uppercase; color: #9a9a9a; font-weight: 600; margin: 0 0 14mm 0; }
.toc .row { display: flex; align-items: baseline; gap: 4mm; padding: 2.4mm 0; border-bottom: .3pt solid #2b2b2b; }
.toc .row .n { width: 16mm; font-size: 9pt; color: #8a8a8a; font-weight: 600; letter-spacing: .12em; }
.toc .row .t { font-size: 12.5pt; font-weight: 600; color: #fff; }
.toc .row .sp { flex: 1; border-bottom: .5pt dotted #4a4a4a; transform: translateY(-1.2mm); }
.toc .row .p { font-size: 10pt; color: #bdbdbd; font-variant-numeric: tabular-nums; }
.toc .row.sub { padding: 1.6mm 0; }
.toc .row.sub .t { font-size: 10.5pt; font-weight: 400; color: #d0d0d0; }
.toc .row.sub .n { color: #6a6a6a; }
.toc .note { margin-top: auto; font-size: 8.5pt; color: #7a7a7a; line-height: 1.5; }
/* divider */
.divider .kick { font-size: 8.5pt; letter-spacing: .32em; text-transform: uppercase; color: #9a9a9a; font-weight: 600; }
.divider .big { font-size: 190pt; line-height: .8; font-weight: 800; letter-spacing: -.06em; margin-top: 18mm; color: #fff; }
.divider h1 { font-size: 36pt; line-height: 1.05; font-weight: 800; letter-spacing: -.025em; margin: 10mm 0 5mm 0; max-width: 150mm; }
.divider .tagline { font-size: 13pt; color: #bdbdbd; line-height: 1.4; max-width: 120mm; }
.divider .list { margin-top: auto; border-top: .4pt solid #3a3a3a; padding-top: 6mm; column-count: 2; column-gap: 10mm; font-size: 8.8pt; line-height: 1.45; color: #cfcfcf; list-style: none; padding-left: 0; margin-bottom: 0; }
.divider .list li { break-inside: avoid; padding: .7mm 0; display: block; }
.divider .list li::before { content: "\2192"; color: #6a6a6a; margin-right: 2mm; }
.divider.appx .big { font-size: 120pt; }
/* body */
.sec { font-family: "Bitstream Charter", Georgia, serif; }
h1, h2, h3, h4 { font-family: Inter, Helvetica, Arial, sans-serif; color: #0a0a0a; }
.black h1, .black h2, .black h3 { color: #fff; }
h2, h3, h4 { break-inside: avoid; }
h2 { font-size: 15.5pt; font-weight: 800; letter-spacing: -.015em; line-height: 1.18; margin: 9mm 0 3.2mm 0; break-after: avoid; }
h2::before { content: ""; display: block; width: 11mm; height: 1.3mm; background: #0a0a0a; margin-bottom: 3mm; }
h3 { font-size: 8.6pt; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: 6mm 0 1.8mm 0; break-after: avoid; color: #0a0a0a; }
h4 { font-size: 10pt; font-weight: 700; margin: 4mm 0 1mm 0; break-after: avoid; }
p { margin: 0 0 2.7mm 0; orphans: 3; widows: 3; }
strong { font-weight: 700; }
a { color: inherit; text-decoration: underline; }
ul, ol { margin: 0 0 3mm 0; padding-left: 5.2mm; }
li { margin: 0 0 1mm 0; }
li > p { margin-bottom: 1mm; }
ul li::marker { color: #0a0a0a; }
ul:has(.cb) { list-style: none; padding-left: 0; }
ul:has(.cb) li { padding-left: 6.5mm; position: relative; }
.cb { display: inline-block; width: 3.1mm; height: 3.1mm; border: .45mm solid #0a0a0a; border-radius: .6mm; vertical-align: -.5mm; margin-right: 1.6mm; }
ul:has(.cb) li .cb:first-child { position: absolute; left: 0; top: 1.1mm; }
blockquote { margin: 3mm 0; padding: .5mm 0 .5mm 4.5mm; border-left: 1.1mm solid #0a0a0a; color: #222; font-style: italic; }
hr { border: 0; border-top: .4pt solid #cfcfcb; margin: 7mm 0; }
code { font-family: "JetBrains Mono", monospace; font-size: 8.4pt; background: #f1f1ee; padding: .2mm 1mm; border-radius: .8mm; }
pre { font-family: "JetBrains Mono", monospace; font-size: 7.5pt; line-height: 1.45; background: #f4f4f1; border: .4pt solid #d6d6d2; border-left: 1.1mm solid #0a0a0a; padding: 4mm 4.5mm; margin: 3.5mm 0 4.5mm 0; white-space: pre-wrap; word-break: break-word; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: inherit; }
table { width: 100%; border-collapse: collapse; margin: 3.5mm 0 5mm 0; font-family: Inter, Helvetica, Arial, sans-serif; font-size: 8.3pt; line-height: 1.4; table-layout: auto; }
th { background: #0a0a0a; color: #fff; text-align: left; font-weight: 600; padding: 2mm 2.4mm; letter-spacing: .02em; }
td { padding: 1.9mm 2.4mm; border-bottom: .4pt solid #cfcfcb; vertical-align: top; }
tr { break-inside: avoid; }
tbody tr:nth-child(even) td { background: #f7f7f5; }
td p { margin: 0; }
colgroup { display: none; }
.tag { font-family: Inter, Helvetica, Arial, sans-serif; font-size: 6.6pt; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; padding: .4mm 1.6mm; border-radius: 1mm; vertical-align: .25mm; white-space: nowrap; }
.tag.demo { background: #0a0a0a; color: #fff; }
.tag.opinion { border: .35mm solid #0a0a0a; color: #0a0a0a; }
figure.diagram { margin: 5mm 0 6mm 0; padding: 5mm 5mm 3mm 5mm; border: .4pt solid #cfcfcb; border-radius: 1.5mm; background: #fff; break-inside: avoid; }
figure.diagram svg { display: block; width: 100%; height: auto; }
figcaption { font-family: Inter, Helvetica, Arial, sans-serif; font-size: 8pt; color: #555; margin-top: 3mm; line-height: 1.4; }
figcaption b { color: #0a0a0a; }
.box { margin: 8mm 0 6mm 0; padding: 5mm 6mm 3mm 6mm; border-radius: 1.2mm; break-inside: avoid; }
.box h2 { margin-top: 0; font-size: 12.5pt; }
.box.exercises { background: #f4f4f1; border-left: 1.8mm solid #0a0a0a; }
.box.exercises h2::before { display: none; }
.box.exercises h2 { text-transform: uppercase; letter-spacing: .1em; font-size: 10pt; font-weight: 800; }
.box.challenge { border: .8pt solid #0a0a0a; break-inside: avoid; }
.box.challenge h2::before { display: none; }
.box.challenge h2 { text-transform: uppercase; letter-spacing: .1em; font-size: 10pt; font-weight: 800; }
.box.recap { background: #0a0a0a; color: #fff; break-inside: avoid; }
.box.recap h2 { color: #fff; text-transform: uppercase; letter-spacing: .1em; font-size: 10pt; font-weight: 800; }
.box.recap h2::before { display: none; }
.box.recap strong, .box.recap p { color: #fff; }
.box.recap a { color: #fff; }
.box h3 { margin-top: 4mm; }
.box.exercises table th { background: #0a0a0a; }
.appx-head { margin: 0 0 8mm 0; padding-bottom: 6mm; border-bottom: 1.2mm solid #0a0a0a; }
.appx-head .k { font-family: Inter, sans-serif; font-size: 8.5pt; letter-spacing: .3em; font-weight: 700; color: #6b6b6b; text-transform: uppercase; }
.appx-head h1 { font-size: 28pt; font-weight: 800; letter-spacing: -.025em; margin: 2mm 0 0 0; line-height: 1.05; }
.white { break-before: page; }
.white.first { break-before: auto; }
'''


from html import escape

PAGE_WHITE = '@page { size: A4; margin: 22mm 20mm 25mm 20mm; }'
PAGE_BLACK = '@page { size: A4; margin: 0; }'

def divider(seg, tagline, marker):
    items = ''.join(f'<li>{escape(i)}</li>' for i in seg['items'][:16])
    if seg['kind'] == 'front': kick, big, title = 'START HERE', '00', 'Start here'
    elif seg['kind'] == 'part': kick, big, title = f'PART {seg["num"]:02d}', f'{seg["num"]:02d}', seg['title']
    else: kick, big, title = 'REFERENCE', 'A–E', 'Appendices'
    cls = 'appx' if seg['kind'] == 'appx_div' else ''
    return (f'<section class="black divider {cls}">'
            f'<div class="kick">{kick}</div><div class="big">{big}</div><h1>{escape(title)}</h1>'
            f'<div class="tagline">{escape(tagline)}</div><ul class="list">{items}</ul></section>')

def build_sequence(segs, pages):
    """Return list of dicts: {type:'black'|'white', html, key, label}. pages: key -> page number (for the TOC)."""
    seq = []
    def pg(k): return pages.get(k, '')
    cover = ('<section class="black cover"><div class="ring"></div><div class="ring2"></div>'
             '<div class="kick">A practical playbook &middot; 2026</div>'
             '<div class="titleblock"><h1>The<br>Essay-Led<br>Creator<br>Playbook</h1><div class="rule"></div>'
             '<div class="sub">Replicating the Dan Koe model as a solo writer: ideas, audience, newsletter, offers and launches.</div></div>'
             '<div class="foot"><b>Prepared for Jonathan Nott</b><br>Jono&rsquo;s Journal &middot; jonathannott.substack.com<br>'
             'Built from 238 letters (222 free, 16 paid), summarised in original words</div></section>')
    seq.append(dict(type='black', html=cover, key='cover', label=''))
    rows = [('', 'Start here', 'div:front', False)]
    for s in segs:
        if s['kind'] == 'part': rows.append((f'{s["num"]:02d}', s['title'], f'div:{s["key"]}', False))
    rows.append(('A–E', 'Appendices', 'div:appx', False))
    for s in segs:
        if s['kind'] == 'appx': rows.append((s['num'], s['title'], f'sec:{s["key"]}', True))
    rows.append(('', 'Your next 7 days', 'sec:final', False))
    tr = ''.join(f'<div class="row{" sub" if sub else ""}"><span class="n">{n}</span><span class="t">{escape(t)}</span><span class="sp"></span><span class="p">{pg(m)}</span></div>' for n, t, m, sub in rows)
    toc = (f'<section class="black toc"><h2>Contents</h2>{tr}'
           '<div class="note">Tags used throughout: <b>DEMO</b> = something the source says it did. <b>OPINION</b> = a claim or recommendation. Treat both as evidence to test, not as guarantees.</div></section>')
    seq.append(dict(type='black', html=toc, key='toc', label=''))
    appx_div_done = False
    for s in segs:
        if s['kind'] == 'front':
            seq.append(dict(type='black', html=divider(s, TAGLINES['front'], ''), key='div:front', label='Start here'))
            seq.append(dict(type='white', html=f'<section class="sec">{s["html"]}</section>', key='sec:front', label='Start here'))
        elif s['kind'] == 'part':
            lab = f'Part {s["num"]}  ·  {s["title"]}'
            seq.append(dict(type='black', html=divider(s, TAGLINES[s['num']], ''), key=f'div:{s["key"]}', label=lab))
            seq.append(dict(type='white', html=f'<section class="sec">{s["html"]}</section>', key=f'sec:{s["key"]}', label=lab))
        elif s['kind'] == 'appx':
            if not appx_div_done:
                d = dict(kind='appx_div', items=[f'{x["num"]}  {x["title"]}' for x in segs if x['kind'] == 'appx'], num=None, title='Appendices')
                seq.append(dict(type='black', html=divider(d, TAGLINES['appx'], ''), key='div:appx', label='Appendices')); appx_div_done = True
            lab = f'Appendix {s["num"]}  ·  {s["title"]}'
            seq.append(dict(type='white', html=f'<section class="sec"><div class="appx-head"><div class="k">Appendix {s["num"]}</div><h1>{escape(s["title"])}</h1></div>{s["html"]}</section>', key=f'sec:{s["key"]}', label=lab))
        else:
            seq.append(dict(type='white', html=f'<section class="sec"><div class="appx-head"><div class="k">Start tomorrow</div><h1>{escape(s["title"])}</h1></div>{s["html"]}</section>', key='sec:final', label='Your next 7 days'))
    return seq

def doc(body, page_css):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The Essay-Led Creator Playbook</title><style>{page_css}{CSS}</style></head><body>{body}</body></html>'

RENDER_JS = r"""
const { chromium } = require('playwright');
(async () => {
  const [,, html, pdf] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + html, { waitUntil: 'load' });
  await p.emulateMedia({ media: 'print' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
"""

def render(html_path, pdf_path):
    js = TMP / 'render.js'; js.write_text(RENDER_JS)
    subprocess.run(['node', str(js), str(html_path), str(pdf_path)], check=True)

def render_pass(seq):
    from pypdf import PdfReader
    blacks = [x for x in seq if x['type'] == 'black']
    whites = [x for x in seq if x['type'] == 'white']
    bh = TMP / 'black.html'; bp = TMP / 'black.pdf'
    wh = TMP / 'white.html'; wp = TMP / 'white.pdf'
    bh.write_text(doc(''.join(x['html'] for x in blacks), PAGE_BLACK)); render(bh, bp)
    wbody = ''.join(f'<div class="wsec{" first" if i == 0 else ""}"><span class="zz">ZZSEC{i:02d}ZZ</span>{x["html"]}</div>' for i, x in enumerate(whites))
    wh.write_text(doc(wbody, PAGE_WHITE)); render(wh, wp)
    rb = PdfReader(str(bp)); rw = PdfReader(str(wp))
    assert len(rb.pages) == len(blacks), f'black pages {len(rb.pages)} != {len(blacks)} (a black page overflowed)'
    starts = {}
    for i, pg in enumerate(rw.pages):
        t = pg.extract_text() or ''
        for m in re.findall(r'ZZSEC(\d\d)ZZ', t): starts.setdefault(int(m), i)
    ranges = []
    for i in range(len(whites)):
        a = starts[i]; z = starts[i + 1] if i + 1 < len(whites) else len(rw.pages)
        ranges.append((a, z))
    # final order
    order = []; bi = wi = 0
    for x in seq:
        if x['type'] == 'black': order.append(('b', bi, x)); bi += 1
        else: a, z = ranges[wi]; order.extend(('w', k, x) for k in range(a, z)); wi += 1
    pages = {}
    for n, (t, k, x) in enumerate(order, start=1): pages.setdefault(x['key'], n)
    return rb, rw, order, pages

def merge(rb, rw, order, dst):
    from pypdf import PdfWriter, PdfReader
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font = 'Helvetica'
    for cand in ['/usr/share/fonts/truetype/inter/Inter-Medium.ttf']:
        if os.path.exists(cand): pdfmetrics.registerFont(TTFont('InterM', cand)); font = 'InterM'
    w = PdfWriter(); mm = 2.8346
    for n, (t, k, x) in enumerate(order, start=1):
        if t == 'b': w.add_page(rb.pages[k]); continue
        p = rw.pages[k]
        W = float(p.mediabox.width); H = float(p.mediabox.height)
        buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(W, H))
        c.setFillColor(HexColor('#8a8a86')); c.setFont(font, 7.2)
        c.drawString(20 * mm, 12.5 * mm, (x['label'] or 'The Essay-Led Creator Playbook').upper())
        c.setFillColor(HexColor('#0a0a0a')); c.setFont(font, 8.2)
        c.drawRightString(W - 20 * mm, 12.5 * mm, str(n))
        c.setStrokeColor(HexColor('#cfcfcb')); c.setLineWidth(0.4)
        c.line(20 * mm, 17.5 * mm, W - 20 * mm, 17.5 * mm)
        c.save(); buf.seek(0)
        p.merge_page(PdfReader(buf).pages[0]); w.add_page(p)
    w.add_metadata({'/Title': 'The Essay-Led Creator Playbook', '/Author': 'Prepared for Jonathan Nott', '/Subject': "Playbook for Jono's Journal"})
    with open(dst, 'wb') as f: w.write(f)

def main():
    segs = split_segments(MD.read_text())
    for s in segs: s['html'] = process(s)
    seq = build_sequence(segs, {})
    rb, rw, order, pages = render_pass(seq)
    seq = build_sequence(segs, pages)              # fills in TOC page numbers
    rb, rw, order2, pages2 = render_pass(seq)
    assert pages2 == pages, 'page map shifted'
    merge(rb, rw, order2, OUT)
    print('pages:', len(order2), 'figures:', fig_counter[0])
    print(pages2)

if __name__ == '__main__':
    main()
