"""Original vector diagrams for the playbook (inline SVG, monochrome)."""
from html import escape

INK = '#0a0a0a'; GREY = '#6b6b6b'; LIGHT = '#efefec'; MID = '#d4d4d0'

def _defs():
    return ('<defs>'
            f'<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
            f'<marker id="ahg" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{GREY}"/></marker>'
            '</defs>')

def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" '
            f'font-family="Inter, Helvetica, Arial, sans-serif">{_defs()}{body}</svg>')

def text(x, y, s, size=11, weight=400, fill=INK, anchor='middle', style='', ls=0):
    st = f' font-style="italic"' if style == 'italic' else ''
    lsp = f' letter-spacing="{ls}"' if ls else ''
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{st}{lsp}>{escape(s)}</text>')

def box(x, y, w, h, title, sub=(), fill='#fff', stroke=INK, tc=None, sc=None, dash=False, r=4, tsize=12.5, ssize=10, sw=1.4):
    tc = tc or (('#fff' if fill == INK else INK))
    sc = sc or (('#cfcfcf' if fill == INK else GREY))
    d = ' stroke-dasharray="5 4"' if dash else ''
    out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
    n = len(sub)
    lh_t, lh_s = 16, 13.5
    total = lh_t + n * lh_s
    y0 = y + (h - total) / 2 + 12
    if title:
        out += text(x + w / 2, y0, title, tsize, 700, tc)
    for i, s in enumerate(sub):
        out += text(x + w / 2, y0 + lh_t + i * lh_s - 1, s, ssize, 400, sc)
    return out

