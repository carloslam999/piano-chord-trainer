"""Build the Clair de Lune trainer from the Nocturne page + parsed notes."""
import json, re, sys
notes = json.load(open(sys.argv[1]))
s = open(sys.argv[2]).read()

def rep(a, b, n=1):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b) if n == 0 else s.replace(a, b, n)
def rex(pat, b):
    global s
    assert re.search(pat, s, flags=re.S), pat[:60]
    s = re.sub(pat, lambda m: b, s, count=1, flags=re.S)

# ---------- chords: (symbol, roman, eighths) per bar; my own reading of the score ----------
I, I6 = ('D♭', 'I'), ('D♭/F', 'I')
C = {
 1: [('D♭', 'I', 9)], 2: [('C°7/G♭', 'vii°⁷', 9)], 3: [('D♭/F', 'I', 9)], 4: [('A♭7/E♭', 'V⁷', 9)],
 5: [('E♭m7/D♭', 'ii⁷', 6), ('A♭7/C', 'V⁷', 3)], 6: [('E♭m7/B♭', 'ii⁷', 6), ('F7/A', 'V⁷/vi', 3)],
 7: [('B♭m7/A♭', 'vi⁷', 6), ('G♭', 'IV', 3)], 8: [('B♭m7/F', 'vi⁷', 6), ('A♭7', 'V⁷', 3)],
 9: [('D♭', 'I', 9)], 10: [('G♭', 'IV', 9)], 11: [('D♭/F', 'I', 9)], 12: [('G♭', 'IV', 9)],
 13: [('D♭7/A♭', 'V⁷/IV', 9)], 14: [('B♭m', 'vi', 9)],
 15: [('E♭m7', 'ii⁷', 9)], 16: [('G♭/B♭', 'IV', 9)], 17: [('E♭m7', 'ii⁷', 9)], 18: [('E♭m7/B♭', 'ii⁷', 9)],
 19: [('A♭7', 'V⁷', 9)], 20: [('A°7', 'vii°⁷/vi', 9)], 21: [('G♭/B♭', 'IV', 9)], 22: [('Cm7♭5', 'vii∅⁷', 9)],
 23: [('G♭/D♭', 'IV', 9)], 24: [('E♭m7', 'ii⁷', 9)],
 25: [('D♭/F', 'I', 6), ('B♭m7♭5/F♭', 'vi∅⁷', 3)], 26: [('A♭7sus/E♭', 'V⁷sus', 6), ('A♭7', 'V⁷', 3)],
 27: [('D♭', 'I', 3), ('Fm', 'iii', 3), ('D♭m7/A♭', 'i⁷', 3)], 28: [('D♭', 'I', 3), ('Fm', 'iii', 3), ('D♭m7/A♭', 'i⁷', 3)],
 29: [('D♭', 'I', 9)], 30: [('E♭7', 'V⁷/V', 9)],
 31: [('A♭7', 'V⁷', 3), ('G♭', 'IV', 3), ('Fm', 'iii', 3)], 32: [('A♭7', 'V⁷', 3), ('G♭', 'IV', 3), ('Fm', 'iii', 3)],
 33: [('E♭m', 'ii', 9)], 34: [('B♭+/D', 'V⁺/ii', 3), ('E♭m', 'ii', 3), ('A♭+', 'V⁺', 3)],
 35: [('D♭', 'I', 3), ('Fm/A♭', 'iii', 3), ('D♭m7/A♭', 'i⁷', 3)], 36: [('D♭', 'I', 3), ('Fm/A♭', 'iii', 3), ('D♭m7/A♭', 'i⁷', 3)],
 37: [('C♯m7', 'vi⁷', 9)], 38: [('Amaj7/G♯', 'IV⁷', 3), ('F♯m', 'ii', 6)],
 39: [('F♯m7/E', 'ii⁷', 3), ('D♯m7♭5', 'vii∅⁷', 3), ('A/C♯', 'IV', 3)],
 40: [('B7', 'V⁷', 3), ('F♯m7/A', 'ii⁷', 3), ('C♯m/G♯', 'vi', 3)],
 41: [('F♯m7', 'ii⁷', 9)], 42: [('F♯m7', 'ii⁷', 9)],
 43: [('A♭7sus', 'V⁷sus', 6), ('A♭7', 'V⁷', 3)], 44: [('A♭7sus', 'V⁷sus', 6), ('A♭7', 'V⁷', 3)],
 45: [('E♭m7', 'ii⁷', 9)], 46: [('E♭m7', 'ii⁷', 9)],
 47: [('E♭m7/G♭', 'ii⁷', 6), ('Cm7♭5', 'vii∅⁷', 3)], 48: [('E♭m7/G♭', 'ii⁷', 6), ('Cm7♭5', 'vii∅⁷', 3)],
 49: [('E♭m7/G♭', 'ii⁷', 9)], 50: [('E♭m7♭5/G♭', 'ii∅⁷', 9)],
 51: [('D♭/F', 'I', 9)], 52: [('F7', 'V⁷/vi', 9)], 53: [('B♭m/F', 'vi', 9)], 54: [('A♭7/E♭', 'V⁷', 9)],
 55: [('E♭m7/D♭', 'ii⁷', 6), ('Fm7/C', 'iii⁷', 3)], 56: [('Fm7/C', 'iii⁷', 3), ('Cm7♭5', 'vii∅⁷', 3), ('F7', 'V⁷/vi', 3)],
 57: [('B♭m7/A♭', 'vi⁷', 6), ('G♭', 'IV', 3)], 58: [('B♭m7/F', 'vi⁷', 6), ('A♭7', 'V⁷', 3)],
 59: [('D♭', 'I', 3), ('D♭7/C♭', 'V⁷/IV', 6)], 60: [('G♭', 'IV', 9)],
 61: [('D♭/A♭', 'I', 3), ('D♭7/A♭', 'V⁷/IV', 6)], 62: [('B♭m', 'vi', 9)],
 63: [('D♭/F', 'I', 9)], 64: [('E♭m7', 'ii⁷', 9)], 65: [('A♭7', 'V⁷', 9)],
 66: [('D♭', 'I', 3), ('Fm', 'iii', 3), ('D♭', 'I', 3)], 67: [('Fm', 'iii', 3), ('D♭m/A♭', 'i', 6)],
 68: [('D♭', 'I', 3), ('Fm', 'iii', 3), ('D♭', 'I', 3)], 69: [('Fm', 'iii', 3), ('D♭m/A♭', 'i', 6)],
 70: [('D♭m/A♭', 'i', 9)], 71: [('D♭', 'I', 9)], 72: [('D♭', 'I', 9)],
}
CH = {
 'D♭': ['D♭','F','A♭'], 'C°7': ['C','E♭','G♭','A'], 'A♭7': ['A♭','C','E♭','G♭'], 'E♭m7': ['E♭','G♭','B♭','D♭'],
 'F7': ['F','A','C','E♭'], 'B♭m7': ['B♭','D♭','F','A♭'], 'G♭': ['G♭','B♭','D♭'], 'D♭7': ['D♭','F','A♭','C♭'],
 'B♭m': ['B♭','D♭','F'], 'E♭m': ['E♭','G♭','B♭'], 'A°7': ['A','C','E♭','G♭'], 'Cm7♭5': ['C','E♭','G♭','B♭'],
 'B♭m7♭5': ['B♭','D♭','F♭','A♭'], 'A♭7sus': ['A♭','D♭','E♭','G♭'], 'Fm': ['F','A♭','C'], 'Fm7': ['F','A♭','C','E♭'],
 'D♭m': ['D♭','F♭','A♭'], 'D♭m7': ['D♭','F♭','A♭','C♭'], 'E♭7': ['E♭','G','B♭','D♭'], 'B♭+': ['B♭','D','G♭'],
 'A♭+': ['A♭','C','E'], 'C♯m7': ['C♯','E','G♯','B'], 'C♯m': ['C♯','E','G♯'], 'Amaj7': ['A','C♯','E','G♯'],
 'A': ['A','C♯','E'], 'F♯m': ['F♯','A','C♯'], 'F♯m7': ['F♯','A','C♯','E'], 'D♯m7♭5': ['D♯','F♯','A','C♯'],
 'B7': ['B','D♯','F♯','A'], 'E♭m7♭5': ['E♭','G♭','A','D♭'],
}
SECTIONS = [
 ('A', 1, 8, 'The theme, in soft thirds. Under it the bass walks down one step per bar: G♭, F, E♭, D♭, B♭, A♭, F.'),
 ('A′', 9, 14, 'The theme again over deep bass notes. D♭ and G♭ take turns, then D♭7 leans toward B♭ minor.'),
 ('B', 15, 26, 'Tempo rubato. Full chords over E♭, then the bass climbs step by step (A♭, A, B♭, C, D♭, E♭) to the high point in bar 25.'),
 ('C', 27, 36, 'Un poco mosso, the flowing arpeggios. Each bar goes D♭, F minor, D♭ minor: that last minor chord is the moonlight colour.'),
 ('D', 37, 42, 'En animant, the climax. The key signature changes to four sharps; the numerals here count from E major.'),
 ('E', 43, 50, 'Calming down over a held A♭, then E♭m7, finding the way home.'),
 ('A″', 51, 58, 'The theme returns, higher and quieter, with F7 in bar 52 as a new colour.'),
 ('A‴', 59, 65, 'Like bars 9–14, ending on A♭7, ready to close.'),
 ('Coda', 66, 72, 'D♭ and F minor rock back and forth, a last touch of D♭ minor, then D♭ to finish.'),
]
for b in range(1, 73):
    assert sum(c[2] for c in C[b]) == 9, b
    for sym, _, _ in C[b]:
        assert sym.split('/')[0] in CH, sym

