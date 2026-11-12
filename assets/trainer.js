const SONG = window.SONG, D = SONG.data, CH = SONG.chords, SECTIONS = SONG.sections;
const PICK = D.pickup, CAD = D.cadenza, NB = D.bars.length, BEATS = D.beats, BL = D.bl || 3, BARLEN = BEATS * BL, BEAMLEN = D.beam || BL;
const tonesOf = sym => CH[sym.split("/")[0]];
const BEATS_HTML = '<div class="beats">' + Array.from({ length: BEATS }, (_, i) => `<span>${i + 1}</span>`).join('') + '</div>';

/* ---------- music helpers ---------- */
const LET = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const pcOf = n => (LET[n[0]] + (n.includes('♭') ? -1 : 0) + (n.includes('♯') ? 1 : 0) + 12) % 12;
const FLATS = ['C','D♭','D','E♭','E','F','G♭','G','A♭','A','B♭','B'];
const secOf = n => SECTIONS.find(s => n >= s.from && n <= s.to);

function voicing(sym) {
  const [base, slash] = sym.split('/');
  const tones = CH[base].map(pcOf), root = tones[0];
  const bass = 36 + (slash ? pcOf(slash) : root);   // C2–B2
  const upper = [48 + root];                         // root position from C3–B3
  for (let i = 1; i < tones.length; i++) {
    let m = upper[upper.length - 1] + 1;
    while (m % 12 !== tones[i]) m++;
    upper.push(m);
  }
  return { bass, upper };
}

/* flat list of chords with absolute times */
const CHORDS = [];
D.bars.forEach(b => b.chords.forEach(([s, r, off, d], i) => CHORDS.push({ s, r, t: b.start + off, d, bar: b.n, i })));
const barAt = p => { let b = D.bars[0]; for (const x of D.bars) if (x.start <= p + 1e-6) b = x; return b; };
function chordIndexAt(p) { let k = 0; for (let i = 0; i < CHORDS.length; i++) if (CHORDS[i].t <= p + 1e-6) k = i; return k; }

/* ---------- audio ---------- */
function iosAudioUnlock() {
  try { if (navigator.audioSession) { navigator.audioSession.type = 'playback'; return; } } catch (e) {}
  if (iosAudioUnlock.el || !/iP(hone|ad|od)|Macintosh/.test(navigator.userAgent) || !('ontouchend' in document)) return;
  const el = iosAudioUnlock.el = document.createElement('audio');
  el.src = 'data:audio/wav;base64,UklGRrQBAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YZABAACAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA'; el.loop = true; el.setAttribute('playsinline', ''); el.setAttribute('x-webkit-airplay', 'deny');
  const p = el.play(); if (p && p.catch) p.catch(() => { iosAudioUnlock.el = null; });
}

let ac = null, master, buses = {}, voices = new Set();
function initAudio() {
  if (ac) return;
  try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}
  ac = new (window.AudioContext || window.webkitAudioContext)();
  const comp = ac.createDynamicsCompressor(); comp.threshold.value = -14; comp.ratio.value = 4;
  master = ac.createGain(); master.gain.value = 0.9;
  const rev = ac.createConvolver(); rev.buffer = impulse(2.6);
  const wet = ac.createGain(); wet.gain.value = 0.28;
  master.connect(comp); master.connect(rev); rev.connect(wet); wet.connect(comp); comp.connect(ac.destination);
  for (const k of ['mel', 'acc', 'ui']) { buses[k] = ac.createGain(); buses[k].connect(master); }
  applyMutes();
  const amps = [1, .62, .32, .2, .12, .07, .045, .03];
  waves.bright = ac.createPeriodicWave(new Float32Array([0, ...amps]), new Float32Array(amps.length + 1));
  waves.soft = ac.createPeriodicWave(new Float32Array([0, 1, .35, .12, .05]), new Float32Array(5));
  waves.warm = ac.createPeriodicWave(new Float32Array([0, 1, .42, .16, .07, .03, .015]), new Float32Array(7));
  waves.felt = ac.createPeriodicWave(new Float32Array([0, 1, .22, .05, .015]), new Float32Array(5));
  waves.sine = ac.createPeriodicWave(new Float32Array([0, 1, .06]), new Float32Array(3));
}
/* Sound presets. "piano" is used for the chords; the melody uses whichever the viewer picks. */
const TONES = {
  bright: { w1: m => m < 84 ? 'bright' : 'soft', w2: 'soft', mix: .35, det: 4, atk: .006, cut0: f => Math.min(f * 9 + 1800, 14000), cut1: f => Math.max(f * 2.2, 500), sus: 1, vel: 1 },
  warm:   { w1: () => 'warm', w2: 'felt', mix: .5, det: 6, atk: .012, cut0: f => Math.min(f * 4 + 700, 5000), cut1: f => Math.max(f * 1.6, 450), sus: 1.25, vel: .9 },
  felt:   { w1: () => 'felt', w2: 'sine', mix: .6, det: -7, atk: .025, cut0: f => Math.min(f * 2.5 + 300, 2800), cut1: f => Math.max(f * 1.3, 380), sus: 1.4, vel: 1 },
};
TONES.piano = TONES.bright;
let melTone = 'warm';
const waves = {};
function impulse(sec) {
  const len = ac.sampleRate * sec, buf = ac.createBuffer(2, len, ac.sampleRate);
  for (let c = 0; c < 2; c++) { const d = buf.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2); }
  return buf;
}
function playNote(m, when, dur, vel, bus) {
  const f = 440 * Math.pow(2, (m - 69) / 12);
  const g = ac.createGain(), lp = ac.createBiquadFilter();
  const P = TONES[bus === 'mel' ? melTone : 'piano'];
  lp.type = 'lowpass'; lp.Q.value = 0.3;
  const o1 = ac.createOscillator(), o2 = ac.createOscillator();
  o1.setPeriodicWave(waves[P.w1(m)]); o2.setPeriodicWave(waves[P.w2]);
  o1.frequency.value = f; o2.frequency.value = f; o2.detune.value = P.det;
  const o2g = ac.createGain(); o2g.gain.value = P.mix;
  o1.connect(lp); o2.connect(o2g); o2g.connect(lp); lp.connect(g); g.connect(buses[bus]);
  const tau = Math.max(0.5, Math.min(3.2, 3.6 - (m - 30) * 0.045)) * P.sus;
  const v = vel * P.vel * (m < 48 ? 1.15 : 1);
  g.gain.setValueAtTime(0, when);
  g.gain.linearRampToValueAtTime(v, when + P.atk);
  g.gain.setTargetAtTime(v * 0.0001, when + P.atk, tau);
  lp.frequency.setValueAtTime(P.cut0(f), when);
  lp.frequency.setTargetAtTime(P.cut1(f), when + 0.01, tau * 0.5);
  const end = when + Math.max(dur, 0.08);
  g.gain.setTargetAtTime(0, end, 0.09);
  o1.start(when); o2.start(when); o1.stop(end + 0.7); o2.stop(end + 0.7);
  const vo = { g, o1, o2 }; voices.add(vo);
  o1.onended = () => voices.delete(vo);
}
function silence() {
  if (!ac) return;
  const now = ac.currentTime;
  for (const v of voices) { try { v.g.gain.cancelScheduledValues(now); v.g.gain.setTargetAtTime(0, now, 0.03); v.o1.stop(now + 0.2); v.o2.stop(now + 0.2); } catch (e) {} }
  voices.clear();
}

