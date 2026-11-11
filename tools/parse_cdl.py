"""Parser for the Mutopia Clair de Lune source (\\parallelMusic, 4 voices, english note names).
Writes notes as [start, dur, midi, staff] in eighth-notes, plus per-bar length checks."""
import re, json, sys
from fractions import Fraction as F

src = open(sys.argv[1]).read()
VOICES = ['rhUp', 'rhDown', 'lhUp', 'lhDown']
STEP = {'c': 0, 'd': 1, 'e': 2, 'f': 3, 'g': 4, 'a': 5, 'b': 6}
SEMI = [0, 2, 4, 5, 7, 9, 11]
DUR = r'(?:\d+\.*(?:\s*\*\s*\d+(?:/\d+)?)*)'
TOK = re.compile(r"\\tuplet\s*\d+/\d+|\\clef\s+\w+|\\ottava\s*#-?\d+|\\[A-Za-z]+|<<|>>|<|>|\{|\}|~|\||"
                 r"[a-g](?:ss|ff|s|f)?[',]*[!?]?" + DUR + r"?|[rs]" + DUR + r"?|" + DUR)

def clean(t):
    t = re.sub(r'%\{.*?%\}', ' ', t, flags=re.S)
    t = re.sub(r'%[^\n]*', ' ', t)
    t = re.sub(r"(\\once\s*)?\\override\s*[\w.-]+\s*=\s*(#'\([^)]*\)|\S+)", ' ', t)
    t = re.sub(r'\\tempo\s*"[^"]*"', ' ', t)
    t = re.sub(r'\\markup(\\\w+)*\s*"[^"]*"', ' ', t)
    t = re.sub(r'"[^"]*"', ' ', t)
    t = re.sub(r'\\key\s+\w+\s*\\\w+', ' ', t)
    t = re.sub(r'\\barNumberCheck\s*#\d+', ' ', t)
    t = re.sub(r'\\[<>!()]', ' ', t)
    t = re.sub(r'[-_^][.>|^+_\-]', ' ', t)      # articulations
    t = re.sub(r'[\[\]()]', ' ', t)
    return t

def dur_of(tok):
    m = re.search(r'(\d+)(\.*)((?:\s*\*\s*\d+(?:/\d+)?)*)$', tok)
    if not m: return None
    base = F(1, int(m.group(1))); d = base
    for _ in m.group(2): base /= 2; d += base
    for mm in re.finditer(r'\*\s*(\d+)(?:/(\d+))?', m.group(3)):
        d *= F(int(mm.group(1)), int(mm.group(2) or 1))
    return d

class Voice:
    def __init__(self, name):
        self.name = name; self.staff = 'u' if name.startswith('rh') else 'l'
        self.ref = (0, 4); self.t = F(0); self.tied = {}; self.tie = False; self.notes = []

G = {'dur': F(1, 4)}
SPELL = {}
EVENTS = []

def pitch(v, tok):
    m = re.match(r"([a-g])(ss|ff|s|f)?([',]*)", tok)
    st = STEP[m.group(1)]; acc = {'s': 1, 'f': -1, 'ss': 2, 'ff': -2, None: 0}[m.group(2)]
    rs, ro = v.ref; o = ro; d = st - rs
    if d > 3: o -= 1
    if d < -3: o += 1
    o += m.group(3).count("'") - m.group(3).count(",")
    v.ref = (st, o)
    SPELL[12 * (o + 1) + SEMI[st] + acc, id(v)] = (o * 7 + st, acc)
    return 12 * (o + 1) + SEMI[st] + acc, (st, o)

def emit(v, midis, d, scale, grace):
    if grace: return
    real = d * scale * 8
    new_tied = {}
    for m in midis:
        if v.tie and m in v.tied:
            v.tied[m][1] += real; new_tied[m] = v.tied[m]
        else:
            n = [v.t, real, m, v.staff, SPELL[m, id(v)]]; v.notes.append(n); new_tied[m] = n
    v.tied = new_tied; v.tie = False; v.t += real