r = lambda x: round(x * 1000) / 1000
bars = []
for n in range(1, 73):
    off, ch = 0, []
    for sym, rom, d in C[n]: ch.append([sym, rom, off, d]); off += d
    bars.append({'n': n, 'start': (n - 1) * 9, 'len': 9, 'chords': ch})
grp = {'u': {}, 'l': {}}
for t, d, m, st, v, _ds, _acc in notes['notes']:
    grp[st].setdefault((r(t), r(d)), []).append(m)
hand = lambda g: [[t, d, sorted(set(ms))] for (t, d), ms in sorted(g.items())]
data = {'bars': bars, 'rh': hand(grp['u']), 'lh': hand(grp['l']), 'end': 72 * 9, 'pickup': 0, 'cadenza': 0}

exec(open(sys.argv[4]).read())
# ---------- page text ----------
rep('<title>Nocturne Op. 9 No. 2 Chord Trainer</title>', '<title>Clair de Lune Chord Trainer</title>')
rep('<div class="eyebrow">Frédéric Chopin · composed 1830–32</div>', '<div class="eyebrow">Claude Debussy · Suite bergamasque, published 1905</div>')
rep('<h1>Nocturne in <em>E♭</em> major, Op. 9 No. 2</h1>', '<h1>Clair de <em>Lune</em></h1>')
rex(r'<div class="meta">.*?</div>', '<div class="meta"><span><b>Key</b> D♭ major</span><span><b>Time</b> 9/8, three beats of three</span><span><b>Andante</b> très expressif</span><span><b>Length</b> 72 bars</span></div>')
rep('<option value="block">Block chords (easiest)</option>', '<option value="block" selected>Block chords (easiest)</option>')
rep('<option value="pattern" selected>Nocturne pattern: bass, chord, chord</option>', '<option value="pattern">Rocking pattern: bass, chord, chord</option>')
rep("<option value=\"orig\">Chopin's own left hand</option>", "<option value=\"orig\">Debussy's own left hand</option>")
rep('min="1" max="34" value="1"', 'min="1" max="72" value="1"'); rep('min="1" max="34" value="4"', 'min="1" max="72" value="4"')
rep('Each card is one bar: four beats, each three eighth notes long (count “1-and-a, 2-and-a…”).', 'Each card is one bar: three beats, each three eighth notes long (count “1-and-a, 2-and-a, 3-and-a”).')
rex(r'<ol>.*?</ol>', '''<ol>
        <li><b>Start with section C, bars 27–36.</b> It is the part everyone knows, and each bar is the same three chords: D♭, F minor, D♭ minor. Loop it with Melody off and Block chords on.</li>
        <li><b>Then the opening, bars 1–8.</b> The right hand is only two notes at a time. In the left hand, follow the bass note after the slash: it steps down one note per bar.</li>
        <li><b>Add the melody slowly.</b> Speed 50–60, loop two bars. Follow the gold notes as they reach the keys. Many are held a long time, so there is room to think.</li>
        <li><b>Listen to Debussy's own left hand.</b> Switch the chord style to hear how he spreads each chord into a wave of single notes. It is the same harmony you already know.</li>
        <li><b>Take section B in two halves.</b> Bars 15–18 sit on E♭ minor. In bars 19–24 only the bass changes much: A♭, A, B♭, C, D♭, E♭.</li>
        <li><b>Leave section D for last.</b> It is written in sharps and moves fastest. The chords are close cousins of the ones before: C♯ minor is D♭ minor under another name.</li>
      </ol>''')
