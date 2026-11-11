"""Parse the Mutopia Nocturne Op.9 No.2 source with the Clair de Lune parser's machinery."""
import re, json, sys
from fractions import Fraction as F
lib = open(sys.argv[3]).read().split("voices = {n: Voice(n)")[0]
exec(lib)          # defines TOK, Voice, run, one, pitch, emit, G, EVENTS, SPELL (reads sys.argv[1] as src)

def strip_markup(t):
    out, i = [], 0
    while True:
        j = t.find('\\markup', i)
        if j < 0: out.append(t[i:]); break
        out.append(t[i:j]); k = j + 7
        while k < len(t) and t[k] in ' \t\n': k += 1
        if k < len(t) and t[k] == '{':
            depth = 0
            while k < len(t):
                if t[k] == '{': depth += 1
                elif t[k] == '}':
                    depth -= 1
                    if depth == 0: k += 1; break
                k += 1
        i = k
    return ''.join(out)

def nclean(t):
    t = re.sub(r'%[^\n]*', ' ', t); t = re.sub(r'\\tuplet(Up|Down|Neutral)', ' ', t)
    t = strip_markup(t)
    t = re.sub(r"(\\once\s+)?\\override\s+[\w.]+\s+#'[\w-]+\s*=\s*(#'\([^)]*\)|##[tf]|#\"[^\"]*\"|#[-\d.]+)", ' ', t)
    t = re.sub(r'\\set\s+\w+\s*=\s*#\d+', ' ', t)
    t = re.sub(r'#\(set-octavation\s+(\d)\)', r' \\ottava #\1 ', t)
    t = re.sub(r'#\([^)]*\)', ' ', t)
    t = re.sub(r'\\(tempo|partial)\s+\S+', ' ', t)
    t = re.sub(r'\\time\s+\d+/\d+', ' ', t)
    t = re.sub(r'\\key\s+\w+\s+\\\w+', ' ', t)
    t = re.sub(r'"[^"]*"', ' ', t)
    t = re.sub(r'\\times\s+(\d+)/(\d+)', r'\\tuplet \2/\1', t)
    t = re.sub(r'[-_^]\d+', ' ', t)
    t = re.sub(r'[-_^][.>|^+_\-]', ' ', t)
    t = re.sub(r'\\[<>!()]', ' ', t)
    t = re.sub(r'[\[\]()]', ' ', t)
    return t

def block(a, b):
    s = src.index(a); s = src.index('{', s) + 1
    return src[s:src.index(b, s)]

out = []
for name, a, b, ref in (('upper', 'upper = \\relative', 'lower = \\relative', (0, 5)), ('lower', 'lower = \\relative', '\\score', (0, 3))):
    v = Voice('rh' if name == 'upper' else 'lh'); v.ref = ref
    toks = [t for t in TOK.findall(nclean(block(a, b))) if t != '|']
    run(v, toks, 0, None, F(1), False)
    print(name, 'total', float(v.t), 'notes', len(v.notes))
    for t, d, m, st, sp in v.notes: out.append([float(t), float(d), m, st, 'rhUp' if name == 'upper' else 'lhUp', sp[0], sp[1]])
out.sort(); EVENTS.sort(); print(EVENTS)
json.dump({'notes': out, 'events': EVENTS}, open(sys.argv[2], 'w'))