def run(v, toks, i, end_tok, scale, grace):
    """Parse sequential music until end_tok; returns index after it."""
    while i < len(toks):
        tk = toks[i]
        if tk == end_tok: return i + 1
        if tk == '\\cu': v.staff = 'u'; i += 1; continue
        if tk == '\\cl': v.staff = 'l'; i += 1; continue
        if tk in ('\\acciaccatura', '\\grace', '\\appoggiatura'):
            if toks[i + 1] == '{': i = run(v, toks, i + 2, '}', scale, True)
            else: i = one(v, toks, i + 1, scale, True)
            continue
        if tk.startswith('\\clef'): EVENTS.append([float(v.t * 1), 'clef', v.staff, tk.split()[1]]); i += 1; continue
        if tk.startswith('\\ottava'): EVENTS.append([float(v.t * 1), 'ott', v.staff, int(re.search(r'-?\d+', tk).group())]); i += 1; continue
        if tk.startswith('\\tuplet'):
            n, d = map(int, re.search(r'(\d+)/(\d+)', tk).groups())
            assert toks[i + 1] == '{'
            i = run(v, toks, i + 2, '}', scale * F(d, n), grace); continue
        if tk.startswith('\\'): i += 1; continue
        if tk == '~': v.tie = True; i += 1; continue
        if tk == '{': i = run(v, toks, i + 1, '}', scale, grace); continue
        if tk == '<<':
            t0 = v.t; tmax = t0; i += 1
            while toks[i] != '>>':
                v.t = t0
                if toks[i] == '{': i = run(v, toks, i + 1, '}', scale, grace)
                elif toks[i].startswith('\\'): i += 1; continue
                else: i = one(v, toks, i, scale, grace)
                tmax = max(tmax, v.t)
            v.t = tmax; i += 1; continue
        i = one(v, toks, i, scale, grace)
    return i

def one(v, toks, i, scale, grace):
    tk = toks[i]
    if tk == '<':
        chord = []; first = None; i += 1
        while toks[i] != '>':
            if re.match(r'[a-g]', toks[i]):
                m, r = pitch(v, toks[i]); chord.append(m)
                if first is None: first = r
            i += 1
        i += 1
        if i < len(toks) and re.fullmatch(DUR, toks[i]): G['dur'] = dur_of(toks[i]); i += 1
        v.ref = first
        emit(v, chord, G['dur'], scale, grace); return i
    if re.match(r'[a-g]', tk):
        m, _ = pitch(v, tk)
        d = dur_of(tk)
        if d is None and i + 1 < len(toks) and re.fullmatch(DUR, toks[i + 1]): d = dur_of(toks[i + 1]); i += 1
        if d is not None: G['dur'] = d
        emit(v, [m], G['dur'], scale, grace); return i + 1
    if tk[0] in 'rs':
        d = dur_of(tk)
        if d is not None: G['dur'] = d
        if not grace: v.t += G['dur'] * scale * 8; v.tie = False
        return i + 1
    return i + 1

voices = {n: Voice(n) for n in VOICES}
bar_len = {n: [] for n in VOICES}
pos = 0
while True:
    s = src.find('\\parallelMusic', pos)
    if s < 0: break
    a = src.index('{', src.index('\n', s)); depth = 0; k = a
    while True:
        if src[k] == '{': depth += 1
        elif src[k] == '}':
            depth -= 1
            if depth == 0: break
        k += 1
    body = src[a + 1:k]; pos = k
    tail = src[k:k + 400]
    for n in VOICES:
        m = re.search(n + r"\s*=.*?\\relative\s+c([',]*)", tail)
        voices[n].ref = (0, 3 + m.group(1).count("'") - m.group(1).count(","))
    toks = TOK.findall(clean(body))
    bars, cur = [], []
    for tk in toks:
        if tk == '|': bars.append(cur); cur = []
        else: cur.append(tk)
    assert not [x for x in cur if not x.startswith('\\')], cur
    assert len(bars) % 4 == 0, len(bars)
    for bi, bt in enumerate(bars):
        v = voices[VOICES[bi % 4]]; t0 = v.t
        run(v, bt, 0, None, F(1), False)
        bar_len[v.name].append(v.t - t0)

nb = len(bar_len['rhUp']); print('bars', nb)
bad = [(n, i + 1, float(l)) for n in VOICES for i, l in enumerate(bar_len[n]) if l != 9]
print('bad bars', bad)
notes = []
for v in voices.values():
    for t, d, m, st, sp in v.notes: notes.append([float(t), float(d), m, st, v.name, sp[0], sp[1]])
notes.sort()
EVENTS.sort()
print(EVENTS)
json.dump({'bars': nb, 'notes': notes, 'events': EVENTS}, open(sys.argv[2], 'w'))
print('notes', len(notes), 'range', min(n[2] for n in notes), max(n[2] for n in notes))