/* ---------- events ---------- */
const $ = id => document.getElementById(id);
/* ---------- fill in this song's text ---------- */
$('songEyebrow').textContent = SONG.eyebrow; $('songTitle').innerHTML = SONG.titleHtml; $('songMeta').innerHTML = SONG.metaHtml;
$('practice').innerHTML = SONG.practiceHtml; $('glossary').innerHTML = SONG.glossaryHtml; $('credits').innerHTML = SONG.creditsHtml;
$('countText').textContent = SONG.countText;
{ const L = D.lib || {}, LV = { 1: ['Beginner', '#24C49B'], 2: ['Intermediate', '#FFC83A'], 3: ['Advanced', '#FF6A50'] }[L.difficulty];
  if (LV) $('songBadges').innerHTML = `<span class="lvl" style="background:${LV[1]}">${LV[0]}</span><span class="mood">${L.mood}</span><span>${L.era}</span><span>~${L.minutes} min</span>`; }
{ const btn = $('themeBtn'), sync = () => { const dark = document.documentElement.dataset.theme === 'dark'; btn.textContent = dark ? '☀ Light' : '☾ Dark'; btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode'); };
  btn.onclick = () => { const dark = document.documentElement.dataset.theme !== 'dark'; if (dark) document.documentElement.dataset.theme = 'dark'; else delete document.documentElement.dataset.theme;
    try { localStorage.setItem('pct-theme', dark ? 'dark' : 'light'); } catch (e) {} sync(); };
  sync(); }
$('style').options[2].textContent = SONG.leftHand; $('style').value = SONG.defaultStyle;
$('loopFrom').max = NB; $('loopTo').max = NB;
document.documentElement.style.setProperty('--beats', BEATS);
try { localStorage.setItem('pct-last', SONG.id); } catch (e) {}
let accEvents = [], melEvents = [], events = [];
function buildEvents() {
  melEvents = [];
  for (const [t, d, ms] of D.rh) {
    const top = Math.max(...ms);
    for (const m of ms) melEvents.push({ t, d, m, vel: m === top ? 0.26 : 0.15, bus: 'mel', sd: d * 1.05 });
  }
  const style = $('style').value;
  accEvents = [];
  const pushOrig = (from, to) => {
    for (const [t, d, ms] of D.lh) {
      if (t < from - 1e-6 || t >= to - 1e-6) continue;
      const b = barAt(t), rel = t - b.start;
      let sus = b.n === CAD ? Math.max(d, 14 - rel) : Math.max(d, Math.ceil((rel + 0.01) / BL) * BL - rel);
      ms.forEach((m, i) => accEvents.push({ t, d, m, vel: ms.length === 1 ? 0.2 : 0.11, bus: 'acc', sd: sus, bass: ms.length === 1 }));
    }
  };
  if (style === 'orig') pushOrig(0, D.end);
  else for (const c of CHORDS) {
    const { bass, upper } = voicing(c.s);
    const b = D.bars[c.bar - 1];
    if (style === 'pattern' && b.n === CAD) { pushOrig(b.start, b.start + b.len); continue; }
    if (style === 'block' || c.d < Math.min(BL, 3) || b.n >= 33 && style === 'pattern' && false) {
      accEvents.push({ t: c.t, d: c.d, m: bass, vel: 0.2, bus: 'acc', sd: c.d, bass: true });
      upper.forEach(m => accEvents.push({ t: c.t, d: c.d, m, vel: 0.11, bus: 'acc', sd: c.d }));
    } else {
      const step = BL === 3 ? 1 : BL, bassUnit = BL === 3 ? 3 : (BEATS === 4 ? 2 * BL : BARLEN);
      for (let e = c.t; e < c.t + c.d - 1e-6; e += step) {
        const k = Math.round(e - b.start) % bassUnit, rest = c.t + c.d - e;
        if (k === 0) accEvents.push({ t: e, d: step, m: bass, vel: 0.2, bus: 'acc', sd: Math.min(rest, bassUnit), bass: true });
        else upper.forEach(m => accEvents.push({ t: e, d: step, m, vel: 0.095, bus: 'acc', sd: Math.min(rest, Math.max(2, step)) }));
      }
    }
  }
  events = melEvents.concat(accEvents).sort((a, b) => a.t - b.t);
}

/* ---------- transport ---------- */
let playing = false, pos = 0, anchorCtx = 0, anchorPos = 0, schedPos = 0, evIdx = 0, timer = null;
const spe = () => 60 / +$('tempo').value;     // seconds per eighth note
function curPos() { return playing ? anchorPos + (ac.currentTime - anchorCtx) / spe() : pos; }
function loopRange() {
  const mode = $('loopMode').value;
  if (mode === 'off') return null;
  const b = barAt(Math.max(pos, PICK));
  if (mode === 'bar') return [b.start, b.start + b.len];
  if (mode === 'section') { const s = secOf(b.n); return [D.bars[s.from - 1].start, D.bars[s.to - 1].start + D.bars[s.to - 1].len]; }
  let f = Math.min(NB, Math.max(1, +$('loopFrom').value || 1)), t = Math.min(NB, Math.max(f, +$('loopTo').value || f));
  return [D.bars[f - 1].start, D.bars[t - 1].start + D.bars[t - 1].len];
}
let loop = null;
function seekIdx(p) { evIdx = 0; while (evIdx < events.length && events[evIdx].t < p - 1e-6) evIdx++; }
function anchor(p) { anchorCtx = ac.currentTime + 0.05; anchorPos = p; schedPos = p; seekIdx(p); }
function tick() {
  const horizon = anchorPos + (ac.currentTime + 0.15 - anchorCtx) / spe();
  let guard = 0;
  while (schedPos < horizon && guard++ < 4) {
    const stop = loop ? Math.min(horizon, loop[1]) : Math.min(horizon, D.end);
    while (evIdx < events.length && events[evIdx].t < stop - 1e-6) {
      const e = events[evIdx++];
      if (e.t >= schedPos - 1e-6) playNote(e.m, anchorCtx + (e.t - anchorPos) * spe(), e.sd * spe(), e.vel, e.bus);
    }
    schedPos = stop;
    if (loop && horizon >= loop[1]) {
      anchorCtx = anchorCtx + (loop[1] - anchorPos) * spe(); anchorPos = loop[0]; schedPos = loop[0]; seekIdx(loop[0]);
    } else if (!loop && schedPos >= D.end) {
      if (ac.currentTime > anchorCtx + (D.end - anchorPos) * spe() + 1.5) { pause(); setPos(0); window.dispatchEvent(new Event('pieceend')); }
      break;
    }
  }
}
function play() {
  initAudio(); iosAudioUnlock(); ac.resume();
  if (pos >= D.end - 0.01) pos = 0;
  loop = loopRange();
  if (loop && (pos < loop[0] || pos >= loop[1])) pos = loop[0];
  playing = true; anchor(pos);
  timer = setInterval(tick, 25); tick();
  $('playBtn').textContent = '❚❚ Pause';
}
function pause() {
  if (!playing) return;
  pos = Math.min(curPos(), D.end); playing = false; clearInterval(timer); silence();
  $('playBtn').textContent = '▶ Play';
}
function setPos(p) {
  p = Math.max(0, Math.min(p, D.end));
  if (playing) { silence(); pos = p; loop = loopRange(); if (loop && (p < loop[0] || p >= loop[1])) loop = null, $('loopMode').value = 'off', syncRange(); anchor(p); }
  else pos = p;
  lastChord = -1;
}
function restartLoop() { if (playing) { const p = curPos(); silence(); pos = p; loop = loopRange(); if (loop && (p < loop[0] || p >= loop[1])) pos = loop[0]; anchor(pos); } }
function auditionChord(sym) {
  initAudio(); iosAudioUnlock(); ac.resume();
  const { bass, upper } = voicing(sym), t = ac.currentTime + 0.02;
  playNote(bass, t, 1.6, 0.22, 'ui'); upper.forEach((m, i) => playNote(m, t + 0.03 * (i + 1), 1.6, 0.13, 'ui'));
  flash = { notes: [bass, ...upper], until: performance.now() + 1200 };
}
$('melTone').onchange = () => {
  melTone = $('melTone').value;
  if (playing) { const p = curPos(); silence(); anchor(p); }
  else { initAudio(); iosAudioUnlock(); ac.resume(); [79, 77, 79, 75].forEach((m, i) => playNote(m, ac.currentTime + 0.05 + i * 0.32, 0.4, 0.26, 'mel')); }
};
$('melVol').oninput = applyMutes;
function applyMutes() { if (!ac) return; buses.mel.gain.value = $('melOn').checked ? $('melVol').value / 100 : 0; buses.acc.gain.value = $('accOn').checked ? 1 : 0; }

/* ---------- controls ---------- */
$('playBtn').onclick = () => playing ? pause() : play();
$('restartBtn').onclick = () => { setPos(0); if (!playing) play(); };
$('prevBar').onclick = () => stepBar(-1);
$('nextBar').onclick = () => stepBar(1);
function stepBar(dir) {
  const p = curPos(), b = barAt(Math.max(p, PICK));
  let n = b.n + dir;
  if (dir < 0 && p - b.start > 2) n = b.n;
  n = Math.max(1, Math.min(NB, n));
  setPos(D.bars[n - 1].start - (n === 1 ? PICK : 0));
}
$('tempo').oninput = () => { $('tempoVal').textContent = $('tempo').value; if (playing) { const p = curPos(); silence(); anchor(p); } };
$('melOn').onchange = applyMutes; $('accOn').onchange = applyMutes;
$('style').onchange = () => { buildEvents(); if (playing) { const p = curPos(); silence(); anchor(p); } };
function syncRange() { $('rangeBox').hidden = $('loopMode').value !== 'range'; }
$('loopMode').onchange = () => {
  syncRange();
  if ($('loopMode').value === 'range') { const b = barAt(Math.max(curPos(), PICK)); $('loopFrom').value = b.n; $('loopTo').value = Math.min(NB, b.n + 3); }
  restartLoop();
};
$('loopFrom').onchange = restartLoop; $('loopTo').onchange = restartLoop;
document.addEventListener('keydown', e => {
  if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName) && e.target.type !== 'checkbox' && e.target.type !== 'range') return;
  if (e.code === 'Space') { e.preventDefault(); playing ? pause() : play(); }
  else if (e.code === 'ArrowRight' && e.target.type !== 'range') { e.preventDefault(); stepBar(1); }
  else if (e.code === 'ArrowLeft' && e.target.type !== 'range') { e.preventDefault(); stepBar(-1); }
});

