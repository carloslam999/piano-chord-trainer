"""Import a piano piece from a Mutopia MIDI file (+ its .ly for the pickup length).

Produces the song data the trainer needs: notes for each hand, note spellings for the
sheet music, clef changes, bars, and a suggested chord for each bar / half bar / beat.

usage: import_midi.py <file.mid> <file.ly> <out.json> [--show]
"""
import json, re, struct, sys
from collections import defaultdict

# ---------------------------------------------------------------- MIDI reading
def read_midi(path):
    data = open(path, 'rb').read()
    assert data[:4] == b'MThd'
    fmt, ntrk, div = struct.unpack('>HHH', data[8:14])
    pos, tracks = 14, []
    for _ in range(ntrk):
        assert data[pos:pos + 4] == b'MTrk', 'bad track'
        ln = struct.unpack('>I', data[pos + 4:pos + 8])[0]
        tracks.append(data[pos + 8:pos + 8 + ln]); pos += 8 + ln
    notes, meta = [], {'time': [], 'key': [], 'names': {}}
    for ti, tr in enumerate(tracks):
        i, tick, status, on = 0, 0, None, {}
        def vlq():
            nonlocal i
            v = 0
            while True:
                b = tr[i]; i += 1; v = (v << 7) | (b & 0x7F)
                if not b & 0x80: return v
        while i < len(tr):
            tick += vlq()
            b = tr[i]
            if b == 0xFF:
                typ = tr[i + 1]; i += 2; ln = vlq(); body = tr[i:i + ln]; i += ln
                if typ == 0x58: meta['time'].append((tick, body[0], 2 ** body[1]))
                elif typ == 0x59: meta['key'].append((tick, struct.unpack('b', body[:1])[0], body[1]))
                elif typ == 0x03: meta['names'][ti] = body.decode('latin1')
                continue
            if b in (0xF0, 0xF7):
                i += 1; ln = vlq(); i += ln; continue
            if b & 0x80: status = b; i += 1
            hi = status & 0xF0
            if hi in (0x80, 0x90):
                pitch, vel = tr[i], tr[i + 1]; i += 2
                key = (pitch, status & 0x0F)
                if hi == 0x90 and vel > 0:
                    if key in on: notes.append((on[key], tick, pitch, ti))   # retrigger: close previous
                    on[key] = tick
                elif key in on:
                    notes.append((on.pop(key), tick, pitch, ti))
            elif hi in (0xA0, 0xB0, 0xE0): i += 2
            elif hi in (0xC0, 0xD0): i += 1
    return div, notes, meta

# ---------------------------------------------------------------- pitch spelling
LETTERS = 'CDEFGAB'
LPC = [0, 2, 4, 5, 7, 9, 11]
SHARP_ORDER, FLAT_ORDER = 'FCGDAEB', 'BEADGCF'
ACC_TXT = {-2: '♭♭', -1: '♭', 0: '', 1: '♯', 2: '×'}

def key_letters(sf):
    acc = [0] * 7
    if sf > 0:
        for L in SHARP_ORDER[:sf]: acc[LETTERS.index(L)] = 1
    else:
        for L in FLAT_ORDER[:-sf]: acc[LETTERS.index(L)] = -1
    return acc

def tonic_of(sf, minor):
    # major tonic walks the circle of fifths from C; minor is a minor third below
    pc = (sf * 7) % 12
    if minor: pc = (pc - 3) % 12
    # letter: for sharps/flats pick the spelling used by that key
    major_names = {0: 'C', 1: 'G', 2: 'D', 3: 'A', 4: 'E', 5: 'B', 6: 'F♯', 7: 'C♯', -1: 'F', -2: 'B♭', -3: 'E♭', -4: 'A♭', -5: 'D♭', -6: 'G♭', -7: 'C♭'}
    minor_names = {0: 'A', 1: 'E', 2: 'B', 3: 'F♯', 4: 'C♯', 5: 'G♯', 6: 'D♯', 7: 'A♯', -1: 'D', -2: 'G', -3: 'C', -4: 'F', -5: 'B♭', -6: 'E♭', -7: 'A♭'}
    name = (minor_names if minor else major_names)[sf]
    return pc, LETTERS.index(name[0]), name

