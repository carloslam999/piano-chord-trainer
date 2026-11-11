# exec'd by build_site.py after SONGS is defined: generalise the player for any time signature,
# add the imported pieces, and attach library metadata (difficulty, era, mood, length) to every song.

# ---------- player: beats of any length (BL eighth notes per beat) ----------
JS_PATCHES = [
    ('BARLEN = BEATS * 3;', 'BL = D.bl || 3, BARLEN = BEATS * BL, BEAMLEN = D.beam || BL;'),
    ('Math.ceil((rel + 0.01) / 3) * 3 - rel', 'Math.ceil((rel + 0.01) / BL) * BL - rel'),
    ("c.d < 3 ||", "c.d < Math.min(BL, 3) ||"),
    ("""      for (let e = c.t; e < c.t + c.d - 1e-6; e += 1) {
        const k = Math.round(e - b.start) % 3, rest = c.t + c.d - e;
        if (k === 0) accEvents.push({ t: e, d: 1, m: bass, vel: 0.2, bus: 'acc', sd: Math.min(rest, 3), bass: true });
        else upper.forEach(m => accEvents.push({ t: e, d: 1, m, vel: 0.095, bus: 'acc', sd: Math.min(rest, 2) }));""",
     """      const step = BL === 3 ? 1 : BL, bassUnit = BL === 3 ? 3 : (BEATS === 4 ? 2 * BL : BARLEN);
      for (let e = c.t; e < c.t + c.d - 1e-6; e += step) {
        const k = Math.round(e - b.start) % bassUnit, rest = c.t + c.d - e;
        if (k === 0) accEvents.push({ t: e, d: step, m: bass, vel: 0.2, bus: 'acc', sd: Math.min(rest, bassUnit), bass: true });
        else upper.forEach(m => accEvents.push({ t: e, d: step, m, vel: 0.095, bus: 'acc', sd: Math.min(rest, Math.max(2, step)) }));"""),
    ("const sub = ['', '-and', '-a'];", "const sub = BL === 3 ? ['', '-and', '-a'] : BL === 2 ? ['', '-and'] : BL === 4 ? ['', '-e', '-and', '-a'] : [''];"),
    ("beat ${Math.floor(e / 3) + 1}${sub[e % 3]}", "beat ${Math.floor(e / BL) + 1}${sub[e % BL] || ''}"),
    ("for (let k = 0; k < 3; k++)", "for (let k = 0; k < BL; k++)"),
    ("for (let e = 0; e <= b.len; e += 3) {", "for (let e = 0; e <= b.len; e += BL) {"),
    ("Math.floor((p.t - PICK) / 3 + 1e-6) === Math.floor((g.t - PICK) / 3 + 1e-6)", "Math.floor((p.t - PICK) / BEAMLEN + 1e-6) === Math.floor((g.t - PICK) / BEAMLEN + 1e-6)"),
    ("const nf = g.d <= 0.75 + 1e-6 ? 2 : 1,", "const nf = SH(g.d) ? 2 : 1,"),
    ("const g = b.gs[i]; if (g.d > 0.75 + 1e-6) continue;", "const g = b.gs[i]; if (!SH(g.d)) continue;"),
    ("if (nx && nx.d <= 0.75 + 1e-6) seg(g.t, nx.t, 1);", "if (nx && SH(nx.d)) seg(g.t, nx.t, 1);"),
    ("else if (!pv || pv.d > 0.75 + 1e-6) {", "else if (!pv || !SH(pv.d)) {"),
    ("const LO = D.lo, HI = 100,", "const LO = D.lo, HI = D.hi || 100,"),
    ("/* ---------- sheet music", "const SH = d => d <= 0.76 && Math.abs(d - 2 / 3) > 0.03;   // shorter than an eighth (but not a triplet eighth)\n/* ---------- sheet music"),
]
for a, b in JS_PATCHES:
    n = js.count(a)
    assert n >= 1, ('player patch not found', a[:60])
    js = js.replace(a, b)
js = js.replace("c.className = 'chip' + (d < 3 ? ' tiny' : '');", "c.className = 'chip' + (d < Math.min(BL, 3) ? ' tiny' : '');")
js = js.replace("      if (d < 3) {", "      if (d < Math.min(BL, 3)) {")
js = js.replace("const beat = Math.floor(off / 3 + 1e-6);", "const beat = Math.floor(off / BL + 1e-6);")
js = js.replace("st.style.flex = '3 1 0';", "st.style.flex = BL + ' 1 0';")
assert '% 3' not in js and "'3 1 0'" not in js, 'leftover 3-eighth assumption'