/* ---------- chord map ---------- */
const mapEl = $('map'), chipEls = [], barEls = [];
for (const s of SECTIONS) {
  const sec = document.createElement('div'); sec.className = 'section';
  sec.innerHTML = `<div class="section-head"><h3>${s.id}</h3><span class="what">Bars ${s.from}–${s.to}. ${s.what}</span><button class="btn loopit" type="button">Repeat ${s.id}</button></div><div class="bars"></div>`;
  sec.querySelector('.loopit').onclick = () => {
    $('loopMode').value = 'range'; syncRange(); $('loopFrom').value = s.from; $('loopTo').value = s.to;
    setPos(D.bars[s.from - 1].start); if (!playing) play(); else restartLoop();
  };
  const grid = sec.querySelector('.bars');
  for (let n = s.from; n <= s.to; n++) {
    const b = D.bars[n - 1];
    const el = document.createElement('div'); el.className = 'bar' + (n === CAD ? ' wide' : '');
    el.innerHTML = `<div class="bar-n"><span>Bar ${n}${n === CAD ? ' · cadenza, free time' : ''}</span><button type="button">play</button></div><div class="chips"></div>` +
      (n === CAD ? '' : BEATS_HTML);
    el.querySelector('button').onclick = () => { setPos(b.start - (n === 1 ? PICK : 0)); if (!playing) play(); };
    const chips = el.querySelector('.chips');
    b.chords.forEach(([sym, rom, off, d]) => {
      const c = document.createElement('button'); c.type = 'button';
      c.className = 'chip' + (d < Math.min(BL, 3) ? ' tiny' : '');
      c.style.flex = `${d} 1 0`;
      c.title = `${sym} = ${tonesOf(sym).join(' – ')}  (${rom})`;
      c.innerHTML = `<span class="s">${sym.replace('/', '/<wbr>')}</span><span class="ro">${rom}</span>`;
      c.onclick = () => { setPos(b.start + off); if (!playing) auditionChord(sym); };
      if (d < Math.min(BL, 3)) {
        const beat = Math.floor(off / BL + 1e-6);
        let st = chips.querySelector(`.stack[data-b="${beat}"]`);
        if (!st) { st = document.createElement('div'); st.className = 'stack'; st.dataset.b = beat; st.style.flex = BL + ' 1 0'; chips.appendChild(st); }
        st.appendChild(c);
      } else chips.appendChild(c);
      chipEls.push(c);
    });
    grid.appendChild(el); barEls.push(el);
  }
  mapEl.appendChild(sec);
}