def spell_pc(pc, sf, minor):
    """Return (letter_index, accidental) for a pitch class in this key."""
    acc = key_letters(sf)
    for li in range(7):
        if (LPC[li] + acc[li]) % 12 == pc: return li, acc[li]
    t_pc, t_li, _ = tonic_of(sf, minor)
    if minor:   # raised 6th and 7th of the minor scale are spelled as sharps of their letters
        for deg in (5, 6):
            li = (t_li + deg) % 7
            if (LPC[li] + acc[li] + 1) % 12 == pc: return li, acc[li] + 1
    for li in range(7):
        if LPC[li] == pc and acc[li] != 0 and (sf >= 0) == (acc[li] > 0): return li, 0
    rel = (pc - t_pc) % 12
    if rel in (1, 3, 8, 10):          # flat-side chromatic notes: ♭2, ♭3, ♭6, ♭7
        for li in range(7):
            if (LPC[li] + acc[li] - 1) % 12 == pc and acc[li] - 1 >= -1: return li, acc[li] - 1
    if sf >= 0 or rel == 6:
        for li in range(7):
            if (LPC[li] + acc[li] + 1) % 12 == pc and acc[li] + 1 <= 1: return li, acc[li] + 1
    for li in range(7):
        if (LPC[li] + acc[li] - 1) % 12 == pc and acc[li] - 1 >= -1: return li, acc[li] - 1
    for li in range(7):
        if (LPC[li] + 1) % 12 == pc: return li, 1
    raise ValueError(pc)

def spell_midi(m, sf, minor):
    li, a = spell_pc(m % 12, sf, minor)
    octave = (m - a - LPC[li]) // 12 - 1
    return octave * 7 + li, a

def name_of(li, a): return LETTERS[li] + ACC_TXT[a]

# ---------------------------------------------------------------- chords
TEMPLATES = [   # (suffix, intervals, roman suffix, quality for case)
    ('', (0, 4, 7), '', 'M'), ('m', (0, 3, 7), '', 'm'), ('°', (0, 3, 6), '°', 'm'), ('+', (0, 4, 8), '+', 'M'),
    ('7', (0, 4, 7, 10), '⁷', 'M'), ('maj7', (0, 4, 7, 11), 'maj⁷', 'M'), ('m7', (0, 3, 7, 10), '⁷', 'm'),
    ('m7♭5', (0, 3, 6, 10), 'ø⁷', 'm'), ('°7', (0, 3, 6, 9), '°⁷', 'm'), ('sus4', (0, 5, 7), 'sus', 'M'),
    ('7sus', (0, 5, 7, 10), '⁷sus', 'M'),
]
STEP_OF = {0: 0, 3: 2, 4: 2, 5: 3, 6: 4, 7: 4, 8: 4, 9: 5, 10: 6, 11: 6}   # dim 7th written as a sixth (C°7 = C E♭ G♭ A)   # letters above root per interval

def chord_tones(root_li, root_a, ivs):
    out = []
    rpc = (LPC[root_li] + root_a) % 12
    for iv in ivs:
        li = (root_li + STEP_OF[iv]) % 7
        a = ((rpc + iv) - LPC[li] + 6) % 12 - 6
        out.append(name_of(li, a))
    return out

def fit(weights, bass_pc, key_pcs):
    total = sum(weights.values()) or 1
    best = None
    for root in range(12):
        for suf, ivs, rsuf, q in TEMPLATES:
            pcs = {(root + iv) % 12 for iv in ivs}
            inside = sum(w for p, w in weights.items() if p in pcs)
            outside = total - inside
            mx = max(weights.values())
            missing = sum(1 for iv in ivs if weights.get((root + iv) % 12, 0) < 0.08 * mx)
            score = inside - 0.75 * outside - 0.22 * mx * missing
            if len(ivs) == 4:
                score -= 0.08 * total                               # prefer the simpler triad
                if weights.get((root + ivs[3]) % 12, 0) < 0.2 * mx: score -= 0.12 * total   # a passing 7th is not a 7th chord
            if weights.get(root, 0) < 0.12 * mx: score -= 0.15 * total                  # the root should really sound
            if suf == '+': score -= 0.28 * total
            if suf == '°': score -= 0.14 * total
            if suf in ('sus4', '7sus'): score -= 0.22 * total
            if suf == 'maj7':
                score -= 0.12 * total
                if (root + 11) % 12 not in key_pcs: score -= 0.4 * total   # a dominant chord is never maj7
            if suf == '°' and weights.get((root - 4) % 12, 0) >= 0.1 * mx: score -= 0.15 * total   # it is really a dominant 7th
            if bass_pc == root: score += 0.10 * total
            elif bass_pc is not None and bass_pc in pcs: score += 0.06 * total
            if root in key_pcs: score += 0.04 * total
            if pcs <= key_pcs: score += 0.07 * total                    # all notes belong to the key
            if best is None or score > best[0]: best = (score, root, suf, ivs, rsuf, q, inside / total)
    return best

