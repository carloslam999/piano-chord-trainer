# Mutopia's Canon in D is the violin tune alone. Add Pachelbel's ground bass (D A Bm F#m G D G A, a half note each)
# with a simple triad above it as the left hand, plus a closing D major bar, and write a two-hand MIDI file.
import sys, struct
sys.argv = [sys.argv[0]]; exec(open('import_midi.py').read().split('def main():')[0])
div, notes, meta = read_midi('scores/canon-in-d-violin.mid')
mel = sorted((a, b, p) for a, b, p, t in notes)
E = div // 2                                     # ticks per eighth
GROUND = [(50, [54, 57, 62]), (45, [52, 57, 61]), (47, [54, 59, 62]), (42, [54, 57, 61]),
          (43, [55, 59, 62]), (38, [54, 57, 62]), (43, [55, 59, 62]), (45, [52, 57, 61])]
end = max(b for a, b, p in mel); bars = -(-end // (8 * E))
lh = []
for h in range(bars * 2):
    bass, tri = GROUND[h % 8]
    for p in [bass] + tri: lh.append((h * 4 * E, (h + 1) * 4 * E - 10, p))
t0 = bars * 8 * E
mel.append((t0, t0 + 8 * E - 10, 62))
for p in [38, 54, 57, 62]: lh.append((t0, t0 + 8 * E - 10, p))
def vlq(v):
    out = [v & 0x7F]; v >>= 7
    while v: out.append((v & 0x7F) | 0x80); v >>= 7
    return bytes(reversed(out))
def track(evs):
    evs.sort(); out, last = b'', 0
    for t, msg in evs: out += vlq(t - last) + msg; last = t
    out += vlq(0) + b'\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(out)) + out
def notes_trk(ns, ch, name):
    ev = [(0, b'\xff\x03' + vlq(len(name)) + name.encode())]
    for a, b, p in ns: ev += [(a, bytes([0x90 | ch, p, 80])), (b, bytes([0x80 | ch, p, 0]))]
    return track(ev)
head = track([(0, b'\xff\x58\x04\x04\x02\x18\x08'), (0, b'\xff\x59\x02\x02\x00'), (0, b'\xff\x51\x03\x07\xa1\x20')])
open('scores/canon-in-d.mid', 'wb').write(b'MThd' + struct.pack('>IHHH', 6, 1, 3, div) + head + notes_trk(mel, 0, 'Melody') + notes_trk(lh, 1, 'Bass'))
print('bars', bars + 1, 'melody', len(mel), 'left hand', len(lh))