rex(r'<dl class="glossary">.*?</dl>', '''<dl class="glossary">
        <dt>D♭/F</dt><dd>A slash chord: play a D♭ chord with F as the lowest note. The letter after the slash is the bass.</dd>
        <dt>E♭m7</dt><dd>A minor seventh: minor triad plus a minor seventh (E♭ – G♭ – B♭ – D♭). The soft, hazy sound of this piece.</dd>
        <dt>A♭7</dt><dd>A dominant seventh. It wants to resolve to D♭. A♭7sus swaps the third (C) for the fourth (D♭) first.</dd>
        <dt>C°7</dt><dd>A diminished seventh: four notes stacked in minor thirds.</dd>
        <dt>Cm7♭5</dt><dd>A half-diminished chord: a minor seventh chord with the fifth lowered.</dd>
        <dt>A♭+</dt><dd>An augmented triad: a major triad with the fifth raised a half step.</dd>
        <dt>I, V⁷, ii⁷</dt><dd>Roman numerals count chords from D♭ (from E in bars 37–42). Upper case is major, lower case is minor.</dd>
      </dl>''')
rex(r'<footer>.*?</footer>', '''<footer>
    The chord names are my own reading of the score, simplified to chords you can play; Debussy's harmony often allows more than one name, so treat them as a guide. Melody and left hand are taken from the public-domain E. Fromont 1905 edition as typeset by the <a href="https://www.mutopiaproject.org" target="_blank" rel="noopener">Mutopia Project</a> (Keith OHara, public domain), with grace notes left out. Sound is a synthesised piano made in your browser.
  </footer>''')

