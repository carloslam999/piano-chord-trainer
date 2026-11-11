# Add-on for build_cdl.py: sheet-music data, flatter control panel, foldable chord bar + sheet.
VI = {'rhUp': 0, 'rhDown': 1, 'lhUp': 2, 'lhDown': 3}
data['sh'] = [[r(t), r(d), 0 if st == 'u' else 1, ds, acc, VI[v], m] for t, d, m, st, v, ds, acc in notes['notes']]
data['clefs'] = [[t, 0 if st == 'u' else 1, 'G' if val == 'treble' else 'F'] for t, kind, st, val in notes['events'] if kind == 'clef']
data['otts'] = [[t, 0 if st == 'u' else 1, val] for t, kind, st, val in notes['events'] if kind == 'ott']
data['keys'] = [[0, -5], [36 * 9, 4], [42 * 9, -5]]

BOARD = '''<div class="board card">
      <div class="nowbar">
        <div class="now-sym" id="nowSym">D♭</div>
        <div class="now-rom" id="nowRom">I</div>
        <div class="tones" id="nowTones"></div>
        <div class="next" id="nextChord"></div>
        <div class="counter">
          <div class="pos" id="posText"></div>
          <div class="meter" id="meter" aria-hidden="true"></div>
        </div>
        <div class="sec-tag" id="secTag" hidden></div>
        <div class="repeat">
          <label class="field" for="loopMode">Repeat
            <select id="loopMode">
              <option value="off">Off</option>
              <option value="bar">This bar</option>
              <option value="section">This section</option>
              <option value="range">Bars from–to</option>
            </select>
          </label>
          <span class="field" id="rangeBox" hidden>
            <input type="number" id="loopFrom" min="1" max="72" value="1" aria-label="Loop from bar">to
            <input type="number" id="loopTo" min="1" max="72" value="4" aria-label="Loop to bar">
          </span>
        </div>
      </div>
      <div class="ctrlbar">
        <button class="btn primary" id="playBtn" type="button">▶ Play</button>
        <button class="btn icon" id="restartBtn" type="button" aria-label="From the top" title="From the top">⟲</button>
        <button class="btn icon" id="prevBar" type="button" aria-label="Previous bar" title="Previous bar">◀</button>
        <button class="btn icon" id="nextBar" type="button" aria-label="Next bar" title="Next bar">▶</button>
        <label class="field speed" for="tempo">Speed <b id="tempoVal">90</b>
          <input type="range" id="tempo" min="36" max="150" value="90" step="2">
        </label>
        <label class="switch"><input type="checkbox" id="melOn" checked><span class="swatch" style="background:var(--melody)"></span>Melody</label>
        <label class="switch"><input type="checkbox" id="accOn" checked><span class="swatch" style="background:var(--chord)"></span>Chords</label>
        <select id="style" aria-label="Chord style" title="Chord style">
          <option value="block" selected>Block chords</option>
          <option value="pattern">Bass, chord, chord</option>
          <option value="orig">Debussy's left hand</option>
        </select>
        <select id="melTone" aria-label="Melody sound" title="Melody sound">
          <option value="warm" selected>Warm piano</option>
          <option value="felt">Soft felt piano</option>
          <option value="bright">Bright piano</option>
        </select>
        <label class="field" for="melVol">Volume
          <input type="range" id="melVol" min="0" max="150" value="90" style="width:70px">
        </label>
      </div>
    </div>
'''
FOLDS = '''<details class="fold" id="foldChords" open>
        <summary><span class="fold-title">Chords</span><span class="sec-tag" id="stripTitle"></span><span class="fold-note" id="stripNext"></span></summary>
        <div class="strip-bars" id="stripBars"></div>
      </details>
      <details class="fold" id="foldSheet" open>
        <summary><span class="fold-title">Sheet music</span><span class="fold-note">simplified: no rests or ties</span></summary>
        <canvas id="sheet" aria-label="Scrolling sheet music"></canvas>
      </details>
'''
CSS = '''
/* flatter control panel */
.board.card { display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; padding: 8px 14px; }
.nowbar { display: flex; align-items: center; gap: 6px 18px; flex-wrap: wrap; }
.nowbar .now-sym { font-size: clamp(30px, 4.4vw, 40px); line-height: 1; min-width: 4.6em; }
.nowbar .now-rom { font-size: 20px; min-width: 2.6em; }
.nowbar .tones { min-width: 0; }
.nowbar .tone { padding: 2px 9px; font-size: 13px; }
.nowbar .meter .beat { padding: 3px 4px; }
.nowbar .next { min-width: 150px; font-size: 13px; }
.nowbar .counter { gap: 10px; }
.nowbar .counter .pos { min-width: 104px; font-size: 13px; }
.nowbar .repeat { margin-left: auto; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.ctrlbar { display: flex; align-items: center; gap: 8px 14px; flex-wrap: wrap; border-top: 1px solid var(--line); padding-top: 8px; }
.ctrlbar .btn { padding: 6px 14px; }
.ctrlbar .btn.primary { min-width: 96px; }
.ctrlbar .btn.icon { padding: 6px 11px; }
.ctrlbar select { background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 5px 8px; max-width: 150px; }
.ctrlbar .speed { flex: 1 1 150px; }
.ctrlbar .speed b { color: var(--ink); font-variant-numeric: tabular-nums; min-width: 2.2em; }
.ctrlbar .speed input { flex: 1; min-width: 80px; }
/* foldable chord bar and sheet */
.fold { border-bottom: 1px solid var(--line); }
.fold summary { cursor: pointer; padding: 7px 12px; display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap; font-size: 13px; color: var(--muted); list-style: none; user-select: none; }
.fold summary::-webkit-details-marker { display: none; }
.fold summary::before { content: "▸"; color: var(--muted); width: 1em; }
.fold[open] summary::before { content: "▾"; }
.fold-title { font-weight: 600; color: var(--ink); }
.fold-note { margin-left: auto; }
.fold .strip-bars { padding: 0 12px 10px; }
.fold .bar { background: var(--bg); padding: 5px 8px 7px; gap: 4px; }
.fold .chip { padding: 5px 2px 4px; }
#sheet { display: block; width: 100%; height: 184px; }
#roll { height: 150px; }
'''
SHEET_JS = r'''
/* ---------- sheet music (simplified engraving drawn on a canvas) ---------- */
const sheetC = $('sheet');
const SP = 7, Y_T = 48, Y_B = Y_T + 4 * SP + 46, PPE = 26, LEFT = 86;
const FLAT_ORDER = [6, 2, 5, 1, 4, 0, 3], SHARP_ORDER = [3, 0, 4, 1, 5, 2, 6];
const keyAt = t => { let k = D.keys[0][1]; for (const [kt, kv] of D.keys) if (kt <= t + 1e-6) k = kv; return k; };
const keyAcc = (step, k) => k < 0 ? (FLAT_ORDER.slice(0, -k).includes(step) ? -1 : 0) : (SHARP_ORDER.slice(0, k).includes(step) ? 1 : 0);
const stateAt = (list, st, t, init) => { let v = init; for (const [et, es, ev] of list) if (es === st && et <= t + 1e-6) v = ev; return v; };
const clefAt = (st, t) => stateAt(D.clefs, st, t, 'G'), ottAt = (st, t) => stateAt(D.otts, st, t, 0);
const ACC = { '-2': '♭♭', '-1': '♭', '0': '♮', '1': '♯', '2': '×' };
const SG = [], BEAMS = [];
{
  const map = new Map();
  for (const [t, d, st, ds, acc, v, m] of D.sh) {
    const k = t + '|' + d + '|' + st + '|' + v;
    let g = map.get(k);
    if (!g) { g = { t, d, st, v, bar: Math.floor(t / 9 + 1e-6), ns: [] }; map.set(k, g); SG.push(g); }
    g.ns.push({ ds, acc, m });
  }
  SG.sort((a, b) => a.t - b.t || a.st - b.st);
  const mem = {}, poly = {};
  for (const g of SG) {
    const clef = clefAt(g.st, g.t), ott = ottAt(g.st, g.t), k = keyAt(g.t);
    for (const n of g.ns) {
      n.pos = n.ds - 7 * ott - (clef === 'G' ? 30 : 18);
      const mk = g.bar + '|' + g.st + '|' + n.ds, cur = mk in mem ? mem[mk] : keyAcc(n.ds % 7, k);
      if (n.acc !== cur) { n.show = ACC[n.acc]; mem[mk] = n.acc; }
    }
    g.ns.sort((a, b) => a.pos - b.pos);
    g.lo = g.ns[0].pos; g.hi = g.ns[g.ns.length - 1].pos;
    (poly[g.bar + '|' + g.st] = poly[g.bar + '|' + g.st] || new Set()).add(g.v % 2);
  }
  for (const g of SG) g.up = poly[g.bar + '|' + g.st].size > 1 ? g.v % 2 === 0 : (g.lo + g.hi) / 2 < 4;
  // beams: runs of short notes in one voice, one staff, one beat
  const last = {};
  for (const g of SG) {
    if (g.d > 1.5 + 1e-6) continue;
    const key = g.v + '|' + g.st, p = last[key];
    if (p && Math.abs(p.t + p.d - g.t) < 1e-6 && Math.floor(p.t / 3 + 1e-6) === Math.floor(g.t / 3 + 1e-6)) {
      if (!p.beam) { p.beam = { gs: [p] }; BEAMS.push(p.beam); }
      g.beam = p.beam; g.beam.gs.push(g);
    }
    last[key] = g;
  }
  for (const b of BEAMS) {
    const lo = Math.min(...b.gs.map(g => g.lo)), hi = Math.max(...b.gs.map(g => g.hi));
    b.up = poly[b.gs[0].bar + '|' + b.gs[0].st].size > 1 ? b.gs[0].v % 2 === 0 : (lo + hi) / 2 < 4;
    b.gs.forEach(g => g.up = b.up);
    // beam line in "pos" units: from the first note's stem end to the last's, kept nearly flat and clear of every note
    const end = g => b.up ? g.hi + 6.5 : g.lo - 6.5;
    let a = end(b.gs[0]), z = end(b.gs[b.gs.length - 1]);
    if (Math.abs(z - a) > 2) z = a + Math.sign(z - a) * 2;
    const t0 = b.gs[0].t, t1 = b.gs[b.gs.length - 1].t;
    const at = t => a + (z - a) * (t1 > t0 ? (t - t0) / (t1 - t0) : 0);
    let push = 0;
    for (const g of b.gs) push = Math.max(push, b.up ? g.hi + 5 - at(g.t) : at(g.t) - (g.lo - 5));
    b.a = a + (b.up ? push : -push); b.z = z + (b.up ? push : -push); b.t0 = t0; b.t1 = t1;
    b.at = t => b.a + (b.z - b.a) * (t1 > t0 ? (t - t0) / (t1 - t0) : 0);
  }
}
const OTT_SPANS = [];
for (let st = 0; st < 2; st++) { let on = null; for (const [t, es, v] of D.otts) if (es === st) { if (v && on === null) on = t; else if (!v && on !== null) { OTT_SPANS.push([on, t, st]); on = null; } } if (on !== null) OTT_SPANS.push([on, D.end, st]); }
const MUSIC_FONT = '"Noto Music", "Apple Symbols", "Segoe UI Symbol", serif';
try { document.fonts.load('40px "Noto Music"', '𝄞𝄢♭♯♮'); } catch (e) {}

function drawSheet(p) {
  const r = sheetC.getBoundingClientRect(); if (!r.height || !sheetC.width) return;
  const W = r.width, H = r.height, c = sheetC.getContext('2d');
  const x0 = LEFT + Math.min(W * 0.22, 220), X = t => x0 + (t - p) * PPE;
  const bottom = st => (st ? Y_B : Y_T) + 4 * SP, Y = (st, pos) => bottom(st) - pos * SP / 2;
  const staffLines = (xa, xb) => { c.strokeStyle = col.muted; c.lineWidth = 1; c.globalAlpha = 0.55; c.beginPath(); for (const y of [Y_T, Y_B]) for (let i = 0; i < 5; i++) { c.moveTo(xa, y + i * SP + 0.5); c.lineTo(xb, y + i * SP + 0.5); } c.stroke(); c.globalAlpha = 1; };
  c.fillStyle = col.surface; c.fillRect(0, 0, W, H);
  staffLines(0, W);
  c.font = '11px ' + getComputedStyle(document.body).fontFamily; c.textAlign = 'left'; c.textBaseline = 'alphabetic';
  for (const b of D.bars) {
    const x = Math.round(X(b.start)) - 12; if (x < LEFT - 20 || x > W + 20) continue;
    c.strokeStyle = col.muted; c.lineWidth = 1; c.beginPath(); c.moveTo(x + 0.5, Y_T); c.lineTo(x + 0.5, Y_B + 4 * SP); c.stroke();
    c.fillStyle = col.muted; c.fillText(b.n, x + 4, Y_T - 7);
  }
  // key changes: say so above the staff (the signature at the left follows the playhead)
  c.font = 'italic 12px ' + getComputedStyle(document.body).fontFamily; c.fillStyle = col.melody;
  for (const [kt, kv] of D.keys) { const x = X(kt) - 8; if (kt > 0 && x > LEFT && x < W) c.fillText(`key changes: ${Math.abs(kv)} ${kv < 0 ? 'flats' : 'sharps'}`, x, Y_T - 22); }
  // 8va brackets
  for (const [a, z, st] of OTT_SPANS) {
    const xa = X(a) - 8, xb = X(z) - 16; if (xb < LEFT || xa > W) continue;
    const y = (st ? Y_B : Y_T) - 38;
    c.fillStyle = col.muted; c.font = 'italic 12px ' + getComputedStyle(document.body).fontFamily; c.fillText('8va', Math.max(xa, LEFT + 4), y + 4);
    c.strokeStyle = col.muted; c.setLineDash([4, 4]); c.beginPath(); c.moveTo(Math.max(xa, LEFT + 4) + 26, y); c.lineTo(xb, y); c.lineTo(xb, y + 7); c.stroke(); c.setLineDash([]);
  }
  // clef changes
  c.fillStyle = col.ink; c.textAlign = 'center';
  for (let st = 0; st < 2; st++) { let prev = 'G'; for (const [t, es, v] of D.clefs) if (es === st) { if (v !== prev) { const x = X(t) - 22; if (x > LEFT && x < W) drawClef(c, v, x, st, 0.72); } prev = v; } }
  const rx = SP * 0.64, ry = SP * 0.46;
  const stemEnd = g => g.beam ? g.beam.at(g.t) : (g.up ? g.hi + 6.5 : g.lo - 6.5);
  for (const g of SG) {
    const x = X(g.t); if (x > W + 30) break; if (x < LEFT - 30) continue;
    const on = g.t <= p + 1e-6 && p < g.t + g.d - 1e-6;
    const ink = on ? (g.st ? col.chord : col.melody) : col.ink;
    c.strokeStyle = ink; c.fillStyle = ink; c.lineWidth = 1.1;
    // ledger lines
    c.beginPath();
    for (let q = -2; q >= g.lo; q -= 2) { c.moveTo(x - rx - 3, Y(g.st, q) + 0.5); c.lineTo(x + rx + 3, Y(g.st, q) + 0.5); }
    for (let q = 10; q <= g.hi; q += 2) { c.moveTo(x - rx - 3, Y(g.st, q) + 0.5); c.lineTo(x + rx + 3, Y(g.st, q) + 0.5); }
    c.stroke();
    // heads, dots, accidentals
    const hollow = g.d >= 4 - 1e-6, base = Math.pow(2, Math.floor(Math.log2(g.d) + 1e-6)), dotted = Math.abs(g.d / base - 1.5) < 0.06;
    let prevPos = -99, prevShift = false;
    for (const n of g.ns) {
      const shift = n.pos - prevPos === 1 && !prevShift, hx = x + (shift ? (g.up ? 2 * rx - 1 : -2 * rx + 1) : 0), y = Y(g.st, n.pos);
      prevPos = n.pos; prevShift = shift;
      c.beginPath(); c.ellipse(hx, y, rx, ry, -0.35, 0, Math.PI * 2);
      if (hollow) { c.lineWidth = 1.5; c.stroke(); c.lineWidth = 1.1; } else c.fill();
      if (dotted) { c.beginPath(); c.arc(x + rx + 4.5 + (shift && g.up ? 2 * rx : 0), y - (n.pos % 2 === 0 ? SP / 2 : 0), 1.4, 0, Math.PI * 2); c.fill(); }
      if (n.show) { c.font = `${SP * 2.3}px ${MUSIC_FONT}`; c.textAlign = 'right'; c.textBaseline = 'middle'; c.fillText(n.show, x - rx - 2.5, y + (n.show === '♭' || n.show === '♭♭' ? -SP * 0.35 : 0)); }
    }
    // stem
    const sx = g.up ? x + rx - 0.6 : x - rx + 0.6, ye = Y(g.st, stemEnd(g));
    c.beginPath(); c.moveTo(sx, Y(g.st, g.up ? g.lo : g.hi)); c.lineTo(sx, ye); c.stroke();
    if (!g.beam && g.d <= 1.5 + 1e-6) {   // flags
      const nf = g.d <= 0.75 + 1e-6 ? 2 : 1, dir = g.up ? 1 : -1;
      c.lineWidth = 1.6; c.beginPath();
      for (let f = 0; f < nf; f++) { c.moveTo(sx, ye + dir * f * 4.5); c.quadraticCurveTo(sx + 7, ye + dir * (f * 4.5 + 5), sx + 5, ye + dir * (f * 4.5 + 11)); }
      c.stroke(); c.lineWidth = 1.1;
    }
  }
  // beams
  for (const b of BEAMS) {
    const xa = X(b.t0), xb = X(b.t1); if (xb < LEFT - 30 || xa > W + 30) continue;
    const st = b.gs[0].st, off = b.up ? rx - 0.6 : -rx + 0.6, th = SP * 0.5 * (b.up ? 1 : -1);
    const on = b.gs.some(g => g.t <= p + 1e-6 && p < g.t + g.d - 1e-6);
    c.fillStyle = on ? (st ? col.chord : col.melody) : col.ink;
    const seg = (ta, tb, lvl) => { const ya = Y(st, b.at(ta)) + lvl * th * 1.6, yb = Y(st, b.at(tb)) + lvl * th * 1.6; c.beginPath(); c.moveTo(X(ta) + off, ya); c.lineTo(X(tb) + off, yb); c.lineTo(X(tb) + off, yb + th); c.lineTo(X(ta) + off, ya + th); c.closePath(); c.fill(); };
    seg(b.t0, b.t1, 0);
    for (let i = 0; i < b.gs.length; i++) {
      const g = b.gs[i]; if (g.d > 0.75 + 1e-6) continue;
      const nx = b.gs[i + 1], pv = b.gs[i - 1];
      if (nx && nx.d <= 0.75 + 1e-6) seg(g.t, nx.t, 1);
      else if (!pv || pv.d > 0.75 + 1e-6) { const dt = 0.3 * (nx ? 1 : -1); seg(Math.min(g.t, g.t + dt), Math.max(g.t, g.t + dt), 1); }
    }
  }
  // fixed left panel: clefs and key signature for what is at the left edge
  const tl = p - (x0 - LEFT) / PPE;
  c.fillStyle = col.surface; c.fillRect(0, 0, LEFT, H); staffLines(0, LEFT);
  const k = keyAt(Math.max(p, 0));
  for (let st = 0; st < 2; st++) {
    const clef = clefAt(st, Math.max(tl, 0));
    c.fillStyle = col.ink; drawClef(c, clef, 16, st, 1);
    const posF = clef === 'G' ? [4, 7, 3, 6, 2, 5, 1] : [2, 5, 1, 4, 0, 3, -1], posS = clef === 'G' ? [8, 5, 9, 6, 3, 7, 4] : [6, 3, 7, 4, 1, 5, 2];
    c.font = `${SP * 2.3}px ${MUSIC_FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle';
    for (let i = 0; i < Math.abs(k); i++) c.fillText(k < 0 ? '♭' : '♯', 36 + i * 9, Y(st, (k < 0 ? posF : posS)[i]) + (k < 0 ? -SP * 0.35 : 0));
  }
  c.strokeStyle = col.muted; c.lineWidth = 1; c.beginPath(); c.moveTo(0.5, Y_T); c.lineTo(0.5, Y_B + 4 * SP); c.stroke();
  // playhead
  c.strokeStyle = col.melody; c.globalAlpha = 0.7; c.lineWidth = 2; c.beginPath(); c.moveTo(x0, Y_T - 16); c.lineTo(x0, Y_B + 4 * SP + 16); c.stroke(); c.globalAlpha = 1;
  c.textAlign = 'left'; c.textBaseline = 'alphabetic';
}
function drawClef(c, clef, x, st, scale) {
  const top = st ? Y_B : Y_T;
  c.textAlign = 'center'; c.textBaseline = 'alphabetic';
  if (clef === 'G') { c.font = `${SP * 5.5 * scale}px ${MUSIC_FONT}`; c.fillText('𝄞', x, top + 4 * SP - 1 + (1 - scale) * -SP); }
  else { c.font = `${SP * 5.4 * scale}px ${MUSIC_FONT}`; c.fillText('𝄢', x, top + SP * 3.6 * scale + (1 - scale) * SP); }
}
for (const id of ['foldChords', 'foldSheet']) {
  const el = $(id);
  try { const v = localStorage.getItem('cdl-' + id); if (v !== null) el.open = v === '1'; } catch (e) {}
  el.addEventListener('toggle', () => { try { localStorage.setItem('cdl-' + id, el.open ? '1' : '0'); } catch (e) {} layout(); });
}
'''

def late():
    rex(r'<div class="board">.*?(?=\n\s*<div class="piano">)', BOARD.rstrip())
    rex(r'<div class="strip" id="strip".*?</div>\s*</div>\n', FOLDS)
    rep('</style>', CSS + '</style>')
    rep('family=Instrument+Sans:wght@400;500;600&display=swap', 'family=Instrument+Sans:wght@400;500;600&family=Noto+Music&display=swap')
    rep('for (const c of [roll, keys]) {', 'for (const c of [roll, keys, sheetC]) {')
    rep('readColors(); layout(); buildEvents();', SHEET_JS + '\nreadColors(); layout(); buildEvents();')
    rep("  requestAnimationFrame(draw);\n}", "  if ($('foldSheet').open) drawSheet(p);\n  requestAnimationFrame(draw);\n}")