def weights_in(notes, a, b):
    w = defaultdict(float); low = None
    for t, d, m, st in notes:
        ov = min(b, t + d) - max(a, t)
        if ov <= 1e-6: continue
        w[m % 12] += ov * (1.6 if st == 'l' else 1.0)
        if t <= a + 0.5 and (low is None or m < low): low = m
    if low is None and w:
        low = min(m for t, d, m, st in notes if min(b, t + d) - max(a, t) > 1e-6)
    return w, (low % 12 if low is not None else None)

def detect(notes, bar_start, bar_len, beat_len, key):
    sf, minor = key
    t_pc, t_li, _ = tonic_of(sf, minor)
    scale = [0, 2, 3, 5, 7, 8, 10, 11] if minor else [0, 2, 4, 5, 7, 9, 11]
    key_pcs = {(t_pc + s) % 12 for s in scale}
    nbeats = round(bar_len / beat_len)
    cands = [[(0, bar_len)]]
    if nbeats % 2 == 0 and nbeats >= 2: cands.append([(0, bar_len / 2), (bar_len / 2, bar_len)])
    if nbeats >= 3 and beat_len >= 2: cands.append([(i * beat_len, (i + 1) * beat_len) for i in range(nbeats)])
    best = None
    for segs in cands:
        total, chords = 0, []
        for a, b in segs:
            w, bass = weights_in(notes, bar_start + a, bar_start + b)
            if not w: chords.append(None); continue
            f = fit(w, bass, key_pcs); total += f[0] / (sum(w.values()) or 1) * (b - a) / bar_len
            chords.append((a, b - a, f, bass))
        total -= 0.10 * (len(segs) - 1)
        if best is None or total > best[0]: best = (total, chords)
    out = []
    for c in best[1]:
        if c is None: continue
        a, d, f, bass = c
        out.append([a, d, f, bass])
    return out

def chord_label(f, bass, key):
    sf, minor = key
    score, root, suf, ivs, rsuf, q, frac = f
    if suf == 'm7♭5' and bass == (root + 3) % 12:
        root, suf, ivs, rsuf, q = bass, 'm6', (0, 3, 7, 9), '⁶', 'm'
    li, a = spell_pc(root, sf, minor)
    # pick the root spelling whose chord tones need the fewest accidentals (B♯maj7 -> Cmaj7)
    def cost(cl, ca):
        try: t = chord_tones(cl, ca, ivs if suf != 'm6' else (0, 3, 7))
        except KeyError: return 99
        n = sum(len(x) - 1 for x in t) + 4 * sum(1 for x in t if '×' in x or '♭♭' in x)
        return n + (0 if (cl, ca) == (li, a) else 2.5)
    alts = [(cl, ca) for cl in range(7) for ca in (-1, 0, 1) if (LPC[cl] + ca) % 12 == root]
    li, a = min(alts, key=lambda x: cost(*x))
    sym = name_of(li, a) + suf
    tones = chord_tones(li, a, ivs) if suf != 'm6' else chord_tones(li, a, (0, 3, 7)) + [name_of((li + 5) % 7, ((LPC[li] + a + 9) - LPC[(li + 5) % 7] + 6) % 12 - 6)]
    if bass is not None and bass != root and bass in {(root + iv) % 12 for iv in ivs}:
        bi = [((LPC[x] + 0) % 12) for x in range(7)]
        sym += '/' + tones[[(root + iv) % 12 for iv in ivs].index(bass)]
    # roman numeral relative to the tonic
    t_pc, t_li, _ = tonic_of(sf, minor)
    deg = (li - t_li) % 7
    scale = [0, 2, 3, 5, 7, 8, 10] if minor else [0, 2, 4, 5, 7, 9, 11]
    diff = ((root - t_pc) - scale[deg] + 6) % 12 - 6
    if minor and deg == 6 and diff == 1: diff = 0                 # raised 7th (leading tone) in minor
    if minor and deg == 5 and diff == 1: diff = 0
    rn = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][deg]
    if q == 'm': rn = rn.lower()
    rn = {-1: '♭', 1: '♯', 0: ''}.get(diff, '') + rn + rsuf
    return sym, rn, name_of(li, a) + suf, tones, frac

