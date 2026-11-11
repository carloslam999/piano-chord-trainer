"""Build the multi-song site (shared engine + one data file per song + library page)
and single-file standalone pages.   usage: build_site.py <scratchpad> <outdir>"""
import json, re, sys, os
SP, OUT = sys.argv[1], sys.argv[2]
clair = open(f'{SP}/base/clair.html').read()
noc = open(f'{SP}/base/noc.html').read()
noc_notes = json.load(open(f'{SP}/noc/notes.json'))

def grab(pat, text, flags=re.S):
    m = re.search(pat, text, flags); assert m, pat[:50]
    return m.group(1)
def sub1(pat, new, text):
    assert re.search(pat, text, flags=re.S), pat[:60]
    return re.sub(pat, lambda m: new, text, count=1, flags=re.S)
def rep(a, b, text, n=1):
    assert a in text, a[:60]
    return text.replace(a, b) if n == 0 else text.replace(a, b, n)

# ---------------- engine pieces from the Clair de Lune page ----------------
css = grab(r'<style>(.*?)</style>', clair)
body = grab(r'</style>\s*(<div class="wrap">.*?)\s*<script>', clair)
js = grab(r'<script>(.*?)</script>', clair)

css = rep('repeat(3, 1fr); font-size: 10px', 'repeat(var(--beats, 4), 1fr); font-size: 10px', css)
css = rep('.fold summary::before { content: "▸"; color: var(--muted); width: 1em; }',
          '.fold summary { align-items: center; }\n.fold summary::before { content: "▸"; color: var(--ink); font-size: 22px; line-height: 1; width: 22px; text-align: center; }', css)
css += '''
@media (max-width: 600px) {
  .nowbar { gap: 4px 12px; }
  .nowbar .now-sym { min-width: 0; font-size: 34px; }
  .nowbar .now-rom { min-width: 0; font-size: 17px; }
  .nowbar .next, .nowbar .counter .pos { min-width: 0; }
  .nowbar .repeat { margin-left: 0; }
  .ctrlbar { gap: 6px 10px; }
  .ctrlbar .speed { flex-basis: 100%; }
  .legend .kbd-hint { display: none; }
  .fold .strip-bars { grid-auto-columns: minmax(132px, 1fr); }
  .chip .s { font-size: 13px; }
  .top h1 { font-size: 30px; }
}
@media (hover: none) { .legend .kbd-hint { display: none; } }
body { margin: 0; }
.back { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: var(--muted); text-decoration: none; border: 1px solid var(--line); border-radius: 999px; padding: 4px 12px; justify-self: start; }
.back:hover { color: var(--ink); border-color: var(--chord); }
.top-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
'''

texts_c = {k: grab(p, body) for k, p in dict(eyebrow=r'<div class="eyebrow">(.*?)</div>', title=r'<h1>(.*?)</h1>', meta=r'<div class="meta">(.*?)</div>',
                                                  practice=r'<ol>(.*?)</ol>', glossary=r'<dl class="glossary">(.*?)</dl>', credits=r'<footer>(.*?)</footer>').items()}
nbody = grab(r'</style>\s*(<div class="wrap">.*?)\s*<script>', noc)
texts_n = {k: grab(p, nbody) for k, p in dict(eyebrow=r'<div class="eyebrow">(.*?)</div>', title=r'<h1>(.*?)</h1>', meta=r'<div class="meta">(.*?)</div>',
                                                   practice=r'<ol>(.*?)</ol>', glossary=r'<dl class="glossary">(.*?)</dl>', credits=r'<footer>(.*?)</footer>').items()}
texts_n['practice'] = rep('<b>Switch to the nocturne pattern.</b>', '<b>Switch the chord style to “Bass, chord, chord”.</b>', texts_n['practice'])

body = sub1(r'<div class="eyebrow">.*?</div>', '<div class="top-row"><div class="eyebrow" id="songEyebrow"></div><!--BACK--></div>', body)
body = sub1(r'<h1>.*?</h1>', '<h1 id="songTitle"></h1>', body)
body = sub1(r'<div class="meta">.*?</div>', '<div class="meta" id="songMeta"></div>', body)
body = sub1(r'<ol>.*?</ol>', '<ol id="practice"></ol>', body)
body = sub1(r'<dl class="glossary">.*?</dl>', '<dl class="glossary" id="glossary"></dl>', body)
body = sub1(r'<footer>.*?</footer>', '<footer id="credits"></footer>', body)
body = sub1(r'The strip above the piano shows the section being played; this is the whole piece\. Each card is one bar: .*?\)\.',
            'The Chords bar above the piano shows the bars being played; this is the whole piece. Each card is one bar: <span id="countText"></span>.', body)

