# exec'd at the end of songs_extra.py: restyle the song pages to match the front page,
# with a light theme by default and a dark theme the viewer can switch to (remembered in localStorage).

LIGHT = '''--bg: #F5F6FB; --surface: #FFFFFF; --ink: #14151C; --muted: #5B5D70; --line: #14151C;
  --edge: #14151C; --shadow-ink: #14151C; --dot: rgba(20,21,28,.07); --hl: #FFF4CF;
  --melody: #FFC83A; --melody-soft: #FFF1C7; --chord: #2F45FF; --chord-soft: #DCE0FF; --bass: #24C49B;
  --sun: #FFC83A; --cobalt: #2F45FF; --mint: #24C49B; --coral: #FF6A50; --lilac: #B7A3FF;
  --key-white: #FBFBFD; --key-black: #14151C; --roll-bg: #14151C; --grid: rgba(255,255,255,.09);
  --roll-chord: #7F95FF; --roll-bass: #24C49B; --roll-text: rgba(255,255,255,.5);
  --sheet-rh: #2F45FF; --sheet-lh: #D9432A; --on-accent: #FFFFFF; --stage-shadow: #2F45FF;'''
DARK = '''--bg: #101119; --surface: #1B1D29; --ink: #EEEEF5; --muted: #A3A5B8; --line: #3B3F58;
  --edge: #3B3F58; --shadow-ink: #05060A; --dot: rgba(255,255,255,.05); --hl: #3A3115;
  --melody: #FFC83A; --melody-soft: #3D3214; --chord: #8C9BFF; --chord-soft: #262F5E; --bass: #24C49B;
  --key-white: #E6E6EE; --key-black: #0B0C12; --roll-bg: #0B0C12; --grid: rgba(255,255,255,.08);
  --sheet-rh: #8C9BFF; --sheet-lh: #FF8A73; --on-accent: #10111A; --stage-shadow: #2F45FF;'''
FONT = "@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&display=swap');\n"

# replace the old dark-first token blocks
a = css.index(':root {'); b = css.index(':root[data-theme="dark"] {'); b = css.index('}', b) + 1
css = FONT + css[:a] + ':root {\n  ' + LIGHT + '\n  --font-display: "Bricolage Grotesque", "Avenir Next", system-ui, sans-serif;\n  --font-ui: "Instrument Sans", system-ui, -apple-system, "Segoe UI", sans-serif;\n  --r: 12px; color-scheme: light;\n}\n:root[data-theme="dark"] {\n  ' + DARK + '\n  color-scheme: dark;\n}' + css[b:]

css += '''
/* ---------- front-page look: paper, ink outlines, sticker shadows ---------- */
body { background-color: var(--bg); background-image: radial-gradient(var(--dot) .8px, transparent .8px); background-size: 22px 22px; }
h1, h2, h3, .now-sym, .now-rom, .chip .s, .next b, .sec-tag b, .glossary dt { font-family: var(--font-display); }
h1, h2, h3 { font-weight: 800; letter-spacing: -.02em; }
.now-sym { font-weight: 700; letter-spacing: -.02em; }
.top h1 { font-size: clamp(30px, 4.6vw, 46px); }
.top h1 em { font-style: normal; color: inherit; background: linear-gradient(transparent 60%, var(--sun) 60%); padding: 0 2px; }
:root[data-theme="dark"] .top h1 em { background: linear-gradient(transparent 60%, #2F45FF 60%); }
.sitebar { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.logo { display: inline-flex; align-items: center; gap: 9px; font-family: var(--font-display); font-weight: 800; font-size: 17px; text-decoration: none; color: var(--ink); }
.logo i { display: inline-grid; grid-template-columns: repeat(3, 6px); gap: 2px; height: 24px; padding: 3px; border: 2px solid var(--edge); border-radius: 6px; background: var(--surface); }
.logo i b { background: var(--ink); height: 60%; border-radius: 0 0 2px 2px; } .logo i b:nth-child(2) { background: var(--cobalt); height: 100%; border-radius: 2px; }
.sitebar-r { display: flex; gap: 8px; align-items: center; }
.back, .themebtn { font: inherit; font-size: 13px; font-weight: 700; color: var(--ink); background: var(--surface); border: 2px solid var(--edge); border-radius: 999px; padding: 4px 12px; box-shadow: 2px 2px 0 var(--shadow-ink); text-decoration: none; cursor: pointer; }
.themebtn { padding: 4px 10px; }
.back, .themebtn { white-space: nowrap; }
@media (max-width: 600px) { .logo { font-size: 15px; } .back, .themebtn { padding: 4px 9px; font-size: 12px; } .sitebar-r { gap: 6px; } }
.back:hover, .themebtn:hover { transform: translate(-1px, -1px); box-shadow: 3px 3px 0 var(--shadow-ink); }
.badges { display: flex; flex-wrap: wrap; gap: 6px; }
.badges span { font-size: 12px; font-weight: 700; border: 1.5px solid var(--edge); border-radius: 999px; padding: 1px 10px; background: var(--surface); color: var(--ink); }
.badges .lvl, .badges .mood { color: #14151C; border-color: #14151C; }
.badges .mood { background: var(--lilac); }
.card { border: 2px solid var(--edge); border-radius: 14px; box-shadow: 3px 3px 0 var(--shadow-ink); }
.piano { border: 2px solid var(--edge); border-radius: 16px; box-shadow: 5px 5px 0 var(--stage-shadow); background: var(--surface); }
.fold { border-bottom: 2px solid var(--edge); }
.legend { border-top: 2px solid var(--edge); }
.btn { border: 2px solid var(--edge); border-radius: 10px; background: var(--surface); color: var(--ink); font-weight: 700; box-shadow: 2px 2px 0 var(--shadow-ink); transition: transform .1s, box-shadow .1s; }
.btn:hover { border-color: var(--edge); transform: translate(-1px, -1px); box-shadow: 3px 3px 0 var(--shadow-ink); }
.btn:active { transform: translate(1px, 1px); box-shadow: 1px 1px 0 var(--shadow-ink); }
.btn.primary { background: var(--cobalt); color: #fff; border-color: var(--edge); }
.ctrlbar { border-top: 2px dashed var(--line); }
.ctrlbar select, .field select, .field input[type=number] { border: 1.5px solid var(--edge); border-radius: 999px; background: var(--surface); color: var(--ink); font-weight: 600; }
.tone { border: 1.5px solid var(--edge); background: var(--surface); }
.tone.root { background: var(--chord); color: var(--on-accent); }
.bar { border: 2px solid var(--edge); border-radius: 10px; box-shadow: 2px 2px 0 var(--shadow-ink); }
.bar.cur { border-color: var(--edge); background: var(--hl); box-shadow: 3px 3px 0 var(--sun); }
.fold .bar { background: var(--bg); }
.fold .bar.cur { background: var(--hl); }
.chip { border: 1.5px solid var(--edge); background: var(--chord-soft); }
.chip.cur { background: var(--chord); color: var(--on-accent); }
.meter .beat { background: var(--bg); border: 1.5px solid var(--line); }
.meter i.on { background: var(--sun); }
.section-head h3 { display: inline-grid; place-items: center; min-width: 2em; padding: 0 10px; height: 34px; font-size: 18px; background: var(--sun); color: #14151C; border: 2px solid #14151C; border-radius: 999px; }
footer a, .glossary a { color: var(--chord); }
kbd { border-color: var(--edge); }
@media (prefers-reduced-motion: reduce) { .btn, .back, .themebtn { transition: none; } }
'''