# ---------------------------------------------------------------- main
def main():
    mid, ly, out = sys.argv[1:4]
    kov = next((a.split('=')[1] for a in sys.argv if a.startswith('--key=')), None)
    show = '--show' in sys.argv
    div, raw, meta = read_midi(mid)
    lysrc = open(ly, encoding='utf-8', errors='replace').read()
    m = re.search(r'\\partial\s*(\d+)(\.?)', lysrc)
    pickup = 0.0
    if m:
        pickup = 8 / int(m.group(1)) * (1.5 if m.group(2) else 1)
    e8 = div / 2   # ticks per eighth note
    q = lambda tk: round(tk / e8 * 24) / 24
    notes = [(q(a), q(b) - q(a), p, ti) for a, b, p, ti in raw if q(b) - q(a) >= 0.15]
    # hands: tracks with mostly high notes are the right hand
    by_tr = defaultdict(list)
    for t, d, p, ti in notes: by_tr[ti].append(p)
    upper_tracks = {ti for ti, ps in by_tr.items() if sum(ps) / len(ps) >= 60}
    if len(by_tr) == 2:   # two staves: the higher one is the right hand, even if both sit high
        upper_tracks = {max(by_tr, key=lambda ti: sum(by_tr[ti]) / len(by_tr[ti]))}
    if len(by_tr) == 1 or not upper_tracks or len(upper_tracks) == len(by_tr):
        split = lambda p, ti: 'u' if p >= 60 else 'l'
    else:
        split = lambda p, ti: 'u' if ti in upper_tracks else 'l'
    hn = sorted((t, d, p, split(p, ti)) for t, d, p, ti in notes)
    num, den = meta['time'][0][1:] if meta['time'] else (4, 4)
    bar_len = num * 8 / den
    compound = den == 8 and num % 3 == 0 and num > 3
    beat_len = 3 if compound else (1 if den == 8 else 8 / den)
    beam = 3 if (den == 8 and num == 3) else (2 if den == 2 else beat_len)
    beats = round(bar_len / beat_len)
    sf, mi = (meta['key'][0][1], meta['key'][0][2]) if meta['key'] else (0, 0)
    key = (sf, bool(mi))
    if kov: key = (sf, kov == 'minor')
    end = max(t + d for t, d, p, st in hn)
    # key changes (the first key may be overridden: --key=major/minor)
    kev = []
    for tk, s, m_ in sorted(meta['key']):
        k = (s, bool(m_))
        if not kev: k = key
        if not kev or kev[-1][1] != k: kev.append((q(tk), k))
    if not kev: kev = [(0, key)]
    key_at = lambda t: [k for kt, k in kev if kt <= t + 1e-6][-1]
    # time-signature changes give bars of different lengths
    tev = sorted({(q(tk), n_, d_) for tk, n_, d_ in meta['time']}) or [(0, num, den)]
    bar_at = lambda t: [n_ * 8 / d_ for tt, n_, d_ in tev if tt <= t + 1e-6][-1]
    starts, pos = [], pickup
    while pos < end - 1e-6:
        starts.append((pos, bar_at(pos))); pos += bar_at(pos)
    bars, CH = [], {}
    for start, ln in starts:
        key = key_at(start)
        has_lh = any(st == 'l' and min(start + ln, t + d) - max(start, t) > 1e-6 for t, d, p, st in hn)
        if not has_lh and bars:   # melody alone: keep the chord that is already sounding
            last = bars[-1]['chords'][-1]
            bars.append({'n': len(bars) + 1, 'start': start, 'len': ln, 'chords': [[last[0], last[1], 0, ln]]}); continue
        cs = detect(hn, start, ln, beat_len, key)
        chords = []
        for a, d, f, bass in cs:
            sym, rn, base, tones, frac = chord_label(f, bass, key)
            CH[base] = tones
            if chords and chords[-1][0] == sym: chords[-1][3] += d; continue
            chords.append([sym, rn, a, d])
        if not chords: chords = [[bars[-1]['chords'][-1][0], bars[-1]['chords'][-1][1], 0, ln]] if bars else [['N.C.', '', 0, ln]]
        # stretch so the bar is fully covered
        for i, c in enumerate(chords):
            c[3] = (chords[i + 1][2] if i + 1 < len(chords) else ln) - c[2]
        bars.append({'n': len(bars) + 1, 'start': start, 'len': ln, 'chords': chords})
    for b in bars:
        for c in b['chords']:
            c[2] = round(c[2], 3); c[3] = round(c[3], 3)
    # sheet: spellings, voices, clef changes for the left hand
    sh = []
    key = kev[0][1]
    for t, d, p, st in hn:
        ds, a = spell_midi(p, *key_at(t))
        sh.append([t, round(d, 3), 0 if st == 'u' else 1, ds, a, 0 if st == 'u' else 2, p])
    clefs, cur = [], 'F'
    for b in bars:
        ps = sorted(p for t, d, p, st in hn if st == 'l' and b['start'] <= t < b['start'] + b['len'])
        if not ps: continue
        med = ps[len(ps) // 2]
        want = 'G' if (cur == 'F' and med >= 60) or (cur == 'G' and med >= 55) else 'F'
        if want != cur: clefs.append([b['start'], 1, want]); cur = want
    cur = 'G'   # right hand: switch to bass clef only for passages that sit well below middle C
    for b in bars:
        ps = sorted(p for t, d, p, st in hn if st == 'u' and b['start'] <= t < b['start'] + b['len'])
        if not ps: continue
        med = ps[len(ps) // 2]
        want = 'F' if (cur == 'G' and med < 50) or (cur == 'F' and med < 57) else 'G'
        if want != cur: clefs.append([b['start'], 0, want]); cur = want
    clefs.sort()
    keys = [list(k) for k in sorted({(round(q(tk)), s_) for tk, s_, _ in meta['key']})] or [[0, 0]]
    keys = [k for i, k in enumerate(keys) if i == 0 or k[1] != keys[i - 1][1]]
    keys[0][0] = 0
    group = lambda st: [[t, d, sorted(ms)] for (t, d), ms in sorted(_grp(st).items())]
    def _grp(st):
        g = defaultdict(list)
        for t, d, p, s in hn:
            if s == st: g[(t, round(d, 3))].append(p)
        return g
    hi = min(108, max(p for t, d, p, st in hn) + 2)
    hi += {1: 1, 3: 1, 6: 1, 8: 1, 10: 1}.get(hi % 12, 0)
    lo = max(21, min(p for t, d, p, st in hn) - 2)
    lo -= {1: 1, 3: 1, 6: 1, 8: 1, 10: 1}.get(lo % 12, 0)
    data = dict(bars=bars, rh=group('u'), lh=group('l'), end=round(end, 3), pickup=pickup, cadenza=0,
                beats=beats, bl=beat_len, beam=beam, lo=lo, hi=max(hi, 100), clef0=['G', 'F'], sh=sh, clefs=clefs, otts=[], keys=keys)
    tonic = tonic_of(*key)[2] + (' minor' if key[1] else ' major')
    json.dump({'data': data, 'chords': CH, 'key': tonic, 'time': f'{num}/{den}', 'bars': len(bars), 'tracks': {str(k): v for k, v in meta['names'].items()}}, open(out, 'w'), ensure_ascii=False)
    print(f'{mid.split("/")[-1]}: {tonic}, {num}/{den}, pickup {pickup}, {len(bars)} bars, {len(hn)} notes, tracks {len(by_tr)} upper={sorted(upper_tracks)}, time sigs {len(meta["time"])}, keys {meta["key"]}')
    if show:
        for b in bars:
            print(f"  {b['n']:3d}", '  '.join(f"{c[0]}({c[1]}){'' if c[3] == b['len'] else ':' + str(c[3])}" for c in b['chords']))

if __name__ == '__main__':
    main()