def arrow(x1, y1, x2, y2, dash=False, grey=False):
    col = GREY if grey else INK
    d = ' stroke-dasharray="5 4"' if dash else ''
    m = 'ahg' if grey else 'ah'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.4"{d} marker-end="url(#{m})"/>'

def path(d, dash=False, grey=False, arrow_end=True):
    col = GREY if grey else INK
    da = ' stroke-dasharray="5 4"' if dash else ''
    m = ' marker-end="url(#ahg)"' if (arrow_end and grey) else (' marker-end="url(#ah)"' if arrow_end else '')
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.4"{da}{m}/>'

# ---------------------------------------------------------------- F1
def fig_model():
    b = []
    # feedback loop above row 1
    b.append(path('M320,48 L320,14 L56,14 L56,40', dash=True, grey=True))
    b.append(text(188, 9, 'essays and replies generate new ideas', 9.5, 400, GREY, style='italic'))
    y = 40; h = 92; w = 112
    xs = [0, 132, 264, 396, 528]
    items = [
        ('1  IDEAS', ['idea museum,', 'reading, walks,', 'thinking partner']),
        ('2  SHORT-FORM', ['daily posts, replies,', 'notes: reach and', 'testing']),
        ('3  NEWSLETTER', ['weekly essay,', 'the home base', 'and "stealth page"']),
        ('4  LEAD MAGNET', ['free, one small', 'result, builds', 'the list']),
        ('5  MICRO OFFER', ['$10-20 guide or', 'small 1:1 pack', 'first paying proof']),
    ]
    for i, (t, s) in enumerate(items):
        fill = INK if i == 4 else '#fff'
        b.append(box(xs[i], y, w, h, t, s, fill=fill, tsize=11.5, ssize=9.5))
        if i < 4:
            b.append(arrow(xs[i] + w + 1, y + h / 2, xs[i + 1] - 2, y + h / 2))
    b.append(text(226, y + h + 16, 'posts link to the essay  /  the essay is cut into posts', 9.5, 400, GREY, style='italic'))
    # ladder
    b.append(path(f'M584,{y+h+2} L584,176', arrow_end=True))
    b.append(box(0, 176, 640, 62, 'THE LADDER', ['micro offer  >  cohort  >  standalone course  >  community / book / software  (one rung at a time, each teaches the next)'], tsize=12.5, ssize=10))
    b.append(arrow(320, 239, 320, 264))
    b.append(box(0, 265, 640, 54, 'LAUNCH', ['dated, three weeks, honest scarcity, content narrowed to the offer'], fill=INK, tsize=12.5, ssize=10))
    # weekly rhythm strip
    b.append(text(0, 346, 'WEEKLY RHYTHM', 9.5, 700, GREY, anchor='start', ls=1.5))
    days = [('MON', 'outline'), ('TUE', 'draft'), ('WED', 'finish'), ('THU', 'publish'), ('FRI', 'mine posts'), ('SAT', 'read, walk'), ('SUN', 'review')]
    cw = 640 / 7
    for i, (d, t) in enumerate(days):
        x = i * cw
        b.append(f'<rect x="{x+1.5:.1f}" y="352" width="{cw-3:.1f}" height="44" rx="3" fill="{LIGHT}" stroke="{MID}"/>')
        b.append(text(x + cw / 2, 369, d, 10.5, 700))
        b.append(text(x + cw / 2, 385, t, 9.5, 400, GREY))
    return svg(640, 404, ''.join(b))

# ---------------------------------------------------------------- F2
def fig_content_map():
    b = []
    ys = [38, 140, 242]
    b.append(f'<circle cx="46" cy="140" r="42" fill="{INK}"/>')
    b.append(text(46, 136, 'ANTI-', 11, 700, '#fff')); b.append(text(46, 150, 'VISION', 11, 700, '#fff'))
    b.append(f'<circle cx="594" cy="140" r="42" fill="{INK}"/>')
    b.append(text(594, 144, 'VISION', 11, 700, '#fff'))
    for i, yy in enumerate(ys):
        b.append(path(f'M88,140 C110,140 110,{yy} 132,{yy}', grey=True))
        b.append(box(134, yy - 22, 120, 44, f'TERRITORY {"ABC"[i]}', ['broad topic'], fill='#fff', tsize=11, ssize=9.5))
        for j in range(3):
            px = 282 + j * 92
            b.append(f'<rect x="{px}" y="{yy-12}" width="82" height="24" rx="12" fill="{LIGHT}" stroke="{MID}"/>')
            b.append(text(px + 41, yy + 4, 'sub-topic', 9.5, 400, GREY))
        b.append(path(f'M256,{yy} L280,{yy}', grey=True, arrow_end=False))
        b.append(path(f'M558,{yy} C580,{yy} 572,140 550,140', grey=True, arrow_end=False))
        b.append(path(f'M{282+3*92-10},{yy} L558,{yy}', grey=True, arrow_end=False))
    b.append(text(320, 294, 'Each sub-topic holds 3-5 specific ideas: pain points, how-tos, lessons, harsh truths, contrarian takes', 10, 400, GREY, style='italic'))
    b.append(text(320, 12, 'Everything on the map moves a reader from the left dot to the right dot', 10.5, 700))
    return svg(640, 304, ''.join(b))

# ---------------------------------------------------------------- F3 (essay anatomy)
def fig_essay_anatomy():
    b = []
    b.append(box(200, 6, 240, 38, '1 TOPIC IDEA', ['becomes the title'], fill=INK, tsize=12, ssize=9.5))
    xs = [0, 225, 450]
    for i, x in enumerate(xs):
        b.append(path(f'M320,45 L320,60 L{x+95},60 L{x+95},76', grey=True, arrow_end=True))
        b.append(box(x, 78, 190, 44, f'KEY POINT {i+1}', ['becomes a section headline'], tsize=11.5, ssize=9.5))
        fills = [('story or scene', 'stat or evidence', 'metaphor or example'),
                 ('quote or source', 'objection and reply', 'personal experience'),
                 ('counter-example', 'step the reader can take', 'what / how / why')][i]
        for k, f in enumerate(fills):
            yy = 134 + k * 28
            b.append(f'<rect x="{x}" y="{yy}" width="190" height="23" rx="3" fill="{LIGHT}" stroke="{MID}"/>')
            b.append(text(x + 95, yy + 15, f, 9.5, 400, GREY))
    b.append(text(320, 232, '3-5 filler ideas per key point (shown: 3)', 9.5, 400, GREY, style='italic'))
    labels = ['PROBLEM', 'INSIGHT', 'SOLUTION']
    for i, x in enumerate(xs):
        b.append(f'<rect x="{x}" y="244" width="190" height="30" rx="3" fill="{INK}"/>')
        b.append(text(x + 95, 263, labels[i], 11, 700, '#fff', ls=1.5))
        if i < 2:
            b.append(arrow(x + 192, 259, xs[i + 1] - 3, 259, grey=True))
    return svg(640, 284, ''.join(b))

# ---------------------------------------------------------------- F4 (ecosystem loop)
def fig_ecosystem():
    b = []
    b.append(box(10, 18, 150, 58, '1 IDEA', ['validated or exciting'], tsize=12, ssize=9.5))
    b.append(box(230, 18, 150, 58, '2 WEEKLY ESSAY', ['public link, product', 'mentioned once'], fill=INK, tsize=12, ssize=9.5))
    b.append(box(230, 186, 150, 58, '3 ABOUT 7 POSTS', ['each rewritten to', 'stand on its own'], tsize=12, ssize=9.5))
    b.append(box(10, 186, 150, 58, '4 LINK DAILY', ['essay link under the', "day's best post"], tsize=12, ssize=9.5))
    b.append(arrow(161, 47, 228, 47))
    b.append(arrow(305, 77, 305, 184))
    b.append(arrow(229, 215, 162, 215))
    b.append(arrow(85, 184, 85, 79))
    b.append(text(195, 128, 'LEVEL 1', 12, 700, INK, ls=2))
    b.append(text(195, 144, 'best posts become', 10, 400, GREY)); b.append(text(195, 158, 'the next ideas', 10, 400, GREY))
    # level 2
    b.append('<rect x="430" y="18" width="210" height="226" rx="4" fill="#fff" stroke="#6b6b6b" stroke-width="1.4" stroke-dasharray="5 4"/>')
    b.append(text(535, 42, 'LEVEL 2  (LATER)', 11.5, 700, INK, ls=1.5))
    for i, t in enumerate(['essay becomes a video script', 'video becomes a podcast', 'best posts become images or', 'short video', 'old essays re-promoted daily']):
        b.append(text(535, 72 + i * 24 + (6 if i >= 4 else 0), t, 10.5, 400, GREY))
    b.append(arrow(382, 47, 428, 47, dash=True, grey=True))
    b.append(text(320, 276, 'Start with one long-form home and one text platform. Add level 2 only when level 1 runs smoothly.', 10, 400, GREY, style='italic'))
    return svg(640, 288, ''.join(b))

# ---------------------------------------------------------------- F5 (ladder)
def fig_ladder():
    b = []
    rows = [
        ('1', 'Free writing: posts, notes', 'free', 'free'),
        ('2', 'Newsletter: the weekly essay', 'free', 'free'),
        ('3', 'Lead magnet', 'free', 'free + email'),
        ('4', 'Micro product', 'paid', '$10-20'),
        ('5', 'Micro service: small 1:1 pack', 'paid', 'about $500-1,000'),
        ('6', 'Cohort: group, dated, scarce', 'paid', 'higher ticket'),
        ('7', 'Standalone course', 'paid', 'cheaper, evergreen'),
        ('8', 'Community', 'later', 'recurring, last'),
    ]
    for i, (n, name, kind, price) in enumerate(rows):
        x = i * 34; y = i * 38; w = 640 - x; h = 32
        if kind == 'paid':
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{INK}"/>')
            tc, pc = '#fff', '#cfcfcf'
        elif kind == 'later':
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#fff" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="5 4"/>')
            tc, pc = INK, GREY
        else:
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{LIGHT}" stroke="{MID}"/>')
            tc, pc = INK, GREY
        b.append(text(x + 14, y + 21, n, 12, 700, tc, anchor='start'))
        b.append(text(x + 34, y + 21, name, 12, 600, tc, anchor='start'))
        b.append(text(626, y + 21, price, 10.5, 400, pc, anchor='end'))
    b.append(text(320, 322, 'More help, more money, more commitment as you move down. Fill one rung at a time.', 10, 400, GREY, style='italic'))
    return svg(640, 332, ''.join(b))

# ---------------------------------------------------------------- F6 (landing page wireframe)
def fig_landing():
    b = []
    secs = ['Eyebrow: who it is for', 'Headline: the promised outcome', 'Subheadline: how, in a line',
            'Optional top proof', 'Lead: five or six pains', 'Body: short story + mechanism',
            'Offer intro: feature > benefit', 'Proof: testimonials', 'Guarantee: risk reversal',
            'Call to action: two honest paths', 'FAQ: objections']
    heights = [26, 40, 28, 24, 44, 44, 40, 30, 28, 34, 30]
    y = 4; pos = []
    for i, (s, hh) in enumerate(zip(secs, heights)):
        fill = INK if i in (1, 9) else LIGHT
        tc = '#fff' if i in (1, 9) else INK
        b.append(f'<rect x="0" y="{y}" width="300" height="{hh}" rx="3" fill="{fill}" stroke="{MID if fill!=INK else INK}"/>')
        b.append(text(12, y + hh / 2 + 4, f'{i+1}  {s}', 10.5, 600, tc, anchor='start'))
        pos.append((y, y + hh)); y += hh + 5
    groups = [(0, 2, 'Above the fold', 'outcome, audience, how'),
              (3, 5, 'Earn the read', 'pain list, story, mechanism'),
              (6, 8, 'Show the proof', 'offer, testimonials, guarantee'),
              (9, 10, 'Decide', 'two honest paths, then FAQ')]
    for a, z, t, sub in groups:
        y0 = pos[a][0]; y1 = pos[z][1]
        b.append(f'<path d="M318,{y0} L326,{y0} L326,{y1} L318,{y1}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        b.append(text(340, (y0 + y1) / 2 - 2, t, 12, 700, INK, anchor='start'))
        b.append(text(340, (y0 + y1) / 2 + 13, sub, 10, 400, GREY, anchor='start'))
    b.append(text(340, y + 8, 'Aim for about 600-800 words. Cut the FAQ and extra', 10, 400, GREY, anchor='start', style='italic'))
    b.append(text(340, y + 22, 'buttons if your host only offers a simple page.', 10, 400, GREY, anchor='start', style='italic'))
    return svg(640, y + 30, ''.join(b))

# ---------------------------------------------------------------- F7 (launch)
def fig_launch():
    b = []
    cols = [
        ('WEEK 1  SOFT', ['Mention near top and in P.S.', 'Link the essay, not the offer,', "under the day's best post", 'Narrow topics toward the offer']),
        ('WEEK 2  HARDER', ['Name problems the offer solves', 'Plug offer + deadline under', 'the best post each day', 'Share real testimonials']),
        ('WEEK 3  CLOSE', ['Repeat; remind of the deadline', 'Last 3 days: a standalone', 'promotion post daily', 'Close: 2 emails + last call']),
    ]
    xs = [0, 218, 436]
    for i, (hd, lines) in enumerate(cols):
        x = xs[i]
        b.append(f'<rect x="{x}" y="0" width="204" height="150" rx="4" fill="#fff" stroke="{INK}" stroke-width="1.4"/>')
        b.append(f'<path d="M{x},4 Q{x},0 {x+4},0 L{x+200},0 Q{x+204},0 {x+204},4 L{x+204},30 L{x},30 z" fill="{INK}"/>')
        b.append(text(x + 102, 20, hd, 11.5, 700, '#fff', ls=1))
        for k, l in enumerate(lines):
            b.append(text(x + 14, 56 + k * 22, l, 10.2, 400, INK, anchor='start'))
        if i < 2:
            b.append(arrow(x + 206, 75, xs[i + 1] - 3, 75, grey=True))
    # sales curve
    b.append(text(0, 180, 'TYPICAL SHAPE OF SALES', 9.5, 700, GREY, anchor='start', ls=1.5))
    b.append(f'<line x1="0" y1="290" x2="640" y2="290" stroke="{MID}" stroke-width="1.4"/>')
    pts = '0,286 70,282 140,278 218,270 300,252 380,232 436,222 500,214 560,190 600,140 640,70'
    b.append(f'<polygon points="0,290 {pts} 640,290" fill="{LIGHT}"/>')
    b.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    b.append(text(100, 306, 'slow', 10, 600, GREY)); b.append(text(320, 306, 'picks up', 10, 600, GREY)); b.append(text(560, 306, 'surge in the last 2 days', 10, 600, GREY))
    b.append(f'<line x1="218" y1="196" x2="218" y2="290" stroke="{MID}" stroke-dasharray="4 4"/>')
    b.append(f'<line x1="436" y1="196" x2="436" y2="290" stroke="{MID}" stroke-dasharray="4 4"/>')
    return svg(640, 316, ''.join(b))

# ---------------------------------------------------------------- F8 (90-day timeline)
def fig_timeline():
    b = []
    labels = ['1  Foundation', '2  Idea system', '3  Free writing', '4  Newsletter', '5  Offer + ladder', '6  Courses', '7  Landing + launch']
    weeks = {1: {1}, 2: {2}, 3: {2, 3, 4}, 4: {3, 4}, 5: {4, 5}, 6: {5}, 7: {5, 6}, 8: {5, 6}, 9: {6, 7}, 10: {7}, 11: {7}, 12: {7}}
    x0 = 150; cw = (640 - x0) / 13
    top = 46; rh = 28
    for wk in range(1, 14):
        x = x0 + (wk - 1) * cw
        b.append(text(x + cw / 2, 38, str(wk), 10.5, 700, INK))
    b.append(text(x0, 20, 'WEEK', 9.5, 700, GREY, anchor='start', ls=1.5))
    for r, lab in enumerate(labels):
        y = top + r * rh
        b.append(text(0, y + 17, lab, 10.5, 600, INK, anchor='start'))
        b.append(f'<line x1="0" y1="{y+rh-3}" x2="640" y2="{y+rh-3}" stroke="{LIGHT}"/>')
        for wk in range(1, 14):
            x = x0 + (wk - 1) * cw
            if wk == 13:
                b.append(f'<rect x="{x+2:.1f}" y="{y+3}" width="{cw-4:.1f}" height="{rh-9}" rx="3" fill="{MID}"/>')
            elif (r + 1) in weeks[wk]:
                b.append(f'<rect x="{x+2:.1f}" y="{y+3}" width="{cw-4:.1f}" height="{rh-9}" rx="3" fill="{INK}"/>')
    yb = top + 7 * rh
    for wk, g in ((4, 1), (8, 2), (12, 3)):
        x = x0 + wk * cw
        b.append(f'<line x1="{x:.1f}" y1="30" x2="{x:.1f}" y2="{yb}" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="4 4"/>')
        b.append(text(x - 5, yb + 16, f'GATE {g}', 9.5, 700, INK, anchor='end'))
    b.append(text(x0 + 12.5 * cw, yb + 16, 'DEBRIEF', 9.5, 700, GREY))
    b.append(text(0, yb + 40, 'Dark bars: parts you work on that week. Dashed lines: decision gates after weeks 4, 8 and 12.', 9.5, 400, GREY, anchor='start', style='italic'))
    return svg(640, yb + 50, ''.join(b))

FIGURES = {
    'model': (fig_model, 'The whole system on one page: ideas feed short-form, short-form feeds the newsletter, the newsletter feeds the offer.'),
    'map': (fig_content_map, 'A content map: three broad territories between the life you reject and the life you want.'),
    'ecosystem': (fig_ecosystem, 'The level 1 content loop. Level 2 is added only once the loop is steady.'),
    'essay': (fig_essay_anatomy, 'Anatomy of a long-form piece: one topic, three or more key points, and filler ideas under each.'),
    'ladder': (fig_ladder, 'The ladder: free rungs build trust, paid rungs are added one at a time.'),
    'landing': (fig_landing, 'Section order for a landing page, grouped by what each stretch of the page must do.'),
    'launch': (fig_launch, 'The three-week launch pattern described in the sources, with the typical shape of sales.'),
    'timeline': (fig_timeline, 'The 13-week plan: which part you work on each week, and when to make decisions.'),
}
