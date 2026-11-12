# exec'd at the end of scrub.py: one fun fact per piece, on a sticky note that floats in the header next to the title.
# Tap the note to flip it open. Reaching the end of the piece flips it open once, with a little burst of notes.

FACTS = {
    'nocturne-op9-no2': 'Chopin wrote this nocturne at about 20 and dedicated the set to Marie Pleyel, wife of the Paris piano maker Camille Pleyel, whose pianos Chopin loved.',
    'clair-de-lune': 'The title comes from a poem by Paul Verlaine. Debussy first called the piece “Promenade sentimentale”, and it was published 15 years after he began the suite.',
    'gymnopedie-1': 'Satie took the name from the Gymnopaedia, a festival in ancient Sparta where young men danced unclothed. Nobody knows exactly why he chose it.',
    'gnossienne-1': 'Satie invented the word “gnossienne”. The score has no bar lines and odd instructions instead of tempo marks, like “très luisant” (very shiny) and “questionnez” (question).',
    'fur-elise': 'Für Elise was only published about 40 years after Beethoven died, and the manuscript is now lost. Nobody knows who Elise was; one theory is that “Therese” was misread.',
    'moonlight-sonata-1': 'Beethoven never called it “Moonlight”. The nickname came from the critic Ludwig Rellstab after Beethoven’s death, who said it reminded him of moonlight on Lake Lucerne.',
    'bach-prelude-in-c': 'About 130 years after Bach wrote it, Charles Gounod wrote a new melody over this prelude. The result became the famous “Ave Maria” by Bach and Gounod.',
    'chopin-prelude-e-minor': 'This prelude was played on the organ at Chopin’s own funeral in Paris in 1849.',
    'traumerei': 'Träumerei means “dreaming”. Vladimir Horowitz loved it as an encore and played it at his famous 1986 return concert in Moscow.',
    'old-french-song': 'Tchaikovsky wrote Album for the Young for his nephew Volodya, following the example of Schumann’s own Album for the Young.',
    'field-nocturne-5': 'The Irish composer John Field invented the piano nocturne. Chopin took up the idea about 15 years later and made it famous.',
    'the-entertainer': 'The Entertainer was published in 1902, and Joplin died in 1917 without seeing ragtime’s revival. It became a hit again in 1973 thanks to the film The Sting.',
    'rondo-alla-turca': 'It imitates the Turkish Janissary bands that were all the rage in Mozart’s Vienna. Some pianos of the time even had a “Turkish” pedal that rang bells and hit a drum.',
    'mozart-sonata-k545': 'Mozart listed this sonata in his own catalogue as “for beginners”. It is still one of the first sonatas piano students learn.',
    'arabesque-1': 'Debussy wrote the two Arabesques in his twenties. They are among his earliest piano pieces, written before his style became famous.',
    'chopin-prelude-a-major': 'In Japan this prelude is famous as the long-running TV jingle for Ohta’s Isan, a stomach medicine.',
    'bach-minuet-g-minor': 'This minuet and the Minuet in G major sit side by side in Anna Magdalena Bach’s notebook. In the 1970s scholars found that both were written by Christian Petzold, not Bach.',
    'bach-minuet-g-major': 'Its melody became the 1965 pop hit “A Lover’s Concerto” by the girl group The Toys.',
    'canon-in-d': 'The Canon was almost forgotten for nearly 300 years until a 1968 recording made it a hit. Today it is one of the most-played pieces at weddings.',
    'chopin-waltz-b-minor': 'Chopin asked for his unpublished music to be destroyed after his death. His friend Julian Fontana published it anyway, including this waltz, in 1855.',
    'mountain-king': 'Grieg wrote it for Ibsen’s play Peer Gynt, and he was not a fan. In an 1874 letter he said he could not bear to listen to it because it reeked of “cow pies”, Norwegian nationalism and trollish self-satisfaction.',
}
for s in SONGS:
    assert s['id'] in FACTS, ('no fun fact for', s['id'])
    s['data']['fact'] = FACTS[s['id']]

_head = '''<header class="top">
    <div class="eyebrow" id="songEyebrow"></div>
    <h1 id="songTitle"></h1>
    <div class="meta" id="songMeta"></div>
    <div class="badges" id="songBadges"></div>
  </header>'''
assert body.count(_head) == 1, 'song header markup changed'
body = body.replace(_head, '''<header class="top">
    <div class="top-main">
      <div class="eyebrow" id="songEyebrow"></div>
      <h1 id="songTitle"></h1>
      <div class="meta" id="songMeta"></div>
      <div class="badges" id="songBadges"></div>
    </div>
    <aside class="fact-note" id="factNote" aria-label="Fun fact" hidden>
      <span class="fn-drift" aria-hidden="true"><i>♪</i><i>♫</i><i>♪</i></span>
      <button class="fn-card" id="factCard" type="button" aria-expanded="false">
        <span class="fn-front"><span class="fn-mascot" aria-hidden="true">♫</span><span class="fn-txt"><b>Psst! Did you know…?</b><small>Tap for a fun fact about this piece</small></span></span>
        <span class="fn-back" aria-live="polite"><b id="factHead">🎵 Fun fact</b><span id="factText"></span><small>Tap to fold it away</small></span>
      </button>
    </aside>
  </header>''', 1)