body = body.replace('<div class="top-row"><div class="eyebrow" id="songEyebrow"></div><!--BACK--></div>',
    '<div class="eyebrow" id="songEyebrow"></div>', 1)
assert '<header class="top">' in body
body = body.replace('<header class="top">',
    '<nav class="sitebar"><a class="logo" href="./"><i aria-hidden="true"><b></b><b></b><b></b></i>Piano Chord Trainer</a>'
    '<span class="sitebar-r"><button class="themebtn" id="themeBtn" type="button" aria-label="Switch to dark mode">☾ Dark</button><!--BACK--></span></nav>\n  <header class="top">', 1)
assert '<div class="meta" id="songMeta"></div>' in body
body = body.replace('<div class="meta" id="songMeta"></div>', '<div class="meta" id="songMeta"></div>\n    <div class="badges" id="songBadges"></div>', 1)
body = body.replace('style="background:var(--chord)"', 'style="background:var(--roll-chord)"')
body = "<script>try{if(localStorage.getItem('pct-theme')==='dark')document.documentElement.dataset.theme='dark'}catch(e){}</script>\n" + body

for a_, b_ in [
    ("for (const k of ['melody','melody-soft','chord','chord-soft','bass','key-white','key-black','roll-bg','grid','line',",
     "for (const k of ['roll-chord','roll-bass','roll-text','sheet-rh','sheet-lh','coral','melody','melody-soft','chord','chord-soft','bass','key-white','key-black','roll-bg','grid','line',"),
    ("if (e === 0) { ctx.fillStyle = col.muted; ctx.font", "if (e === 0) { ctx.fillStyle = col['roll-text']; ctx.font"),
    ("const c = e.bus === 'mel' ? col.melody : e.bass ? col.bass : col.chord;", "const c = e.bus === 'mel' ? col.melody : e.bass ? col['roll-bass'] : col['roll-chord'];"),
    ("c.font = 'italic 12px ' + getComputedStyle(document.body).fontFamily; c.fillStyle = col.melody;", "c.font = 'italic 12px ' + getComputedStyle(document.body).fontFamily; c.fillStyle = col.coral;"),
    ("const ink = on ? (g.st ? col.chord : col.melody) : col.ink;", "const ink = on ? (g.st ? col['sheet-lh'] : col['sheet-rh']) : col.ink;"),
    ("c.fillStyle = on ? (st ? col.chord : col.melody) : col.ink;", "c.fillStyle = on ? (st ? col['sheet-lh'] : col['sheet-rh']) : col.ink;"),
    ("$('countText').textContent = SONG.countText;", """$('countText').textContent = SONG.countText;
{ const L = D.lib || {}, LV = { 1: ['Beginner', '#24C49B'], 2: ['Intermediate', '#FFC83A'], 3: ['Advanced', '#FF6A50'] }[L.difficulty];
  if (LV) $('songBadges').innerHTML = `<span class="lvl" style="background:${LV[1]}">${LV[0]}</span><span class="mood">${L.mood}</span><span>${L.era}</span><span>~${L.minutes} min</span>`; }
{ const btn = $('themeBtn'), sync = () => { const dark = document.documentElement.dataset.theme === 'dark'; btn.textContent = dark ? '☀ Light' : '☾ Dark'; btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode'); };
  btn.onclick = () => { const dark = document.documentElement.dataset.theme !== 'dark'; if (dark) document.documentElement.dataset.theme = 'dark'; else delete document.documentElement.dataset.theme;
    try { localStorage.setItem('pct-theme', dark ? 'dark' : 'light'); } catch (e) {} sync(); };
  sync(); }"""),
]:
    assert a_ in js, ('theme patch not found', a_[:60])
    js = js.replace(a_, b_, 1)
for s in SONGS:
    s['data']['lib'] = s['lib']