/* ---------- now panel ---------- */
const meter = $('meter');
for (let b = 0; b < BEATS; b++) { const g = document.createElement('span'); g.className = 'beat'; for (let k = 0; k < BL; k++) { const i = document.createElement('i'); if (!k) i.className = 'big'; g.appendChild(i); } meter.appendChild(g); }
const dots = [...meter.querySelectorAll('i')];
let lastChord = -1, lastBar = -1, lastEighth = -1, curNames = {};
const stripBars = $('stripBars'); let stripSec = null, stripChips = {}, stripBarEls = {};
function renderStrip(s, w) {
  stripSec = w; stripChips = {}; stripBarEls = {}; stripBars.innerHTML = '';
  const nx = SECTIONS[SECTIONS.indexOf(s) + 1];
  $('stripTitle').innerHTML = `<b>${s.id}</b> · bars ${s.from}–${s.to}`;
  $('stripNext').textContent = w + 4 <= s.to ? `then bars ${w + 4}–${Math.min(s.to, w + 7)}` : nx ? `then ${nx.id} (bars ${nx.from}–${nx.to})` : 'then the end';
  for (let n = w; n <= Math.min(s.to, w + 3); n++) {
    const b = D.bars[n - 1], el = document.createElement('div'); el.className = 'bar';
    el.innerHTML = `<div class="bar-n"><span>Bar ${n}${n === CAD ? ' · cadenza, free time' : ''}</span></div><div class="chips"></div>`;
    const chips = el.querySelector('.chips');
    let ci = CHORDS.findIndex(c => c.bar === n);
    b.chords.forEach(([sym, rom, off, d]) => {
      const c = document.createElement('button'); c.type = 'button';
      c.className = 'chip' + (d < Math.min(BL, 3) ? ' tiny' : '');
      c.style.flex = `${d} 1 0`;
      c.title = `${sym} = ${tonesOf(sym).join(' – ')}  (${rom})`;
      c.innerHTML = `<span class="s">${sym.replace('/', '/<wbr>')}</span><span class="ro">${rom}</span>`;
      c.onclick = () => { setPos(b.start + off); if (!playing) auditionChord(sym); };
      if (d < Math.min(BL, 3)) {
        const beat = Math.floor(off / BL + 1e-6);
        let st = chips.querySelector(`.stack[data-b="${beat}"]`);
        if (!st) { st = document.createElement('div'); st.className = 'stack'; st.dataset.b = beat; st.style.flex = BL + ' 1 0'; chips.appendChild(st); }
        st.appendChild(c);
      } else chips.appendChild(c);
      stripChips[ci++] = c;
    });
    stripBars.appendChild(el); stripBarEls[n] = el;
  }
}
function updatePanel(p) {
  const bn0 = barAt(Math.max(p, PICK)).n, s0 = secOf(bn0), w0 = s0.from + 4 * Math.floor((bn0 - s0.from) / 4);
  if (w0 !== stripSec) { renderStrip(s0, w0); lastChord = -1; lastBar = -1; }
  const ci = p < PICK ? 0 : chordIndexAt(p), c = CHORDS[ci];
  if (ci !== lastChord) {
    lastChord = ci;
    $('nowSym').textContent = c.s; $('nowRom').textContent = c.r;
    const names = tonesOf(c.s); curNames = {};
    names.forEach(n => curNames[pcOf(n)] = n);
    $('nowTones').innerHTML = names.map((n, i) => `<span class="tone${i ? '' : ' root'}">${n}</span>`).join('') + (c.s.includes('/') ? `<span class="tone bassnote">bass ${c.s.split('/')[1]}</span>` : '');
    const nx = CHORDS[ci + 1];
    $('nextChord').innerHTML = nx ? `Next: <b>${nx.s}</b> &nbsp;in bar ${nx.bar}` : 'Last chord: let it ring';
    chipEls.forEach((el, i) => el.classList.toggle('cur', i === ci));
    for (const k in stripChips) stripChips[k].classList.toggle('cur', +k === ci);
  }
  const b = barAt(Math.max(p, PICK));
  if (b.n !== lastBar) {
    lastBar = b.n; barEls.forEach((el, i) => el.classList.toggle('cur', i === b.n - 1));
    for (const k in stripBarEls) stripBarEls[k].classList.toggle('cur', +k === b.n);
    if (stripBarEls[b.n]) stripBars.scrollLeft = stripBarEls[b.n].offsetLeft - 8;
    const s = secOf(b.n); $('secTag').innerHTML = `<b>${s.id}</b> · bars ${s.from}–${s.to}`;
  }
  const e = p < PICK ? -1 : Math.floor(p - b.start + 1e-6);
  const key = b.n * 100 + e;
  if (key !== lastEighth) {
    lastEighth = key;
    const sub = BL === 3 ? ['', '-and', '-a'] : BL === 2 ? ['', '-and'] : BL === 4 ? ['', '-e', '-and', '-a'] : [''];
    if (p < PICK) $('posText').innerHTML = 'Pickup note';
    else if (b.n === CAD) $('posText').innerHTML = `<b>Bar 32</b> · cadenza`;
    else $('posText').innerHTML = `<b>Bar ${b.n}</b> · beat ${Math.floor(e / BL) + 1}${sub[e % BL] || ''}`;
    dots.forEach((d, i) => d.classList.toggle('on', b.n !== CAD && p >= 1 && i === e));
  }
}