css += '''
/* ---------- fun fact sticky note, floating next to the title ---------- */
.top-main { display: grid; gap: 4px; min-width: 0; }
.fact-note { position: relative; margin-top: 6px; }
.fn-card { position: relative; display: block; width: 100%; text-align: left; font: inherit; cursor: pointer;
  background: var(--sun); color: #14151C; border: 2px solid #14151C; border-radius: 4px 14px 14px 14px;
  box-shadow: 4px 4px 0 var(--shadow-ink); padding: 14px 16px 12px; transform: rotate(-1.2deg);
  transition: transform .18s ease, box-shadow .18s ease; }
.fn-card::before { content: ""; position: absolute; top: -11px; left: 50%; width: 74px; height: 20px; transform: translateX(-50%) rotate(3deg);
  background: rgba(255,255,255,.6); border: 1px solid rgba(20,21,28,.18); }
.fn-card:hover { transform: rotate(0deg) translate(-2px, -2px); box-shadow: 6px 6px 0 var(--shadow-ink); }
.fn-card:focus-visible { outline: 3px solid var(--cobalt); outline-offset: 3px; }
.fn-front { display: flex; align-items: center; gap: 12px; }
.fn-mascot { flex: none; display: grid; place-items: center; width: 42px; height: 42px; border-radius: 50%; background: var(--cobalt); color: #fff;
  border: 2px solid #14151C; font-size: 22px; animation: fnWiggle 3.2s ease-in-out infinite; }
.fn-txt b, .fn-back b { display: block; font-family: var(--font-display); font-size: 16px; font-weight: 800; letter-spacing: -.01em; }
.fn-txt small, .fn-back small { display: block; font-size: 12px; font-weight: 600; opacity: .7; margin-top: 2px; }
.fn-back { display: none; font-size: 14px; line-height: 1.45; }
.fn-back b { margin-bottom: 4px; }
.fn-back small { margin-top: 6px; }
.fact-note.open .fn-front { display: none; }
.fact-note.open .fn-back { display: block; }
.fact-note.open .fn-card { background: var(--surface); color: var(--ink); border-color: var(--edge); box-shadow: 4px 4px 0 var(--sun); }
.fact-note.open .fn-card::before { background: rgba(255,200,58,.75); }
.fn-card.flip { animation: fnFlip .32s ease-in-out; }
.fn-drift { position: absolute; right: 18px; top: -6px; width: 60px; height: 0; pointer-events: none; }
.fn-drift i { position: absolute; bottom: 0; font-style: normal; font-size: 16px; color: var(--cobalt); opacity: 0; animation: fnDrift 6s ease-in infinite; }
.fn-drift i:nth-child(2) { left: 22px; animation-delay: 2s; font-size: 19px; color: var(--coral); }
.fn-drift i:nth-child(3) { left: 44px; animation-delay: 4s; color: var(--mint); }
.fn-burst { position: absolute; left: 50%; top: 50%; font-style: normal; font-size: 20px; pointer-events: none; z-index: 5; animation: fnBurst 1.1s ease-out forwards; }
@keyframes fnWiggle { 0%, 70%, 100% { transform: rotate(0); } 76% { transform: rotate(-14deg); } 84% { transform: rotate(12deg); } 92% { transform: rotate(-6deg); } }
@keyframes fnDrift { 0% { transform: translateY(0) rotate(0); opacity: 0; } 15% { opacity: .75; } 100% { transform: translateY(-46px) rotate(18deg); opacity: 0; } }
@keyframes fnFlip { 0% { transform: rotate(-1.2deg) scaleX(1); } 50% { transform: rotate(0) scaleX(0); } 100% { transform: rotate(-1.2deg) scaleX(1); } }
@keyframes fnBurst { from { transform: translate(-50%, -50%) scale(.6); opacity: 1; } to { transform: translate(calc(-50% + var(--dx)), calc(-50% + var(--dy))) scale(1.2) rotate(var(--r)); opacity: 0; } }
@keyframes fnPop { 0% { transform: rotate(-1.2deg) scale(1); } 40% { transform: rotate(2deg) scale(1.06); } 100% { transform: rotate(-1.2deg) scale(1); } }
.fn-card.pop { animation: fnPop .6s ease-out; }
/* open note: compact text and a corner × instead of a "fold away" line, so it stays about as tall as the title block */
.fact-note.open .fn-card { padding: 9px 30px 9px 14px; }
.fact-note.open .fn-card::after { content: "×"; position: absolute; top: 3px; right: 9px; font-size: 19px; line-height: 1; color: var(--muted); }
.fn-back { font-size: 13px; line-height: 1.4; }
.fn-back b { font-size: 14px; margin-bottom: 2px; }
.fn-back small { display: none; }
/* computer: the note floats beside the title and never changes the header's height */
@media (min-width: 900px) {
  .top { position: relative; padding-right: 440px; }
  .fact-note { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); width: 400px; margin: 0; }
}
/* phone: the closed note keeps its place; the open note drops down over the player like a pop-up */
@media (max-width: 899px) { .fn-drift { display: none; } .fact-note { margin-top: 12px; } .fn-card { transform: rotate(-.6deg); padding: 9px 12px 8px; }
  .fn-mascot { width: 32px; height: 32px; font-size: 17px; } .fn-front { gap: 10px; } .fn-txt b { font-size: 15px; } .fn-txt small { margin-top: 0; }
  .fact-note.open { z-index: 30; }
  .fact-note.open .fn-card { position: absolute; top: 0; left: 0; right: 0; width: auto; z-index: 30; box-shadow: 4px 4px 0 var(--sun), 0 10px 30px rgba(20,21,28,.25); } }
@media (prefers-reduced-motion: reduce) { .fn-mascot, .fn-drift i, .fn-card.flip, .fn-card.pop, .fn-burst { animation: none; } .fn-burst { display: none; } .fn-card { transition: none; } }
'''

a_ = '{ pause(); setPos(0); }'
assert js.count(a_) == 1
js = js.replace(a_, "{ pause(); setPos(0); window.dispatchEvent(new Event('pieceend')); }", 1)
js += r'''
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
'''