# ---------- imported pieces ----------
IMP = f'{SP}/imported'
GLOSSARY = '''<dt>C</dt><dd>A plain letter is a major chord: root, major third, fifth (C – E – G).</dd>
        <dt>Am</dt><dd>“m” is a minor chord: the middle note is a half step lower (A – C – E).</dd>
        <dt>G7</dt><dd>A dominant seventh: major chord plus a minor seventh. It wants to resolve, usually down a fifth (G7 → C).</dd>
        <dt>Cmaj7, Am7</dt><dd>Major seventh and minor seventh chords: a soft, open sound. Satie uses them a lot.</dd>
        <dt>C/E</dt><dd>A slash chord: play C with E as the lowest note. The letter after the slash is the bass.</dd>
        <dt>B°, Bm7♭5, B°7</dt><dd>Diminished and half-diminished chords: tense, passing colours.</dd>
        <dt>Csus4</dt><dd>The third is replaced by the fourth, which then usually resolves.</dd>
        <dt>I, V⁷, ii</dt><dd>Roman numerals count chords from the home key. Upper case is major, lower case is minor.</dd>'''

PIECES = [
    dict(id='gymnopedie-1', title='Gymnopédie No. 1', titleHtml='Gymnopédie <em>No. 1</em>', composer='Erik Satie', eyebrow='Erik Satie · Trois Gymnopédies, 1888',
         tempo='Lent et douloureux', difficulty=1, era='Belle Époque', mood='Calm', minutes=3.5, key='major', defaultStyle='block',
         blurb='Two chords rocking back and forth, Gmaj7 and Dmaj7, under a slow, floating tune. The friendliest way into chord playing.',
         tips=['<b>Start with bars 1–4.</b> Just Gmaj7 then Dmaj7, one per bar. Play the bass note on beat 1 and the chord on beat 2.',
               '<b>Add the melody from bar 5.</b> It is slow and mostly long notes, so there is time to look at the keys.',
               '<b>Bars 17–39 visit new chords</b> (F♯m, Bm, Em, D7) before the opening returns. Loop them four bars at a time.',
               '<b>Keep it soft and even.</b> The marking means “slow and painful”: let every chord ring.']),
    dict(id='gnossienne-1', title='Gnossienne No. 1', titleHtml='Gnossienne <em>No. 1</em>', composer='Erik Satie', eyebrow='Erik Satie · Gnossiennes, 1890',
         tempo='Lent', difficulty=2, era='Belle Époque', mood='Dreamy', minutes=3.5, defaultStyle='block',
         blurb='Hypnotic and a little strange: almost the whole piece sits on F minor, with B♭m6 for colour. The challenge is the winding melody.',
         tips=['<b>The left hand is easy.</b> Mostly F minor, sometimes B♭m6. Loop bars 17–24 to feel the change.',
               '<b>The melody is the work.</b> Slow the speed right down and loop two bars at a time. Watch the gold notes.',
               '<b>Satie wrote no bar lines.</b> This version counts four beats per bar so you can find your place.']),
    dict(id='fur-elise', title='Für Elise', titleHtml='Für <em>Elise</em>', composer='Ludwig van Beethoven', eyebrow='Ludwig van Beethoven · Bagatelle WoO 59, 1810',
         tempo='Poco moto', difficulty=2, era='Classical', mood='Playful', minutes=3, defaultStyle='block',
         symmap={'Emaj7/D♯': ('E', 'V')},
         blurb='The tune everyone knows. The famous opening uses just A minor and E, so you can play the first page within an evening.',
         tips=['<b>Bars 1–8 are the famous part.</b> The left hand only alternates A minor and E. Loop them first.',
               '<b>The E–D♯ wiggle is melody alone.</b> Keep the left hand quiet there and let the right hand lead.',
               '<b>The middle sections change mood.</b> First a brighter part in C and F, later a stormy part over a repeated A. Learn them one section at a time.',
               '<b>The time is 3/8:</b> three quick counts per bar. Count “1-2-3” lightly, feeling one pulse per bar.']),
    dict(id='moonlight-sonata-1', src='moonlight-1', title='Moonlight Sonata, 1st movement', titleHtml='Moonlight Sonata, <em>1st movement</em>', composer='Ludwig van Beethoven',
         eyebrow='Ludwig van Beethoven · Sonata Op. 27 No. 2, 1801', tempo='Adagio sostenuto', difficulty=2, era='Classical', mood='Melancholy', minutes=6, key='minor', defaultStyle='orig',
         leftHandName="Beethoven's left hand",
         blurb='Slow rolling triplets and a quiet melody on top. Every bar is a chord broken into three notes, which makes it ideal for chord thinking.',
         tips=['<b>Each bar is a chord, played as a rolling triplet.</b> Name the chord, then find its three notes in the right hand.',
               '<b>Bars 1–5 are the heart of it:</b> C♯m, C♯m7/B, F♯m/A, G♯. Loop them until the shapes feel automatic.',
               '<b>The melody enters in bar 5.</b> Play it with the top fingers of the right hand, a little louder than the triplets.',
               '<b>Use the pedal on every chord change.</b> Beethoven asks for a dreamy, blurred sound.']),
    dict(id='bach-prelude-in-c', src='bach-prelude-c', title='Prelude in C major', titleHtml='Prelude in <em>C major</em>', composer='Johann Sebastian Bach',
         eyebrow='J. S. Bach · Well-Tempered Clavier I, BWV 846, 1722', tempo='Moderato', difficulty=1, era='Baroque', mood='Calm', minutes=2.5, defaultStyle='orig',
         leftHandName="Bach's left hand",
         blurb='One chord per bar, broken into the same pattern every time. If you can play chords, this is the perfect first classical piece.',
         tips=['<b>Every bar is one chord, broken into a pattern.</b> Find the chord first (block chords), then play it note by note.',
               '<b>The pattern never changes:</b> two low notes, then the top three notes twice.',
               '<b>Watch the bass line.</b> It walks down slowly (C, B, A…), which is what gives the piece its pull.',
               '<b>Near the end the bass stays on G</b> while the chords above get tense; then everything settles on C.']),
    dict(id='chopin-prelude-e-minor', title='Prelude in E minor, Op. 28 No. 4', titleHtml='Prelude in <em>E minor</em>', composer='Frédéric Chopin',
         eyebrow='Frédéric Chopin · 24 Preludes, Op. 28, 1839', tempo='Largo', difficulty=2, era='Romantic', mood='Melancholy', minutes=2, defaultStyle='orig',
         leftHandName="Chopin's left hand",
         blurb='A sad, simple melody over left-hand chords that slide down a half step at a time. Short, slow and unforgettable.',
         tips=['<b>The left hand is the piece.</b> Repeated chords where one note at a time slides down a half step. Play them with “Chopin’s left hand”.',
               '<b>The chord names change fast</b> because of those slides. Think of them as one slow descent rather than many chords.',
               '<b>The melody barely moves</b>, mostly B and C. Keep it singing and slightly louder.',
               '<b>Bars 16–18 are the climax.</b> Then the music quietens and ends on E minor.']),
    dict(id='traumerei', title='Träumerei', titleHtml='<em>Träumerei</em>', composer='Robert Schumann', eyebrow='Robert Schumann · Scenes from Childhood, Op. 15 No. 7, 1838',
         tempo='Langsam', difficulty=2, era='Romantic', mood='Dreamy', minutes=2.5, defaultStyle='block',
         blurb='“Dreaming”: a gentle tune that rises again and again, over warm chords in F major. Short and very rewarding.',
         tips=['<b>The opening phrase comes back several times.</b> Learn bars 1–4 well and you know a large part of the piece.',
               '<b>The tune often hands over between voices.</b> Listen for the melody, even when it moves to the middle of the texture.',
               '<b>Chords change often here,</b> sometimes twice a bar. Use Block chords and a slow speed to hear each one.']),
    dict(id='old-french-song', title='Old French Song', titleHtml='Old French <em>Song</em>', composer='Pyotr Ilyich Tchaikovsky', eyebrow='Tchaikovsky · Album for the Young, Op. 39 No. 16, 1878',
         tempo='Moderato', difficulty=1, era='Romantic', mood='Melancholy', minutes=1.5, defaultStyle='block',
         blurb='A short, songlike piece written for children. Mostly G minor and C minor: a great first “real” piece in a minor key.',
         tips=['<b>Two chords do most of the work:</b> G minor and C minor, with D7 leading home.',
               '<b>The melody is a simple song.</b> Sing it, then play it over block chords.',
               '<b>The second half repeats the first</b> with a short excursion in the middle. Loop that middle part (bars 17–24) separately.']),
]
for P in PIECES:
    src = P.get('src', P['id'])
    imp = json.load(open(f'{IMP}/{src}.json'))
    ly = open(f'{SP}/scores/{src}.ly', encoding='utf-8', errors='replace').read()
    hdr = lambda k: (re.search(k + r'\s*=\s*"([^"]*)"', ly) or [None, ''])[1]
    lic = hdr('license') or hdr('copyright') or 'Public Domain'
    D = imp['data']; CH = imp['chords']
    for b in D['bars']:   # piece-specific corrections
        for c in b['chords']:
            if c[0] in P.get('symmap', {}): c[0], c[1] = P['symmap'][c[0]]
    for sym in {c[0] for b in D['bars'] for c in b['chords']}:
        base = sym.split('/')[0]
        if base not in CH:   # a plain triad added by a correction
            from_imp = {'E': ['E', 'G♯', 'B']}
            CH[base] = from_imp[base]
    # sections: 8-bar groups (4 for very short pieces), described by the chords they use
    nb = len(D['bars']); size = 8 if nb > 20 else 4
    secs, n = [], 1
    while n <= nb:
        to = min(nb, n + size - 1)
        if nb - to < size // 2: to = nb
        seen = []
        for b in D['bars'][n - 1:to]:
            for c in b['chords']:
                if c[0] not in seen: seen.append(c[0])
        what = 'Chords: ' + ', '.join(seen[:7]) + (' and more.' if len(seen) > 7 else '.')
        secs.append({'id': str(len(secs) + 1), 'from': n, 'to': to, 'what': what})
        n = to + 1
    num, den = imp['time'].split('/')
    feel = {'3/4': 'three beats', '3/8': 'three quick counts', '2/4': 'two beats', '4/4': 'four beats', '2/2': 'two half-note beats'}[imp['time']]
    count = {'3/4': 'three beats, each a quarter note (count “1-and, 2-and, 3-and”)', '3/8': 'three quick counts, one per eighth note',
             '2/4': 'two beats, each a quarter note (count “1-and, 2-and”)', '4/4': 'four beats, each a quarter note (count “1-and, 2-and…”)',
             '2/2': 'two beats, each a half note (count “1-e-and-a, 2-e-and-a”)'}[imp['time']]
    texts = dict(eyebrow=P['eyebrow'], title=P['titleHtml'],
                 meta=f'<span><b>Key</b> {imp["key"]}</span><span><b>Time</b> {imp["time"]}, {feel}</span><span><b>{P["tempo"]}</b></span><span><b>Length</b> {nb} bars</span>',
                 practice=''.join(f'<li>{t}</li>' for t in P['tips']), glossary=GLOSSARY,
                 credits=f'Notes come from the {hdr("source")} edition as typeset by the <a href="https://www.mutopiaproject.org" target="_blank" rel="noopener">Mutopia Project</a> ({hdr("maintainer")}, {lic}), with grace notes left out and repeats written out. '
                         'The chord names were worked out automatically from the notes and spot-checked, so a few bars may simplify the harmony. Sound is a synthesised piano made in your browser.')
    SONGS.append(dict(id=P['id'], file=P['id'] + '.html', title=P['title'], short=P['title'], composer=P['composer'], facts=[imp['key'], imp['time'], f'{nb} bars'],
                      blurb=P['blurb'], texts=texts, data=D, chords=json.dumps(CH, ensure_ascii=False), sections=json.dumps(secs, ensure_ascii=False),
                      leftHand=P.get('leftHandName', 'Original left hand'), defaultStyle=P['defaultStyle'], countText=count,
                      desc=f"Play-along chord trainer for {P['composer']}'s {P['title']}.", lib=P))

LIB = {   # library metadata for the two hand-made pieces
    'nocturne-op9-no2': dict(difficulty=3, era='Romantic', mood='Dreamy', minutes=4.5),
    'clair-de-lune': dict(difficulty=3, era='Belle Époque', mood='Dreamy', minutes=5),
}
for s in SONGS:
    if 'lib' not in s: s['lib'] = LIB[s['id']]

exec(open(f'{SP}/theme.py').read())
