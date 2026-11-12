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
    dict(id='field-nocturne-5', title='Nocturne No. 5 in B♭ major', titleHtml='Nocturne No. 5 in <em>B♭ major</em>', composer='John Field',
         eyebrow='John Field · Nocturne No. 5, H. 37, 1817', tempo='Andante, cantabile', difficulty=2, era='Romantic', mood='Dreamy', minutes=4, defaultStyle='orig',
         leftHandName="Field's left hand",
         blurb='Field invented the nocturne, and Chopin learned from him. A gentle singing tune over a rocking 12/8 left hand, mostly in B♭.',
         tips=['<b>Start with bars 1–4.</b> B♭ with a passing diminished chord in each bar: the same rocking shape comes back throughout.',
               '<b>The left hand is the nocturne pattern:</b> a low bass note, then the chord spread upwards. Listen to it with “Field’s left hand”.',
               '<b>Bars 14–17 move fast,</b> one chord per beat. Loop them slowly with Block chords before adding the melody.',
               '<b>Let the melody sing.</b> The marking is “cantabile”: play the gold notes a little louder than the accompaniment.']),
    dict(id='the-entertainer', src='entertainer', title='The Entertainer', titleHtml='The <em>Entertainer</em>', composer='Scott Joplin',
         eyebrow='Scott Joplin · A Ragtime Two-Step, 1902', tempo='Not fast', difficulty=2, era='Ragtime', mood='Playful', minutes=4, defaultStyle='orig',
         leftHandName="Joplin's left hand",
         blurb='The ragtime hit everyone knows. A bouncing “oom-pah” left hand under a cheeky, syncopated tune, mostly on C, F and G7.',
         tips=['<b>Bars 1–4 are the famous intro run</b> in octaves, with no real chords. Learn it slowly as a melody.',
               '<b>The left hand is ragtime stride:</b> a low bass note on the beat, then a chord on the off-beat. Loop one bar with “Joplin’s left hand” to hear the bounce.',
               '<b>The main tune (from bar 5) uses C, C7, F and G7.</b> Get those four chords comfortable first.',
               '<b>Joplin wrote “Not fast”.</b> Keep it relaxed and steady; the syncopation does the work.']),
    dict(id='rondo-alla-turca', title='Rondo alla Turca', titleHtml='Rondo <em>alla Turca</em>', composer='Wolfgang Amadeus Mozart',
         eyebrow='W. A. Mozart · Piano Sonata K. 331, 3rd movement, 1783', tempo='Allegretto', difficulty=2, era='Classical', mood='Playful', minutes=3.5, defaultStyle='orig',
         leftHandName="Mozart's left hand",
         blurb='The “Turkish March”: quick, bright and famous. It moves between A minor and a stomping A major chorus with spread chords in the left hand.',
         tips=['<b>The opening (bars 1–8) is A minor, then E minor.</b> Loop it at a slow speed; the right hand runs in quick, even notes.',
               '<b>The A major chorus (from bar 25) is the “march”.</b> The left hand plays fast spread chords on A and E: practise them as block chords first.',
               '<b>The piece keeps coming back to the same sections.</b> Learn each one once and you know most of it.',
               '<b>Speed comes last.</b> It is marked Allegretto, which is lively but not frantic.']),
    dict(id='mozart-sonata-k545', src='mozart-k545-1', title='Sonata in C, K. 545, 1st movement', titleHtml='Sonata in C, <em>K. 545</em>', composer='Wolfgang Amadeus Mozart',
         eyebrow='W. A. Mozart · Piano Sonata No. 16, K. 545, 1788', tempo='Allegro', difficulty=2, era='Classical', mood='Playful', minutes=4, defaultStyle='orig',
         leftHandName="Mozart's left hand",
         blurb='Mozart called it a sonata “for beginners”. Clear chords in an Alberti bass (low, high, middle, high) under a famous singing tune and lots of scales.',
         tips=['<b>Bars 1–4 are C, G7, F and back to C.</b> The left hand breaks each chord into the Alberti pattern: low, high, middle, high.',
               '<b>Bars 5–12 are scales over simple chords.</b> Loop two bars at a time and keep the scales even.',
               '<b>The middle section moves through minor keys</b> (G minor, D minor, A minor). Use Block chords to hear each change.',
               '<b>The repeats are written out,</b> so the piece is longer here than it looks in the score.']),
    dict(id='arabesque-1', title='Arabesque No. 1', titleHtml='Arabesque <em>No. 1</em>', composer='Claude Debussy',
         eyebrow='Claude Debussy · Deux Arabesques, 1891', tempo='Andantino con moto', difficulty=3, era='Belle Époque', mood='Dreamy', minutes=4.5, defaultStyle='orig',
         leftHandName="Debussy's left hand",
         blurb='Flowing triplet waves passed between the hands, with soft seventh chords in E major. A favourite for players moving towards Debussy.',
         tips=['<b>Both hands share the triplet waves.</b> Learn each hand alone at a slow speed before putting them together.',
               '<b>Watch for two against three:</b> the melody often moves in pairs while the accompaniment moves in threes. Loop one bar slowly.',
               '<b>The chords are gentle sevenths</b> (F♯m7, C♯m7, B7). Play them as Block chords first to hear the colours.',
               '<b>The middle section changes key</b> (to A major, then briefly C major) before returning to E major.']),
    dict(id='chopin-prelude-a-major', title='Prelude in A major, Op. 28 No. 7', titleHtml='Prelude in <em>A major</em>', composer='Frédéric Chopin',
         eyebrow='Frédéric Chopin · 24 Preludes, Op. 28, 1839', tempo='Andantino', difficulty=1, era='Romantic', mood='Calm', minutes=1, defaultStyle='orig',
         leftHandName="Chopin's left hand",
         blurb='Just 16 bars, like a little mazurka. Almost all of it is E7 and A, so you can play the whole piece in a day.',
         tips=['<b>Two chords do almost everything:</b> E7 and A, swapping every two bars.',
               '<b>Bar 12 has the one surprise,</b> a big F♯7 chord leading to B minor. Practise that bar on its own.',
               '<b>The rhythm repeats every two bars:</b> a dotted note, a short note, then a long chord.',
               '<b>Play it softly and slowly.</b> It is over in under a minute.']),
    dict(id='bach-minuet-g-minor', title='Minuet in G minor, BWV Anh. 115', titleHtml='Minuet in <em>G minor</em>', composer='Johann Sebastian Bach',
         eyebrow='Anna Magdalena Bach Notebook, BWV Anh. 115, 1725 · now credited to Christian Petzold', tempo='Moderato', difficulty=1, era='Baroque', mood='Melancholy', minutes=2, defaultStyle='orig',
         leftHandName='Original left hand', repeatsOut=False, startTempo=140,
         blurb='The darker twin of the famous Minuet in G major, from the same notebook. One melody line over a walking bass, so it is a perfect first Baroque piece.',
         symmap={'Am': ('A°', 'ii°'), 'Am/C': ('A°/C', 'ii°⁶'), 'Cm7/G': ('Gm', 'i'), 'G7/B': ('G7/B', 'V⁷/iv'), 'F7/C': ('F7/C', 'V⁷/III'),
                 'C7/G': ('C7/G', 'V⁷/VII'), 'G/B': ('G/B', 'V/iv')},
         addChords={'A°': ['A', 'C', 'E♭']},
         tips=['<b>The left hand mostly plays one note at a time,</b> walking down step by step (G, F, E♭, D) in the opening bars. Learn that bass line first.',
               '<b>Two halves of 16 bars, each played twice.</b> The first half stays in G minor; the second visits B♭ major before coming home.',
               '<b>Bars 13 to 16 are a sequence:</b> G7 then F7, the same shape one step lower, landing on B♭.',
               '<b>Keep it in three:</b> a minuet is a dance, so lean a little on beat 1 of every bar.']),
    dict(id='bach-minuet-g-major', title='Minuet in G major, BWV Anh. 114', titleHtml='Minuet in <em>G major</em>', composer='Johann Sebastian Bach',
         eyebrow='Anna Magdalena Bach Notebook, BWV Anh. 114, 1725 · now credited to Christian Petzold', tempo='Moderato', difficulty=1, era='Baroque', mood='Playful', minutes=2, defaultStyle='orig',
         leftHandName='Original left hand', repeatsOut=False, startTempo=140,
         blurb='Probably the most-learned beginner piece of all. A bright tune over a simple bass line, and only a handful of chords: G, C, D7 and Am.',
         symmap={'Gmaj7/D': ('G/D', 'I⁶₄'), 'Bm7': ('G/B', 'I⁶'), 'Cmaj7': ('C', 'IV'), 'Am7': ('Am', 'ii'), 'C♯m': ('A/C♯', 'V⁶/V'),
                 'F♯m': ('D/F♯', 'V⁶'), 'Gmaj7': ('G', 'I')},
         tips=['<b>Start with the left hand alone.</b> It is a single note at a time, mostly half notes then quarter notes.',
               '<b>Bars 1 to 8 use just G, C and D.</b> Get those three shapes under your fingers first.',
               '<b>The second half (bar 17) moves to D major,</b> with A and A7 chords, then comes home to G.',
               '<b>Count three in every bar</b> and keep the quarter notes even, like a gentle dance.']),
    dict(id='canon-in-d', title='Canon in D', titleHtml='Canon in <em>D</em>', composer='Johann Pachelbel',
         eyebrow='Johann Pachelbel · Canon and Gigue in D major, c. 1700', tempo='Andante', difficulty=1, era='Baroque', mood='Calm', minutes=3, defaultStyle='orig',
         leftHandName='Ground bass with chords', repeatsOut=False, startTempo=100,
         blurb='Eight chords, repeated all the way through: D, A, Bm, F♯m, G, D, G, A. Learn them once and you can play the whole piece while the melody grows on top.',
         symmap={'Bm7/D': ('D', 'I'), 'Em7/G': ('G', 'IV'), 'F♯m7/A': ('A', 'V'), 'A7': ('A', 'V'), 'Bm7': ('Bm', 'vi')},
         credits='The melody is the violin line typeset by the <a href="https://www.mutopiaproject.org" target="_blank" rel="noopener">Mutopia Project</a> from Jim Paterson’s arrangement (mfiles.co.uk, Creative Commons Attribution 3.0). '
                 'The left hand is Pachelbel’s ground bass with a simple chord above it, added here for piano, plus a closing D major chord. Sound is a synthesised piano made in your browser.',
         tips=['<b>The whole piece is one 8-chord loop:</b> D A | Bm F♯m | G D | G A. Each chord lasts two beats.',
               '<b>Learn the bass line first:</b> it steps down D, A, B, F♯, G, D, G, A. Your hand barely moves.',
               '<b>Use the Repeat setting on bars 1 to 2</b> until the loop is automatic, then add the melody.',
               '<b>The melody gets busier as it goes</b> (half notes, then quarters, then eighths), but the chords never change.']),
    dict(id='chopin-waltz-b-minor', title='Waltz in B minor, Op. 69 No. 2', titleHtml='Waltz in <em>B minor</em>', composer='Frédéric Chopin',
         eyebrow='Frédéric Chopin · Waltz Op. 69 No. 2, written 1829, published 1855', tempo='Moderato', difficulty=2, era='Romantic', mood='Melancholy', minutes=4, defaultStyle='orig',
         leftHandName="Chopin's left hand", startTempo=150,
         blurb='A favourite first Chopin waltz: a sad, singing tune over the classic oom-pah-pah left hand, with a warm B major middle section.',
         tips=['<b>The left hand is always bass, chord, chord.</b> Practise jumping from the low note to the chord without looking.',
               '<b>Bars 1 to 16 are mostly Bm and F♯7,</b> with a B°7 colour in bar 6. That is most of the piece.',
               '<b>The middle section (bar 65) switches to B major</b> and swings between B and F♯7.',
               '<b>Let the melody breathe:</b> waltzes like this are played with a little give in the timing.']),
    dict(id='mountain-king', title='In the Hall of the Mountain King', titleHtml='In the Hall of the <em>Mountain King</em>', composer='Edvard Grieg',
         eyebrow='Edvard Grieg · Peer Gynt Suite No. 1, Op. 46 No. 4, 1875 (piano version)', tempo='Alla marcia e molto marcato', difficulty=2, era='Romantic', mood='Playful', minutes=3, defaultStyle='orig',
         leftHandName="Grieg's left hand", startTempo=130,
         blurb='The famous creeping tune that gets louder and faster until it explodes. One short melody repeated over and over, so it is quicker to learn than it sounds.',
         symmap={'B♭/D': ('D+', 'III+'), 'Bsus4': ('Bm', 'i')},
         tips=['<b>Learn the 2-bar tune first:</b> B C♯ D E F♯ D F♯. Almost the whole piece is that tune, moved around.',
               '<b>The left hand marches B, F♯, B, F♯</b> under the melody. Keep it short and detached.',
               '<b>From bar 10 the tune moves up to F♯</b>, with a spooky D augmented chord (D+) in between.',
               '<b>Start slowly and speed up</b> each time you play it, just like the piece does.']),
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
            from_imp = {'E': ['E', 'G♯', 'B'], **P.get('addChords', {})}
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
    feel = {'3/4': 'three beats', '3/8': 'three quick counts', '2/4': 'two beats', '4/4': 'four beats', '2/2': 'two half-note beats', '12/8': 'four beats of three', '6/8': 'two beats of three', '9/8': 'three beats of three'}[imp['time']]
    count = {'3/4': 'three beats, each a quarter note (count “1-and, 2-and, 3-and”)', '3/8': 'three quick counts, one per eighth note',
             '2/4': 'two beats, each a quarter note (count “1-and, 2-and”)', '4/4': 'four beats, each a quarter note (count “1-and, 2-and…”)',
             '2/2': 'two beats, each a half note (count “1-e-and-a, 2-e-and-a”)', '12/8': 'four beats, each three eighth notes long (count “1-and-a, 2-and-a…”)', '6/8': 'two beats, each three eighth notes long (count “1-and-a, 2-and-a”)', '9/8': 'three beats, each three eighth notes long (count “1-and-a, 2-and-a, 3-and-a”)'}[imp['time']]
    texts = dict(eyebrow=P['eyebrow'], title=P['titleHtml'],
                 meta=f'<span><b>Key</b> {imp["key"]}</span><span><b>Time</b> {imp["time"]}, {feel}</span><span><b>{P["tempo"]}</b></span><span><b>Length</b> {nb} bars</span>',
                 practice=''.join(f'<li>{t}</li>' for t in P['tips']), glossary=GLOSSARY,
                 credits=P.get('credits') or f'Notes come from the {re.sub(r"^[Tt]he ", "", hdr("source"))} edition as typeset by the <a href="https://www.mutopiaproject.org" target="_blank" rel="noopener">Mutopia Project</a> ({hdr("maintainer")}, {lic}), with grace notes left out' + (' and repeats written out' if P.get('repeatsOut', True) else '') + '. '
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
