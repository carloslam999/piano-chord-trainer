# exec'd by build_site.py: writes the library (front) page.
LEVELS = {1: 'Beginner', 2: 'Intermediate', 3: 'Advanced'}
COMPOSER_SHORT = lambda c: c.split()[-1]
cards = []
for s in SONGS:
    L = s['lib']
    cards.append(dict(id=s['id'], file=s['file'], title=s['title'], composer=s['composer'], short=COMPOSER_SHORT(s['composer']),
                      key=s['facts'][0], time=s['facts'][1], bars=s['facts'][2], blurb=s['blurb'], chords=first_chords(s['data'], 4),
                      level=L['difficulty'], era=L['era'], mood=L['mood'], minutes=L['minutes']))
cards.sort(key=lambda c: (c['level'], c['minutes']))
composers = sorted({c['short'] for c in cards}, key=lambda x: [c['short'] for c in cards].index(x))
moods = ['Calm', 'Dreamy', 'Melancholy', 'Playful']

index = page_head('Piano Chord Trainer', 'Learn famous classical piano pieces from their chords: falling notes, a chord for every bar and rolling sheet music. Free.') + '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&display=swap">
<script>try{if(localStorage.getItem('pct-theme')==='dark')document.documentElement.dataset.theme='dark'}catch(e){}</script>
<style>
/* Layout: a bright practice-room poster. Hero with a playable keyboard, a sticky filter bar, then a grid of piece cards. */
:root {
  color-scheme: light;
  --paper: #F5F6FB; --card: #FFFFFF; --ink: #14151C; --muted: #5B5D70; --line: #14151C;
  --cobalt: #2F45FF; --sun: #FFC83A; --coral: #FF6A50; --mint: #24C49B; --lilac: #B7A3FF;
  --lvl1: var(--mint); --lvl2: var(--sun); --lvl3: var(--coral);
  --font-display: "Bricolage Grotesque", "Avenir Next", system-ui, sans-serif;
  --font-ui: "Instrument Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --edge: #14151C; --shadow-ink: #14151C; --hl-mark: var(--sun); --on-ink: #FFFFFF;
  --shadow: 4px 4px 0 var(--shadow-ink);
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --paper: #101119; --card: #1B1D29; --ink: #EEEEF5; --muted: #A3A5B8; --line: #3B3F58;
  --edge: #3B3F58; --shadow-ink: #05060A; --hl-mark: #2F45FF; --on-ink: #101119;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--font-ui); font-size: 15px; line-height: 1.5; }
body::before { content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: radial-gradient(var(--ink) 0.8px, transparent 0.8px); background-size: 22px 22px; opacity: .06; }
.wrap { position: relative; z-index: 1; max-width: 1180px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
h1, h2, h3 { font-family: var(--font-display); margin: 0; text-wrap: balance; }
:focus-visible { outline: 3px solid var(--cobalt); outline-offset: 2px; }
a { color: inherit; }

/* top bar */
.bar { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding-block: 18px; }
.logo { display: flex; align-items: center; gap: 10px; font-family: var(--font-display); font-weight: 800; font-size: 19px; text-decoration: none; letter-spacing: -.01em; }
.logo i { display: inline-grid; grid-template-columns: repeat(3, 7px); gap: 2px; height: 26px; padding: 3px; border: 2px solid var(--edge); border-radius: 6px; background: var(--card); }
.logo i b { background: var(--ink); border-radius: 0 0 2px 2px; height: 60%; } .logo i b:nth-child(2) { background: var(--cobalt); height: 100%; border-radius: 2px; }
.bar nav { display: flex; gap: 6px; flex-wrap: wrap; }
.pill-link { font-size: 14px; font-weight: 600; text-decoration: none; padding: 6px 12px; border-radius: 999px; border: 2px solid transparent; }
.pill-link:hover { border-color: var(--edge); }
.themebtn { font: inherit; font-size: 13px; font-weight: 700; color: var(--ink); background: var(--card); border: 2px solid var(--edge); border-radius: 999px; padding: 4px 11px; box-shadow: 2px 2px 0 var(--shadow-ink); cursor: pointer; }
@media (max-width: 640px) { .bar nav .pill-link { display: none; } .stage canvas { height: 260px; } }

/* hero */
.hero { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: 36px; align-items: center; padding-block: 18px 44px; }
@media (max-width: 880px) { .hero { grid-template-columns: minmax(0, 1fr); gap: 24px; } }
.kicker { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; background: var(--card); border: 2px solid var(--edge); border-radius: 999px; padding: 4px 12px 4px 6px; box-shadow: 2px 2px 0 var(--shadow-ink); }
.kicker span { color: #14151C; background: var(--sun); border-radius: 999px; padding: 1px 8px; font-size: 12px; }
.hero h1 { font-size: clamp(42px, 7.2vw, 84px); line-height: .95; letter-spacing: -.035em; font-weight: 800; margin-top: 18px; }
.hero h1 .hl { position: relative; white-space: nowrap; }
.hero h1 .hl::after { content: ""; position: absolute; left: -4px; right: -6px; bottom: .06em; height: .32em; background: var(--hl-mark); z-index: -1; border-radius: 4px; transform: rotate(-1.2deg); }
.hero h1 .hl { z-index: 0; isolation: isolate; }
.hero p { font-size: 18px; color: var(--muted); max-width: 46ch; margin: 18px 0 0; }
.ctas { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 26px; }
.btn { font: inherit; font-weight: 700; font-size: 15px; cursor: pointer; border: 2px solid var(--edge); border-radius: 12px; padding: 11px 18px; background: var(--card); color: var(--ink); box-shadow: var(--shadow); text-decoration: none; transition: transform .12s, box-shadow .12s; }
.btn:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--shadow-ink); }
.btn:active { transform: translate(2px, 2px); box-shadow: 2px 2px 0 var(--shadow-ink); }
.btn.primary { background: var(--cobalt); color: #fff; }
.stats { display: flex; gap: 22px; flex-wrap: wrap; margin-top: 26px; font-size: 14px; color: var(--muted); }
.stats b { display: block; font-family: var(--font-display); font-size: 28px; color: var(--ink); line-height: 1; font-variant-numeric: tabular-nums; }

.stage { background: var(--ink); border: 2px solid var(--edge); border-radius: 18px; box-shadow: 8px 8px 0 var(--cobalt); overflow: hidden; position: relative; }
.stage canvas { display: block; width: 100%; height: 330px; touch-action: manipulation; cursor: pointer; }
.stage .now { position: absolute; left: 14px; top: 12px; display: flex; gap: 8px; align-items: center; color: #fff; font-size: 13px; }
.stage .now b { font-family: var(--font-display); font-size: 22px; }
.stage .hear { position: absolute; right: 12px; top: 10px; font: inherit; font-size: 13px; font-weight: 700; border: 2px solid #fff; color: #fff; background: transparent; border-radius: 999px; padding: 5px 12px; cursor: pointer; }
.stage .hear[aria-pressed="true"] { background: var(--sun); color: var(--ink); border-color: var(--sun); }
.stage .hint { position: absolute; left: 0; right: 0; bottom: 8px; text-align: center; color: #fff; opacity: .55; font-size: 12px; pointer-events: none; }

/* filters */
.filters { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: color-mix(in srgb, var(--paper) 92%, transparent); backdrop-filter: blur(8px); border-block: 2px solid var(--edge); padding-block: 12px; margin-bottom: 26px; }
.frow { display: flex; align-items: center; gap: 8px 14px; flex-wrap: wrap; }
.frow + .frow { margin-top: 10px; }
.flabel { font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); min-width: 74px; }
.chips { display: flex; gap: 6px; flex-wrap: wrap; }
.chip { font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; border: 2px solid var(--edge); border-radius: 999px; padding: 4px 12px; background: var(--card); color: var(--ink); display: inline-flex; align-items: center; gap: 6px; }
.chip:hover { background: color-mix(in srgb, var(--sun) 35%, var(--card)); }
.chip[aria-pressed="true"] { background: var(--ink); color: var(--on-ink); border-color: var(--ink); }
.chip .dot { width: 10px; height: 10px; border-radius: 50%; border: 1.5px solid var(--edge); }
.chip .n { font-size: 12px; opacity: .6; font-variant-numeric: tabular-nums; }
.search { font: inherit; border: 2px solid var(--edge); border-radius: 999px; padding: 6px 14px; background: var(--card); min-width: 0; width: min(100%, 240px); }
.sort { font: inherit; font-weight: 600; border: 2px solid var(--edge); border-radius: 999px; padding: 5px 10px; background: var(--card); }
.fmeta { margin-left: auto; display: flex; gap: 10px; align-items: center; font-size: 14px; color: var(--muted); }
.reset { font: inherit; font-size: 14px; background: none; border: 0; text-decoration: underline; cursor: pointer; color: var(--ink); }
@media (max-width: 700px) { .flabel { min-width: 0; width: 100%; } .fmeta { margin-left: 0; } .chips { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 2px; } .search { width: 100%; } }

/* cards */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 22px; padding-bottom: 20px; }
.card { position: relative; display: grid; grid-template-rows: auto 1fr; background: var(--card); border: 2px solid var(--edge); border-radius: 16px; box-shadow: var(--shadow); text-decoration: none; color: inherit; overflow: hidden; transition: transform .14s, box-shadow .14s; min-width: 0; }
.card:hover { transform: translate(-3px, -3px); box-shadow: 7px 7px 0 var(--shadow-ink); }
.band { display: flex; justify-content: space-between; align-items: center; padding: 8px 14px; border-bottom: 2px solid var(--edge); font-size: 13px; font-weight: 700; color: #14151C; }
.band .meter { display: inline-flex; gap: 3px; } .band .meter i { width: 14px; height: 8px; border: 1.5px solid #14151C; border-radius: 2px; background: #fff; } .band .meter i.on { background: #14151C; }
.body { padding: 16px; display: grid; gap: 10px; align-content: start; }
.who { display: flex; align-items: center; gap: 10px; }
.mono { width: 38px; height: 38px; border-radius: 50%; border: 2px solid var(--edge); display: grid; place-items: center; font-family: var(--font-display); font-weight: 800; font-size: 15px; flex: none; color: #14151C; }
.who small { display: block; color: var(--muted); font-size: 12px; }
.who strong { font-size: 14px; }
.card h3 { font-size: 25px; line-height: 1.05; letter-spacing: -.02em; font-weight: 750; }
.facts { display: flex; flex-wrap: wrap; gap: 6px; }
.facts span { font-size: 12px; font-weight: 600; border: 1.5px solid var(--edge); border-radius: 6px; padding: 1px 7px; }
.facts .mood { background: var(--lilac); color: #14151C; }
.card p { margin: 0; color: var(--muted); font-size: 14px; }
.opens { display: flex; flex-wrap: wrap; gap: 5px; align-items: center; font-size: 12px; color: var(--muted); }
.opens b { font-family: var(--font-display); font-weight: 700; font-size: 14px; color: var(--ink); background: color-mix(in srgb, var(--cobalt) 12%, var(--card)); border-radius: 6px; padding: 2px 8px; }
.go { font-weight: 800; color: var(--cobalt); display: flex; justify-content: space-between; align-items: center; margin-top: 2px; }
.last { position: absolute; top: 44px; right: 12px; transform: rotate(4deg); background: var(--sun); color: #14151C; border: 2px solid var(--edge); border-radius: 6px; font-size: 11px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; padding: 2px 7px; }
.ask { display: grid; place-content: center; gap: 10px; text-align: center; padding: 24px; border-style: dashed; box-shadow: none; background: transparent; }
.ask:hover { box-shadow: var(--shadow); background: var(--card); }
.ask h3 { font-size: 22px; } .ask p { max-width: 30ch; margin: 0 auto; }
.empty { text-align: center; padding: 40px 0; color: var(--muted); }

/* how + footer */
.how { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 18px; padding-block: 40px; }
.how div { border-top: 2px solid var(--edge); padding-top: 14px; }
.how h3 { font-size: 21px; margin-bottom: 6px; }
.how p { margin: 0; color: var(--muted); font-size: 14px; max-width: 42ch; }
.how .n { display: inline-grid; place-items: center; width: 28px; height: 28px; border-radius: 50%; background: var(--sun); color: #14151C; border: 2px solid var(--edge); font-weight: 800; font-size: 13px; margin-bottom: 8px; }
footer { border-top: 2px solid var(--edge); padding-block: 22px 40px; font-size: 13px; color: var(--muted); display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
footer a { color: var(--cobalt); font-weight: 600; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } .btn, .card { transition: none; } }
</style>
</head>
<body>
<div class="wrap">
  <header class="bar">
    <a class="logo" href="./"><i aria-hidden="true"><b></b><b></b><b></b></i>Piano Chord Trainer</a>
    <nav><button class="themebtn" id="themeBtn" type="button" aria-label="Switch to dark mode">☾ Dark</button><a class="pill-link" href="#pieces">Pieces</a><a class="pill-link" href="#how">How it works</a><a class="pill-link" href="''' + ISSUES + '''" target="_blank" rel="noopener">Request a piece</a></nav>
  </header>

  <section class="hero">
    <div>
      <span class="kicker"><span>Free</span> No sheet music reading needed</span>
      <h1>Play the classics <span class="hl">from the chords.</span></h1>
      <p>Pick a famous piece, watch the notes fall onto the keys, and follow the chord for every bar. Slow it down, loop the hard part, and play along.</p>
      <div class="ctas">
        <a class="btn primary" href="#pieces" id="startEasy">Start with an easy one</a>
        <button class="btn" type="button" id="surprise">Surprise me 🎲</button>
      </div>
      <div class="stats" id="stats"></div>
    </div>
    <div class="stage" aria-label="Try the keyboard">
      <canvas id="demo"></canvas>
      <div class="now" aria-hidden="true">Für Elise <b id="demoChord">Am</b></div>
      <button class="hear" id="hear" type="button" aria-pressed="false">♪ Sound on</button>
      <div class="hint">Tap the keys to play</div>
    </div>
  </section>
</div>

<div class="filters" id="pieces">
  <div class="wrap">
    <div class="frow">
      <span class="flabel">Level</span>
      <div class="chips" id="fLevel"></div>
      <div class="fmeta"><span id="count"></span><button class="reset" id="reset" type="button" hidden>Clear filters</button></div>
    </div>
    <div class="frow">
      <span class="flabel">Composer</span>
      <div class="chips" id="fComposer"></div>
    </div>
    <div class="frow">
      <span class="flabel">Mood</span>
      <div class="chips" id="fMood"></div>
      <input class="search" id="q" type="search" placeholder="Search pieces" aria-label="Search pieces">
      <select class="sort" id="sort" aria-label="Sort pieces">
        <option value="level">Easiest first</option>
        <option value="short">Shortest first</option>
        <option value="az">A to Z</option>
        <option value="composer">By composer</option>
      </select>
    </div>
  </div>
</div>

<div class="wrap">
  <div class="grid" id="grid"></div>
  <p class="empty" id="empty" hidden>No piece matches those filters. <button class="reset" type="button" onclick="resetAll()">Clear filters</button></p>

  <section class="how" id="how" aria-label="How it works">
    <div><span class="n">1</span><h3>Pick a piece</h3><p>Filter by level, composer or mood. Every piece is public domain, so it is free to play and share.</p></div>
    <div><span class="n">2</span><h3>Learn the chords</h3><p>A chord bar follows the music, and a full map of the piece lets you loop any section at any speed.</p></div>
    <div><span class="n">3</span><h3>Add the melody</h3><p>Gold notes fall onto the keys you play. Turn on the rolling sheet music when you are ready to read along.</p></div>
  </section>

  <footer>
    <span>Scores from public-domain editions typeset by the Mutopia Project. Each piece credits its sources. Sound is a synthesised piano in your browser.</span>
    <span>Want another piece? <a href="''' + ISSUES + '''" target="_blank" rel="noopener">Suggest it on GitHub</a></span>
  </footer>
</div>

<script>
const SONGS = ''' + json.dumps(cards, ensure_ascii=False) + ''';
const LEVELS = ''' + json.dumps(LEVELS) + ''', COMPOSERS = ''' + json.dumps(composers, ensure_ascii=False) + ''', MOODS = ''' + json.dumps(moods) + ''';
const LVL_COL = { 1: 'var(--lvl1)', 2: 'var(--lvl2)', 3: 'var(--lvl3)' };
const MONO_COL = ['#FFC83A', '#24C49B', '#B7A3FF', '#FF6A50', '#7FD3FF', '#FF9DC8', '#C6F06B', '#FFB36B'];
const $ = id => document.getElementById(id);
let last = null; try { last = localStorage.getItem('pct-last'); } catch (e) {}
const state = { level: 0, composer: '', mood: '', q: '', sort: 'level' };

/* ---------- stats ---------- */
$('stats').innerHTML = `<div><b>${SONGS.length}</b>pieces</div><div><b>${COMPOSERS.length}</b>composers</div><div><b>${SONGS.filter(s => s.level === 1).length}</b>for beginners</div>`;

/* ---------- filter chips ---------- */
function chip(label, pressed, onClick, extra = '') {
  const b = document.createElement('button'); b.type = 'button'; b.className = 'chip';
  b.setAttribute('aria-pressed', pressed); b.innerHTML = extra + label; b.onclick = onClick; return b;
}
function drawFilters() {
  const lv = $('fLevel'); lv.innerHTML = '';
  lv.append(chip('All', state.level === 0, () => { state.level = 0; update(); }));
  for (const k of [1, 2, 3]) {
    const n = SONGS.filter(s => s.level === k).length;
    lv.append(chip(`${LEVELS[k]} <span class="n">${n}</span>`, state.level === k, () => { state.level = state.level === k ? 0 : k; update(); }, `<span class="dot" style="background:${LVL_COL[k]}"></span>`));
  }
  const co = $('fComposer'); co.innerHTML = '';
  co.append(chip('All', !state.composer, () => { state.composer = ''; update(); }));
  for (const c of COMPOSERS) co.append(chip(c, state.composer === c, () => { state.composer = state.composer === c ? '' : c; update(); }));
  const mo = $('fMood'); mo.innerHTML = '';
  mo.append(chip('Any', !state.mood, () => { state.mood = ''; update(); }));
  for (const m of MOODS) mo.append(chip(m, state.mood === m, () => { state.mood = state.mood === m ? '' : m; update(); }));
}
function initials(name) { const p = name.split(' '); return (p[0][0] + p[p.length - 1][0]).toUpperCase(); }
function monoColor(c) { return MONO_COL[COMPOSERS.indexOf(c.split(' ').pop()) % MONO_COL.length]; }
function minutes(m) { return m < 1 ? '<1 min' : `~${m % 1 ? m.toFixed(1) : m} min`; }
function cardHtml(s) {
  return `<a class="card" href="${s.file}">
    <div class="band" style="background:${LVL_COL[s.level]}"><span>${LEVELS[s.level]}</span><span class="meter" aria-hidden="true">${[1, 2, 3].map(i => `<i class="${i <= s.level ? 'on' : ''}"></i>`).join('')}</span></div>
    ${s.id === last ? '<span class="last">Last played</span>' : ''}
    <div class="body">
      <div class="who"><span class="mono" style="background:${monoColor(s.composer)}">${initials(s.composer)}</span><div><strong>${s.composer}</strong><small>${s.era}</small></div></div>
      <h3>${s.title}</h3>
      <div class="facts"><span>${s.key}</span><span>${s.time}</span><span>${minutes(s.minutes)}</span><span class="mood">${s.mood}</span></div>
      <p>${s.blurb}</p>
      <div class="opens">Opens with ${s.chords.map(c => `<b>${c}</b>`).join('')}</div>
      <div class="go">Practise <span aria-hidden="true">→</span></div>
    </div></a>`;
}
function update() {
  state.q = $('q').value.trim().toLowerCase(); state.sort = $('sort').value;
  let list = SONGS.filter(s => (!state.level || s.level === state.level) && (!state.composer || s.short === state.composer) && (!state.mood || s.mood === state.mood)
    && (!state.q || (s.title + ' ' + s.composer + ' ' + s.key + ' ' + s.mood + ' ' + s.era).toLowerCase().includes(state.q)));
  const by = { level: (a, b) => a.level - b.level || a.minutes - b.minutes, short: (a, b) => a.minutes - b.minutes, az: (a, b) => a.title.localeCompare(b.title), composer: (a, b) => a.short.localeCompare(b.short) || a.level - b.level }[state.sort];
  list = list.slice().sort(by);
  $('grid').innerHTML = list.map(cardHtml).join('') + (list.length ? `<a class="card ask" href="''' + ISSUES + '''" target="_blank" rel="noopener"><h3>Missing a piece?</h3><p>Tell us which public-domain piece you want to learn next.</p><span class="go" style="justify-content:center">Suggest one →</span></a>` : '');
  $('empty').hidden = list.length > 0;
  const filtered = state.level || state.composer || state.mood || state.q;
  $('count').textContent = filtered ? `${list.length} of ${SONGS.length} pieces` : `${SONGS.length} pieces`;
  $('reset').hidden = !filtered;
  drawFilters();
}
function resetAll() { Object.assign(state, { level: 0, composer: '', mood: '' }); $('q').value = ''; update(); }
$('reset').onclick = resetAll; $('q').oninput = update; $('sort').onchange = update;
$('startEasy').onclick = () => { state.level = 1; update(); };
$('surprise').onclick = () => { const s = SONGS[Math.floor(Math.random() * SONGS.length)]; location.href = s.file; };
update();
{ const btn = $('themeBtn'), sync = () => { const dark = document.documentElement.dataset.theme === 'dark'; btn.textContent = dark ? '☀ Light' : '☾ Dark'; btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode'); };
  btn.onclick = () => { const dark = document.documentElement.dataset.theme !== 'dark'; if (dark) document.documentElement.dataset.theme = 'dark'; else delete document.documentElement.dataset.theme;
    try { localStorage.setItem('pct-theme', dark ? 'dark' : 'light'); } catch (e) {} sync(); };
  sync(); }

/* ---------- hero: falling notes onto a playable keyboard ---------- */
const cv = $('demo'), LO = 52, HI = 81;   // E3..A5
const isBlack = m => [1, 3, 6, 8, 10].includes(m % 12);
// Für Elise, opening: [time in eighths, length, midi, hand]  (a = right hand, b = left hand)
const PH = [[0,.5,76,'a'],[.5,.5,75,'a'],[1,.5,76,'a'],[1.5,.5,75,'a'],[2,.5,76,'a'],[2.5,.5,71,'a'],[3,.5,74,'a'],[3.5,.5,72,'a'],[4,1.5,69,'a'],[4,.5,45,'b'],[4.5,.5,52,'b'],[5,.5,57,'b'],
  [5.5,.5,60,'a'],[6,.5,64,'a'],[6.5,.5,69,'a'],[7,1.5,71,'a'],[7,.5,52,'b'],[7.5,.5,56,'b'],[8,.5,59,'b'],[8.5,.5,64,'a'],[9,.5,68,'a'],[9.5,.5,71,'a'],[10,1.5,72,'a'],[10,.5,45,'b'],[10.5,.5,52,'b'],[11,.5,57,'b'],[11.5,.5,64,'a']];
const CH_AT = [[0, 'E'], [4, 'Am'], [7, 'E'], [10, 'Am']];
const LOOP = 12, SPE = 0.27;
let ac = null, soundOn = false, flash = {}, nextIdx = 0, loopStart = performance.now();
function audio() { if (!ac) ac = new (window.AudioContext || window.webkitAudioContext)(); if (ac.state === 'suspended') ac.resume(); return ac; }
function tone(m, dur = 0.6, vel = 0.18) {
  const a = audio(), t = a.currentTime, f = 440 * Math.pow(2, (m - 69) / 12);
  const o = a.createOscillator(), o2 = a.createOscillator(), g = a.createGain(), lp = a.createBiquadFilter();
  o.type = 'triangle'; o2.type = 'sine'; o.frequency.value = f; o2.frequency.value = f * 2; lp.type = 'lowpass'; lp.frequency.value = Math.min(f * 5, 5000);
  const g2 = a.createGain(); g2.gain.value = .25; o.connect(lp); o2.connect(g2); g2.connect(lp); lp.connect(g); g.connect(a.destination);
  g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vel, t + .01); g.gain.setTargetAtTime(0, t + .02, Math.max(.25, dur));
  o.start(t); o2.start(t); o.stop(t + dur * 4); o2.stop(t + dur * 4);
}
$('hear').onclick = () => { soundOn = !soundOn; $('hear').setAttribute('aria-pressed', soundOn); $('hear').textContent = soundOn ? '♪ Sound on ✓' : '♪ Sound on'; if (soundOn) audio(); };
let geo;
function layoutDemo() {
  const r = cv.getBoundingClientRect(), dpr = devicePixelRatio || 1;
  cv.width = r.width * dpr; cv.height = r.height * dpr; cv.getContext('2d').setTransform(dpr, 0, 0, dpr, 0, 0);
  const whites = []; for (let m = LO; m <= HI; m++) if (!isBlack(m)) whites.push(m);
  const ww = r.width / whites.length, x = {};
  whites.forEach((m, i) => x[m] = { x: i * ww, w: ww, b: false });
  for (let m = LO; m <= HI; m++) if (isBlack(m)) x[m] = { x: x[m - 1].x + ww * .66, w: ww * .62, b: true };
  geo = { W: r.width, H: r.height, KH: Math.min(110, r.height * .34), x };
}
function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect ? c.roundRect(x, y, w, h, r) : c.rect(x, y, w, h); }
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
function frame(now) {
  const { W, H, KH, x } = geo, c = cv.getContext('2d'), roll = H - KH, ppe = roll / 8;
  let p = ((now - loopStart) / 1000) / SPE;
  if (reduce) p = 4.2;
  if (p >= LOOP) { loopStart = now; p = 0; nextIdx = 0; }
  // sound + flashes for notes that just landed
  while (nextIdx < PH.length && PH[nextIdx][0] <= p) {
    const [t, d, m, h] = PH[nextIdx++];
    flash[m] = { until: now + d * SPE * 1000, col: h === 'a' ? '#FFC83A' : '#7F95FF' };
    if (soundOn && !reduce) tone(m < LO ? m + 12 : m, d * SPE, h === 'a' ? .16 : .1);
  }
  let ch = 'Am'; for (const [t, n] of CH_AT) if (t <= p) ch = n; $('demoChord').textContent = ch;
  c.fillStyle = '#14151C'; c.fillRect(0, 0, W, H);
  c.strokeStyle = 'rgba(255,255,255,.07)'; c.lineWidth = 1;
  for (let k = 0; k < 9; k++) { const y = roll - ((Math.ceil(p) + k - p) * ppe); c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); }
  for (let rep = 0; rep < 2; rep++) for (const [t, d, m, h] of PH) {
    const tt = t + rep * LOOP, mm = m < LO ? m + 12 : m, g = x[mm]; if (!g) continue;
    const y1 = roll - (tt - p) * ppe, y0 = roll - (tt + d - p) * ppe;
    if (y1 < 0 || y0 > roll) continue;
    c.fillStyle = h === 'a' ? '#FFC83A' : '#7F95FF';
    rr(c, g.x + 2, Math.max(y0, -10), g.w - 4, Math.min(y1, roll) - Math.max(y0, -10) - 2, 5); c.fill();
  }
  c.fillStyle = '#FFC83A'; c.fillRect(0, roll - 3, W, 3);
  for (let pass = 0; pass < 2; pass++) for (let m = LO; m <= HI; m++) {
    const g = x[m]; if (g.b !== !!pass) continue;
    const f = flash[m] && flash[m].until > now ? flash[m].col : null;
    c.fillStyle = f || (g.b ? '#14151C' : '#FBFBFD');
    rr(c, g.x + (g.b ? 0 : 1), roll, g.w - (g.b ? 0 : 2), (g.b ? KH * .6 : KH) - 2, 4); c.fill();
  }
  if (!reduce) requestAnimationFrame(frame);
}
cv.addEventListener('pointerdown', e => {
  const r = cv.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top, { x, H, KH } = geo;
  let hit = null;
  for (let m = LO; m <= HI; m++) { const g = x[m]; if (g.b && py > H - KH && py < H - KH * .4 && px >= g.x && px < g.x + g.w) hit = m; }
  if (hit === null) for (let m = LO; m <= HI; m++) { const g = x[m]; if (!g.b && px >= g.x && px < g.x + g.w) hit = m; }
  if (hit === null) return;
  tone(hit, .7, .2); flash[hit] = { until: performance.now() + 350, col: '#24C49B' };
  if (reduce) frame(performance.now());
});
layoutDemo(); addEventListener('resize', () => { layoutDemo(); if (reduce) frame(performance.now()); });
requestAnimationFrame(frame);
</script>
</body>
</html>
'''
open(f'{OUT}/site/index.html', 'w').write(index)