D_c = json.loads(grab(r'const D = (\{.*?\});\nconst PICK', js))
CH_c = grab(r'const CH = (\{.*?\});\nconst tonesOf', js)
SEC_c = grab(r'const SECTIONS = (\[.*?\]);\n', js)
js = sub1(r'const D = \{.*?\};\nconst PICK[^\n]*\n', '''const SONG = window.SONG, D = SONG.data, CH = SONG.chords, SECTIONS = SONG.sections;
const PICK = D.pickup, CAD = D.cadenza, NB = D.bars.length, BEATS = D.beats, BARLEN = BEATS * 3;
const tonesOf = sym => CH[sym.split("/")[0]];
const BEATS_HTML = '<div class="beats">' + Array.from({ length: BEATS }, (_, i) => `<span>${i + 1}</span>`).join('') + '</div>';
''', js)
js = sub1(r'const CH = \{.*?\};\nconst tonesOf[^\n]*\n', '', js)
js = sub1(r'const SECTIONS = \[.*?\];\n', '', js)
js = rep("'<div class=\"beats\"><span>1</span><span>2</span><span>3</span></div>'", 'BEATS_HTML', js)
js = rep('for (let b = 0; b < 3; b++)', 'for (let b = 0; b < BEATS; b++)', js)
js = rep('const LO = 24,', 'const LO = D.lo,', js)
js = rep("stateAt(D.clefs, st, t, 'G')", 'stateAt(D.clefs, st, t, D.clef0[st])', js)
js = rep("let prev = 'G';", 'let prev = D.clef0[st];', js)
js = rep('bar: Math.floor(t / 9 + 1e-6)', 'bar: Math.floor((t - PICK) / BARLEN + 1e-6)', js)
js = rep('Math.floor(p.t / 3 + 1e-6) === Math.floor(g.t / 3 + 1e-6)', 'Math.floor((p.t - PICK) / 3 + 1e-6) === Math.floor((g.t - PICK) / 3 + 1e-6)', js)
js = rep("'cdl-' + id", "'pct-' + id", js, 0)
js = rep('const $ = id => document.getElementById(id);', '''const $ = id => document.getElementById(id);
/* ---------- fill in this song's text ---------- */
$('songEyebrow').textContent = SONG.eyebrow; $('songTitle').innerHTML = SONG.titleHtml; $('songMeta').innerHTML = SONG.metaHtml;
$('practice').innerHTML = SONG.practiceHtml; $('glossary').innerHTML = SONG.glossaryHtml; $('credits').innerHTML = SONG.creditsHtml;
$('countText').textContent = SONG.countText;
$('style').options[2].textContent = SONG.leftHand; $('style').value = SONG.defaultStyle;
$('loopFrom').max = NB; $('loopTo').max = NB;
document.documentElement.style.setProperty('--beats', BEATS);
try { localStorage.setItem('pct-last', SONG.id); } catch (e) {}''', js)
assert '/ 9' not in js and 'Debussy' not in js.replace("Debussy's left hand", ''), 'song-specific code left in engine'
body = rep('<span><kbd>Space</kbd> play or pause', '<span class="kbd-hint"><kbd>Space</kbd> play or pause', body)
body = rep("<option value=\"orig\">Debussy's left hand</option>", '<option value="orig">Original left hand</option>', body)

# ---------------- song data ----------------
r3 = lambda x: round(x * 1000) / 1000
def hands(notes):
    g = {'u': {}, 'l': {}}
    for t, d, m, st, v, ds, acc in notes: g[st].setdefault((r3(t), r3(d)), []).append(m)
    f = lambda x: [[t, d, sorted(set(ms))] for (t, d), ms in sorted(x.items())]
    return f(g['u']), f(g['l'])
VI = {'rhUp': 0, 'rhDown': 1, 'lhUp': 2, 'lhDown': 3}
def sheet(notes): return [[r3(t), r3(d), 0 if st == 'u' else 1, ds, acc, VI[v], m] for t, d, m, st, v, ds, acc in notes]
def events(ev, kind, conv): return [[t, 0 if st == 'u' else 1, conv(val)] for t, k, st, val in ev if k == kind and t > 0]

D_c.update(beats=3, lo=24, clef0=['G', 'G'])
D_n_old = json.loads(grab(r'const D = (\{.*?\});\n', noc))
rh, lh = hands(noc_notes['notes'])
D_n = dict(bars=D_n_old['bars'], rh=rh, lh=lh, end=D_n_old['end'], pickup=1, cadenza=32, beats=4, lo=33, clef0=['G', 'F'],
           sh=sheet(noc_notes['notes']), clefs=events(noc_notes['events'], 'clef', lambda v: 'G' if v == 'treble' else 'F'),
           otts=events(noc_notes['events'], 'ott', int), keys=[[0, -3]])
CH_n = grab(r'const CH = (\{.*?\n\});', noc)
SEC_n = grab(r'const SECTIONS = (\[.*?\n\]);', noc)

def first_chords(D, n=5):
    out = []
    for b in D['bars']:
        for c in b['chords']:
            if not out or out[-1] != c[0]: out.append(c[0])
            if len(out) == n: return out
    return out