# ---------- script ----------
rex(r'const D = \{.*?\};\n', 'const D = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\nconst PICK = D.pickup, CAD = D.cadenza, NB = D.bars.length;\n')
rex(r'const CH = \{.*?\n\};', 'const CH = ' + json.dumps(CH, ensure_ascii=False) + ';\nconst tonesOf = sym => CH[sym.split("/")[0]];')
rex(r'const SECTIONS = \[.*?\n\];', 'const SECTIONS = ' + json.dumps([{'id': a, 'from': b, 'to': c, 'what': d} for a, b, c, d in SECTIONS], ensure_ascii=False) + ';')
rex(r'function voicing\(sym\) \{.*?\n\}\n', '''function voicing(sym) {
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
''')
rep('CH[sym].join', 'tonesOf(sym).join', 0)
rep('const names = CH[c.s]; curNames = {};', 'const names = tonesOf(c.s); curNames = {};')
rep("""$('nowTones').innerHTML = names.map((n, i) => `<span class="tone${i ? '' : ' root'}">${n}</span>`).join('');""",
    """$('nowTones').innerHTML = names.map((n, i) => `<span class="tone${i ? '' : ' root'}">${n}</span>`).join('') + (c.s.includes('/') ? `<span class="tone bassnote">bass ${c.s.split('/')[1]}</span>` : '');""")