/* ---------- drawing ---------- */
const LO = D.lo, HI = D.hi || 100, roll = $('roll'), keys = $('keys');
const isBlack = m => [1, 3, 6, 8, 10].includes(m % 12);
let geo = null, col = {}, flash = null;
function readColors() { const cs = getComputedStyle(document.documentElement); for (const k of ['roll-chord','roll-bass','roll-text','sheet-rh','sheet-lh','coral','melody','melody-soft','chord','chord-soft','bass','key-white','key-black','roll-bg','grid','line','ink','muted','surface']) col[k] = cs.getPropertyValue('--' + k).trim(); }
function layout() {
  const dpr = window.devicePixelRatio || 1;
  for (const c of [roll, keys, sheetC]) { const r = c.getBoundingClientRect(); c.width = Math.round(r.width * dpr); c.height = Math.round(r.height * dpr); c.getContext('2d').setTransform(dpr, 0, 0, dpr, 0, 0); }
  const W = roll.getBoundingClientRect().width, whites = [];
  for (let m = LO; m <= HI; m++) if (!isBlack(m)) whites.push(m);
  const ww = W / whites.length, x = {};
  whites.forEach((m, i) => x[m] = { x: i * ww, w: ww, black: false });
  for (let m = LO; m <= HI; m++) if (isBlack(m)) x[m] = { x: x[m - 1].x + ww - ww * 0.31, w: ww * 0.62, black: true };
  geo = { W, ww, x, RH: roll.getBoundingClientRect().height, KH: keys.getBoundingClientRect().height };
}
function rr(ctx, x, y, w, h, r) { r = Math.min(r, w / 2, h / 2); ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
const LOOK = 12;   // eighth notes visible above the keys
function draw() {
  const p = curPos();
  if (playing) pos = Math.min(p, D.end);
  updatePanel(p);
  const { W, x, RH, KH } = geo, ctx = roll.getContext('2d'), k = keys.getContext('2d');
  const ppe = RH / LOOK;
  ctx.fillStyle = col['roll-bg']; ctx.fillRect(0, 0, W, RH);
  // octave guides + bar lines
  ctx.fillStyle = col.grid;
  for (let m = LO; m <= HI; m++) if (m % 12 === 0) ctx.fillRect(x[m].x, 0, 1, RH);
  for (const b of D.bars) for (let e = 0; e <= b.len; e += BL) {
    const y = RH - (b.start + e - p) * ppe; if (y < 0 || y > RH) continue;
    ctx.fillStyle = col.grid; ctx.fillRect(0, y, W, e === 0 ? 2 : 1);
    if (e === 0) { ctx.fillStyle = col['roll-text']; ctx.font = '11px ' + getComputedStyle(document.body).fontFamily; ctx.fillText('Bar ' + b.n, 6, y - 4); }
  }
  const active = {};
  const accOn = $('accOn').checked, melOn = $('melOn').checked;
  for (const e of events) {
    if (e.t > p + LOOK) break;
    if (e.t + e.d < p) continue;
    if (e.bus === 'acc' && !accOn || e.bus === 'mel' && !melOn) continue;
    const g = x[e.m]; if (!g) continue;
    const y1 = RH - (e.t - p) * ppe, y0 = RH - (e.t + e.d - p) * ppe;
    const c = e.bus === 'mel' ? col.melody : e.bass ? col['roll-bass'] : col['roll-chord'];
    ctx.fillStyle = c; rr(ctx, g.x + 1.5, y0 + 1, g.w - 3, Math.max(4, y1 - y0 - 2), 4); ctx.fill();
    if (e.t <= p + 1e-6 && p < e.t + e.d) active[e.m] = c;
  }
  if (flash && performance.now() < flash.until) flash.notes.forEach(m => active[m] = active[m] || col.chord);
  // keys
  k.fillStyle = col.line; k.fillRect(0, 0, W, KH);
  const chordPcs = new Set(Object.keys(curNames).map(Number));
  for (let pass = 0; pass < 2; pass++) for (let m = LO; m <= HI; m++) {
    const g = x[m]; if (g.black !== !!pass) continue;
    const h = g.black ? KH * 0.62 : KH;
    k.fillStyle = active[m] || (g.black ? col['key-black'] : col['key-white']);
    rr(k, g.x + 0.5, -4, g.w - 1, h + 4 - 1, 3); k.fill();
    if (!active[m] && chordPcs.has(m % 12)) {
      k.strokeStyle = col.chord; k.lineWidth = 2; rr(k, g.x + 2, h - (g.black ? 18 : 22), g.w - 4, g.black ? 14 : 18, 3); k.stroke();
    }
    if (active[m]) {
      const nm = curNames[m % 12] || FLATS[m % 12];
      k.fillStyle = g.black ? col['key-black'] : col['key-white'];
      k.font = `600 ${Math.max(9, Math.min(12, g.w * 0.55))}px ` + getComputedStyle(document.body).fontFamily;
      k.textAlign = 'center'; k.fillText(nm, g.x + g.w / 2, h - 8); k.textAlign = 'left';
    } else if (m % 12 === 0 && !g.black) {
      k.fillStyle = col.muted; k.font = '10px ' + getComputedStyle(document.body).fontFamily; k.textAlign = 'center'; k.fillText('C' + (m / 12 - 1), g.x + g.w / 2, KH - 6); k.textAlign = 'left';
    }
  }
  // hit line
  ctx.fillStyle = col.melody; ctx.globalAlpha = 0.5; ctx.fillRect(0, RH - 2, W, 2); ctx.globalAlpha = 1;
  if ($('foldSheet').open) drawSheet(p);
  requestAnimationFrame(draw);
}
keys.addEventListener('pointerdown', ev => {
  const r = keys.getBoundingClientRect(), px = ev.clientX - r.left, py = ev.clientY - r.top;
  let hit = null;
  for (let m = LO; m <= HI; m++) { const g = geo.x[m]; if (g.black && py < geo.KH * 0.62 && px >= g.x && px < g.x + g.w) hit = m; }
  if (hit == null) for (let m = LO; m <= HI; m++) { const g = geo.x[m]; if (!g.black && px >= g.x && px < g.x + g.w) hit = m; }
  if (hit == null) return;
  initAudio(); iosAudioUnlock(); ac.resume(); playNote(hit, ac.currentTime + 0.01, 0.9, 0.25, 'ui');
  flash = { notes: [hit], until: performance.now() + 500 };
});


const SH = d => d <= 0.76 && Math.abs(d - 2 / 3) > 0.03;   // shorter than an eighth (but not a triplet eighth)
/* ---------- sheet music (simplified engraving drawn on a canvas) ---------- */
const sheetC = $('sheet');
const SP = 7, Y_T = 48, Y_B = Y_T + 4 * SP + 46, PPE = 26, LEFT = 86;
const FLAT_ORDER = [6, 2, 5, 1, 4, 0, 3], SHARP_ORDER = [3, 0, 4, 1, 5, 2, 6];
const keyAt = t => { let k = D.keys[0][1]; for (const [kt, kv] of D.keys) if (kt <= t + 1e-6) k = kv; return k; };
const keyAcc = (step, k) => k < 0 ? (FLAT_ORDER.slice(0, -k).includes(step) ? -1 : 0) : (SHARP_ORDER.slice(0, k).includes(step) ? 1 : 0);
const stateAt = (list, st, t, init) => { let v = init; for (const [et, es, ev] of list) if (es === st && et <= t + 1e-6) v = ev; return v; };
const clefAt = (st, t) => stateAt(D.clefs, st, t, D.clef0[st]), ottAt = (st, t) => stateAt(D.otts, st, t, 0);
const ACC = { '-2': '♭♭', '-1': '♭', '0': '♮', '1': '♯', '2': '×' };
const SG = [], BEAMS = [];
{
  const map = new Map();
  for (const [t, d, st, ds, acc, v, m] of D.sh) {
    const k = t + '|' + d + '|' + st + '|' + v;
    let g = map.get(k);
    if (!g) { g = { t, d, st, v, bar: Math.floor((t - PICK) / BARLEN + 1e-6), ns: [] }; map.set(k, g); SG.push(g); }
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
    if (p && Math.abs(p.t + p.d - g.t) < 1e-6 && Math.floor((p.t - PICK) / BEAMLEN + 1e-6) === Math.floor((g.t - PICK) / BEAMLEN + 1e-6)) {
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
  c.font = 'italic 12px ' + getComputedStyle(document.body).fontFamily; c.fillStyle = col.coral;
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
  for (let st = 0; st < 2; st++) { let prev = D.clef0[st]; for (const [t, es, v] of D.clefs) if (es === st) { if (v !== prev) { const x = X(t) - 22; if (x > LEFT && x < W) drawClef(c, v, x, st, 0.72); } prev = v; } }
  const rx = SP * 0.64, ry = SP * 0.46;
  const stemEnd = g => g.beam ? g.beam.at(g.t) : (g.up ? g.hi + 6.5 : g.lo - 6.5);
  for (const g of SG) {
    const x = X(g.t); if (x > W + 30) break; if (x < LEFT - 30) continue;
    const on = g.t <= p + 1e-6 && p < g.t + g.d - 1e-6;
    const ink = on ? (g.st ? col['sheet-lh'] : col['sheet-rh']) : col.ink;
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
      const nf = SH(g.d) ? 2 : 1, dir = g.up ? 1 : -1;
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
    c.fillStyle = on ? (st ? col['sheet-lh'] : col['sheet-rh']) : col.ink;
    const seg = (ta, tb, lvl) => { const ya = Y(st, b.at(ta)) + lvl * th * 1.6, yb = Y(st, b.at(tb)) + lvl * th * 1.6; c.beginPath(); c.moveTo(X(ta) + off, ya); c.lineTo(X(tb) + off, yb); c.lineTo(X(tb) + off, yb + th); c.lineTo(X(ta) + off, ya + th); c.closePath(); c.fill(); };
    seg(b.t0, b.t1, 0);
    for (let i = 0; i < b.gs.length; i++) {
      const g = b.gs[i]; if (!SH(g.d)) continue;
      const nx = b.gs[i + 1], pv = b.gs[i - 1];
      if (nx && SH(nx.d)) seg(g.t, nx.t, 1);
      else if (!pv || !SH(pv.d)) { const dt = 0.3 * (nx ? 1 : -1); seg(Math.min(g.t, g.t + dt), Math.max(g.t, g.t + dt), 1); }
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
  try { const v = localStorage.getItem('pct-' + id); if (v !== null) el.open = v === '1'; } catch (e) {}
  el.addEventListener('toggle', () => { try { localStorage.setItem('pct-' + id, el.open ? '1' : '0'); } catch (e) {} layout(); });
}

readColors(); layout(); buildEvents();
window.addEventListener('resize', () => { layout(); });
try { matchMedia('(prefers-color-scheme: dark)').addEventListener('change', readColors); } catch (e) {}
new MutationObserver(readColors).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class', 'style'] });
// keep the middle of the keyboard in view on narrow screens
requestAnimationFrame(() => { const sc = $('pianoScroll'); sc.scrollLeft = (sc.scrollWidth - sc.clientWidth) * 0.55; });
requestAnimationFrame(draw);

/* ---------- drag, swipe, tap or scroll the sheet music to move ---------- */
{
  const tip = $('scrubTip');
  const x0Of = () => LEFT + Math.min(sheetC.getBoundingClientRect().width * 0.22, 220);
  const clamp = p => Math.max(0, Math.min(p, D.end - 0.01));
  const where = p => {
    if (p < PICK - 1e-6) return 'Pickup';
    const b = barAt(p), e = Math.floor(p - b.start + 1e-6);
    return b.n === CAD ? `Bar ${b.n} · cadenza` : `Bar ${b.n} · beat ${Math.floor(e / BL) + 1}`;
  };
  const snap = p => {
    if (p < PICK - 1e-6) return 0;
    const b = barAt(p);
    return Math.min(b.start + Math.round((p - b.start) / BL) * BL, b.start + b.len - BL > b.start ? b.start + b.len - 1e-6 : b.start);
  };
  const showTip = (p, x) => { tip.hidden = false; tip.textContent = where(p); tip.style.left = x + 'px'; };
  let drag = null;
  sheetC.addEventListener('pointerdown', e => {
    if (e.button !== undefined && e.button !== 0) return;
    drag = { x: e.clientX, y: e.clientY, p: curPos(), wasPlaying: playing, moved: false, id: e.pointerId };
    if (playing) pause();
  });
  sheetC.addEventListener('pointermove', e => {
    if (!drag || e.pointerId !== drag.id) return;
    const dx = e.clientX - drag.x;
    if (!drag.moved) {
      if (Math.abs(dx) < 6) return;
      if (Math.abs(e.clientY - drag.y) > Math.abs(dx)) { drag = null; return; }   // a vertical swipe scrolls the page
      drag.moved = true; sheetC.classList.add('dragging');
      try { sheetC.setPointerCapture(e.pointerId); } catch (err) {}
    }
    const p = clamp(drag.p - dx / PPE);
    setPos(p); showTip(p, x0Of());
  });
  const end = e => {
    if (!drag || (e && e.pointerId !== drag.id)) return;
    const d = drag; drag = null; sheetC.classList.remove('dragging');
    let p;
    if (!d.moved) {   // a tap: jump to the spot that was tapped
      const r = sheetC.getBoundingClientRect(), x = e.clientX - r.left;
      if (x < LEFT) { if (d.wasPlaying) play(); return; }
      p = clamp(d.p + (x - x0Of()) / PPE);
    } else p = curPos();
    p = snap(p); setPos(p); showTip(p, x0Of());
    clearTimeout(tip._t); tip._t = setTimeout(() => { tip.hidden = true; }, 900);
    if (d.wasPlaying) play();
  };
  sheetC.addEventListener('pointerup', end);
  sheetC.addEventListener('pointercancel', () => { if (drag) { const d = drag; drag = null; sheetC.classList.remove('dragging'); if (d.wasPlaying) play(); } });
  sheetC.addEventListener('wheel', e => {
    const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : (e.shiftKey ? e.deltaY : 0);
    if (!delta) return;   // ordinary vertical scrolling keeps scrolling the page
    e.preventDefault();
    const p = clamp(curPos() + delta / PPE);
    setPos(p); showTip(p, x0Of());
    clearTimeout(tip._t); tip._t = setTimeout(() => { tip.hidden = true; }, 700);
  }, { passive: false });
}

{ const t = D.lib && D.lib.startTempo; if (t) { $('tempo').value = t; $('tempoVal').textContent = t; } }

/* ---------- fun fact sticky note: tap to flip; flips open once when you reach the end ---------- */
if (D.fact) {
  const note = $('factNote'), card = $('factCard'), KEY = 'pct-fact-' + location.pathname.split('/').pop();
  $('factText').textContent = D.fact; note.hidden = false;
  const burst = () => {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const syms = ['♪', '♫', '♩', '♬', '✦'], cols = ['var(--cobalt)', 'var(--coral)', 'var(--mint)', 'var(--lilac)', '#14151C'];
    for (let i = 0; i < 10; i++) {
      const el = document.createElement('i'), a = (i / 10) * Math.PI * 2 + Math.random() * .5, d = 70 + Math.random() * 50;
      el.className = 'fn-burst'; el.textContent = syms[i % syms.length]; el.style.color = cols[i % cols.length];
      el.style.setProperty('--dx', Math.cos(a) * d + 'px'); el.style.setProperty('--dy', Math.sin(a) * d * .7 + 'px'); el.style.setProperty('--r', (Math.random() * 80 - 40) + 'deg');
      note.appendChild(el); setTimeout(() => el.remove(), 1200);
    }
  };
  const setOpen = (open, head) => {
    if (head) $('factHead').textContent = head;
    if (note.classList.contains('open') === open) return;
    card.classList.remove('flip'); void card.offsetWidth; card.classList.add('flip');
    setTimeout(() => {
      if (open && matchMedia('(max-width: 899px)').matches) note.style.height = note.offsetHeight + 'px'; else note.style.height = '';   // hold the closed size so nothing below moves
      note.classList.toggle('open', open); card.setAttribute('aria-expanded', open);
    }, 160);
    if (open) setTimeout(burst, 180);
  };
  card.addEventListener('animationend', () => card.classList.remove('flip', 'pop'));
  card.onclick = () => setOpen(!note.classList.contains('open'), '🎵 Fun fact');
  addEventListener('pieceend', () => {
    let seen = false; try { seen = localStorage.getItem(KEY) === '1'; localStorage.setItem(KEY, '1'); } catch (e) {}
    if (seen) return;
    if (note.classList.contains('open')) { $('factHead').textContent = '🎉 You made it to the end!'; card.classList.add('pop'); burst(); }
    else setOpen(true, '🎉 You made it to the end! Fun fact:');
    if (note.getBoundingClientRect().bottom < 0) note.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}