SONGS = [
    dict(id='nocturne-op9-no2', file='nocturne-op9-no2.html', title='Nocturne in E♭ major, Op. 9 No. 2', short='Nocturne Op. 9 No. 2', composer='Frédéric Chopin',
         facts=['E♭ major', '12/8', '34 bars'], blurb='The famous singing melody over a rocking left hand. Four bars of chords come back four times, so it is quicker to learn than it sounds.',
         texts=texts_n, data=D_n, chords=CH_n, sections=SEC_n, leftHand="Chopin's left hand", defaultStyle='pattern',
         countText='four beats, each three eighth notes long (count “1-and-a, 2-and-a…”)',
         desc="Play-along chord trainer for Chopin's Nocturne Op. 9 No. 2."),
    dict(id='clair-de-lune', file='clair-de-lune.html', title='Clair de Lune', short='Clair de Lune', composer='Claude Debussy',
         facts=['D♭ major', '9/8', '72 bars'], blurb='Soft thirds, then the flowing middle section everyone knows: D♭, F minor, D♭ minor, bar after bar.',
         texts=texts_c, data=D_c, chords=CH_c, sections=SEC_c, leftHand="Debussy's left hand", defaultStyle='block',
         countText='three beats, each three eighth notes long (count “1-and-a, 2-and-a, 3-and-a”)',
         desc="Play-along chord trainer for Debussy's Clair de Lune."),
]
exec(open(f'{SP}/songs_extra.py').read())

def song_js(s):
    meta = dict(id=s['id'], title=s['title'], eyebrow=s['texts']['eyebrow'], titleHtml=s['texts']['title'], metaHtml=s['texts']['meta'],
                practiceHtml=s['texts']['practice'], glossaryHtml=s['texts']['glossary'], creditsHtml=s['texts']['credits'] + f' <br>Spotted a wrong chord or want another piece? <a href="{ISSUES}" target="_blank" rel="noopener">Tell me on GitHub</a>.',
                countText=s['countText'], leftHand=s['leftHand'], defaultStyle=s['defaultStyle'], data=s['data'])
    return 'window.SONG = Object.assign(' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ', { chords: ' + s['chords'] + ', sections: ' + s['sections'] + ' });\n'

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..600&family=Instrument+Sans:wght@400;500;600&family=Noto+Music&display=swap">'
SITE = 'https://carloslam999.github.io/piano-chord-trainer/'
ISSUES = 'https://github.com/carloslam999/piano-chord-trainer/issues/new'
def share_tags(title, desc, path):
    return (f'<link rel="canonical" href="{SITE}{path}">\n<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="Piano Chord Trainer">\n<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n<meta property="og:url" content="{SITE}{path}">\n'
            f'<meta property="og:image" content="{SITE}assets/preview.png">\n<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="theme-color" content="#0E0F1E">\n')
GOAT = '<script data-goatcounter="https://pianochord.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>\n'
def page_head(title, desc, path=''):
    return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>{title}</title>\n<meta name="description" content="{desc}">\n' + share_tags(title, desc, path) + f'{FONTS}\n' + GOAT

os.makedirs(f'{OUT}/site/assets', exist_ok=True); os.makedirs(f'{OUT}/site/songs', exist_ok=True)
import shutil; shutil.copy(f'{SP}/preview.png', f'{OUT}/site/assets/preview.png')
open(f'{OUT}/site/assets/trainer.css', 'w').write(css.strip() + '\n')
open(f'{OUT}/site/assets/trainer.js', 'w').write(js.strip() + '\n')
BACK = '<a class="back" href="./">← All songs</a>'
for s in SONGS:
    open(f"{OUT}/site/songs/{s['id']}.js", 'w').write(song_js(s))
    html = page_head(f"{s['short']} · Piano Chord Trainer", s['desc'] + ' Falling notes, a chord for every bar and rolling sheet music.', s['file']) + '<link rel="stylesheet" href="assets/trainer.css">\n</head>\n<body>\n' + \
        body.replace('<!--BACK-->', BACK) + f"\n<script src=\"songs/{s['id']}.js\"></script>\n<script src=\"assets/trainer.js\"></script>\n</body>\n</html>\n"
    open(f"{OUT}/site/{s['file']}", 'w').write(html)
    # single-file version (for the claude.ai artifact): everything inline, no link back to a library
    alone = f"<meta charset=\"utf-8\">\n<title>{s['short']} Chord Trainer</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n{FONTS}\n<style>\n{css.strip()}\n</style>\n\n" + \
        body.replace('<!--BACK-->', '') + '\n\n<script>\n' + song_js(s) + js.strip() + '\n</script>\n'
    if s['id'] in ('nocturne-op9-no2', 'clair-de-lune'):
        open(f"{OUT}/{'nocturne-chord-trainer' if s['id'].startswith('noc') else 'clair-de-lune-chord-trainer'}.html", 'w').write(alone)

# ---------------- library page ----------------
exec(open(f'{SP}/index_page.py').read())
print('built', [s['id'] for s in SONGS], {f: os.path.getsize(f'{OUT}/site/{f}') for f in ['index.html', 'assets/trainer.js', 'assets/trainer.css', 'songs/nocturne-op9-no2.js', 'songs/clair-de-lune.js']})