rep('<span class="s">${sym}</span>', "<span class=\"s\">${sym.replace('/', '/<wbr>')}</span>", 0)
for a, b in [('p < 1', 'p < PICK'), ('Math.max(p, 1)', 'Math.max(p, PICK)'), ('Math.max(pos, 1)', 'Math.max(pos, PICK)'),
             ('Math.max(curPos(), 1)', 'Math.max(curPos(), PICK)'), ('(n === 1 ? 1 : 0)', '(n === 1 ? PICK : 0)'),
             ('=== 32', '=== CAD'), ('!== 32', '!== CAD'), ('Math.min(34,', 'Math.min(NB,'),
             ('for (let b = 0; b < 4; b++)', 'for (let b = 0; b < 3; b++)'),
             ('<span>1</span><span>2</span><span>3</span><span>4</span>', '<span>1</span><span>2</span><span>3</span>'),
             ('.beats { display: grid; grid-template-columns: repeat(4, 1fr);', '.beats { display: grid; grid-template-columns: repeat(3, 1fr);'),
             ('const LO = 33,', 'const LO = 24,')]:
    rep(a, b, 0)
rep('white-space: nowrap; }\n.chip .ro', 'white-space: normal; overflow-wrap: anywhere; text-align: center; }\n.tone.bassnote { background: none; border: 1px solid var(--line); color: var(--muted); }\n.chip .ro')
rep('.chip .s { font-family: var(--font-display); font-weight: 600; font-size: 17px;', '.chip .s { font-family: var(--font-display); font-weight: 600; font-size: 15px;')
# strip: show four bars at a time
rep('function renderStrip(s) {\n  stripSec = s;', 'function renderStrip(s, w) {\n  stripSec = w;')
rex(r"\$\('stripNext'\)\.textContent = [^\n]*\n", "$('stripNext').textContent = w + 4 <= s.to ? `then bars ${w + 4}–${Math.min(s.to, w + 7)}` : nx ? `then ${nx.id} (bars ${nx.from}–${nx.to})` : 'then the end';\n")
rep("for (let n = s.from; n <= s.to; n++) {\n    const b = D.bars[n - 1], el = document.createElement('div'); el.className = 'bar';",
    "for (let n = w; n <= Math.min(s.to, w + 3); n++) {\n    const b = D.bars[n - 1], el = document.createElement('div'); el.className = 'bar';")
rep("const s0 = secOf(barAt(Math.max(p, PICK)).n);\n  if (s0 !== stripSec) { renderStrip(s0);",
    "const bn0 = barAt(Math.max(p, PICK)).n, s0 = secOf(bn0), w0 = s0.from + 4 * Math.floor((bn0 - s0.from) / 4);\n  if (w0 !== stripSec) { renderStrip(s0, w0);")
late()
s = re.sub(r'\s*<p class="hint" style="display:none">.*?</p>', '', s, count=1, flags=re.S)
open(sys.argv[3], 'w').write(s)
print('ok', len(s), 'rh', len(data['rh']), 'lh', len(data['lh']))
