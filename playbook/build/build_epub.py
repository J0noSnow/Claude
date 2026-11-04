#!/usr/bin/env python3
"""Build a reflowable EPUB (Kobo-friendly) from the playbook markdown."""
import re, subprocess, sys, json, shutil, warnings
from pathlib import Path
warnings.filterwarnings('ignore')
from bs4 import BeautifulSoup
sys.path.insert(0, str(Path(__file__).parent))
import build_pdf as bp
from figures import FIGURES
from PIL import Image

ROOT = bp.ROOT
OUT = ROOT / 'essay-led-creator-playbook.epub'
WORK = Path('/tmp/claude-0/epubbuild'); shutil.rmtree(WORK, ignore_errors=True); WORK.mkdir(parents=True)
IMG = WORK / 'img'; IMG.mkdir()
used = []   # figure ids in document order

def make_figure_img(fid, soup):
    fn, cap = FIGURES[fid]
    bp.fig_counter[0] += 1
    n = bp.fig_counter[0]; used.append((n, fid))
    alt = f'Figure {n}: {cap}'
    f = BeautifulSoup(f'<figure class="diagram"><img src="fig{n}.png" alt="{alt}"/><figcaption><b>Figure {n}.</b> {cap}</figcaption></figure>', 'html.parser')
    return f.figure
bp.make_figure = make_figure_img

SHOT_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  for (const j of jobs) {
    const p = await b.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.scale });
    await p.goto('file://' + j.html, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    if (j.selector) { await (await p.$(j.selector)).screenshot({ path: j.png }); }
    else { await p.screenshot({ path: j.png }); }
    await p.close();
  }
  await b.close();
})();
"""

def screenshots(jobs):
    jf = WORK / 'jobs.json'; jf.write_text(json.dumps(jobs)); js = WORK / 'shot.js'; js.write_text(SHOT_JS)
    subprocess.run(['node', str(js), str(jf)], check=True)

def main():
    segs = bp.split_segments(bp.MD.read_text())
    for s in segs: s['html'] = bp.process(s)
    # --- figures -> grayscale PNG
    jobs = []
    for n, fid in used:
        svg = FIGURES[fid][0]()
        h = WORK / f'fig{n}.html'
        h.write_text(f'<!doctype html><html><body style="margin:0;background:#fff"><div id="f" style="width:1100px;padding:10px;background:#fff">{svg}</div></body></html>')
        jobs.append(dict(html=str(h), png=str(IMG / f'fig{n}.png'), w=1140, h=900, scale=2, selector='#f'))
    # --- cover
    cov = WORK / 'cover.html'
    cov.write_text('''<!doctype html><html><body style="margin:0;background:#0a0a0a;color:#fff;font-family:Inter,sans-serif;width:1200px;height:1800px;position:relative;overflow:hidden">
<div style="position:absolute;right:-420px;top:-380px;width:1000px;height:1000px;border:3px solid #2a2a2a;border-radius:50%"></div>
<div style="position:absolute;left:110px;top:130px;font-size:30px;letter-spacing:.32em;color:#9a9a9a;font-weight:600">A PRACTICAL PLAYBOOK</div>
<div style="position:absolute;left:110px;top:520px;font-size:176px;line-height:.95;font-weight:800;letter-spacing:-.035em;text-transform:uppercase">The<br>Essay-Led<br>Creator<br>Playbook</div>
<div style="position:absolute;left:110px;top:1210px;width:190px;height:12px;background:#fff"></div>
<div style="position:absolute;left:110px;top:1260px;width:900px;font-size:46px;line-height:1.3;color:#d6d6d6">Ideas, audience, newsletter, offers and launches for the solo writer</div>
<div style="position:absolute;left:110px;top:1620px;font-size:32px;color:#bdbdbd;line-height:1.6"><b style="color:#fff">Prepared for Jonathan Nott</b><br>Jono&rsquo;s Journal</div>
</body></html>''')
    jobs.append(dict(html=str(cov), png=str(WORK / 'cover_rgb.png'), w=1200, h=1800, scale=1, selector=None))
    screenshots(jobs)
    for n, fid in used:
        p = IMG / f'fig{n}.png'; Image.open(p).convert('L').save(p, optimize=True)
    Image.open(WORK / 'cover_rgb.png').convert('L').save(WORK / 'cover.png', optimize=True)
    # --- html
    parts = []
    for s in segs:
        if s['kind'] == 'front': title = 'Start here'
        elif s['kind'] == 'part': title = f'Part {s["num"]}: {s["title"]}'
        elif s['kind'] == 'appx': title = f'Appendix {s["num"]}: {s["title"]}'
        else: title = 'Your next 7 days'
        parts.append(f'<h1>{title}</h1>\n{s["html"]}')
    (WORK / 'book.html').write_text('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>The Essay-Led Creator Playbook</title></head><body>' + '\n'.join(parts) + '</body></html>')
    shutil.copy(Path(__file__).parent / 'epub.css', WORK / 'epub.css')
    meta = WORK / 'meta.yaml'
    meta.write_text('''---
title: The Essay-Led Creator Playbook
subtitle: Ideas, audience, newsletter, offers and launches for the solo writer
author: Prepared for Jonathan Nott
lang: en-GB
date: 2026-11
publisher: Personal copy
rights: Original synthesis for personal use
description: A practical playbook, with exercises and diagrams, built from a study of one creator's published letters and written in original words.
...
''')
    subprocess.run(['pandoc', '-f', 'html', '-t', 'epub3', 'book.html', '--metadata-file=meta.yaml', '--css=epub.css',
                    '--epub-cover-image=cover.png', '--toc', '--toc-depth=2', '--split-level=1', '--resource-path=.:img',
                    '-o', str(OUT)], cwd=WORK, check=True)
    print('wrote', OUT, OUT.stat().st_size // 1024, 'KB; figures:', len(used))

if __name__ == '__main__':
    main()
