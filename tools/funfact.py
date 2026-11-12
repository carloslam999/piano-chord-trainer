# exec'd at the end of scrub.py: one fun fact per piece, shown once when you reach the end of the piece,
# and any time from a small "♪ Fun fact" pill next to the badges.

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

body = body.replace('<div class="badges" id="songBadges"></div>',
    '<div class="badges" id="songBadges"></div>\n    <div class="fact-toast" id="factToast" role="status" aria-live="polite" hidden><button class="fact-x" id="factX" type="button" aria-label="Close fun fact">×</button><b id="factHead">♪ Fun fact</b><p id="factText"></p></div>', 1)
assert 'id="factToast"' in body

css += '''
.badges .factbtn { font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; background: var(--sun); color: #14151C; border-color: #14151C; }
.badges .factbtn:hover { transform: translate(-1px, -1px); box-shadow: 2px 2px 0 var(--shadow-ink); }
.fact-toast { position: fixed; right: 20px; bottom: 20px; z-index: 50; max-width: 340px; background: var(--surface); color: var(--ink); border: 2px solid var(--edge); border-radius: 14px;
  box-shadow: 4px 4px 0 var(--sun); padding: 12px 36px 12px 14px; font-size: 14px; line-height: 1.45; animation: factIn .35s ease-out; }
.fact-toast b { display: block; font-family: var(--font-display); font-size: 15px; margin-bottom: 3px; }
.fact-toast p { margin: 0; }
.fact-x { position: absolute; top: 6px; right: 8px; border: 0; background: none; color: var(--muted); font-size: 20px; line-height: 1; cursor: pointer; padding: 2px 4px; }
@keyframes factIn { from { transform: translateY(16px); opacity: 0; } to { transform: none; opacity: 1; } }
@media (max-width: 600px) { .fact-toast { left: 16px; right: 16px; bottom: 16px; max-width: none; } }
@media (prefers-reduced-motion: reduce) { .fact-toast { animation: none; } }
'''

a_ = '{ pause(); setPos(0); }'
assert js.count(a_) == 1
js = js.replace(a_, "{ pause(); setPos(0); window.dispatchEvent(new Event('pieceend')); }", 1)
js += r'''
/* ---------- fun fact: once when you reach the end, and any time from the ♪ pill ---------- */
if (D.fact) {
  const toast = $('factToast'), KEY = 'pct-fact-' + location.pathname.split('/').pop();
  let hideT = null;
  const show = (head, auto) => {
    $('factHead').textContent = head; $('factText').textContent = D.fact; toast.hidden = false;
    clearTimeout(hideT); if (auto) hideT = setTimeout(() => { toast.hidden = true; }, 12000);
  };
  $('factX').onclick = () => { toast.hidden = true; clearTimeout(hideT); };
  const pill = document.createElement('button');
  pill.type = 'button'; pill.className = 'factbtn'; pill.textContent = '♪ Fun fact';
  pill.onclick = () => toast.hidden ? show('♪ Fun fact', false) : (toast.hidden = true);
  const addPill = () => { const b = $('songBadges'); if (b && !b.contains(pill)) b.appendChild(pill); };
  addPill(); setTimeout(addPill, 0);
  addEventListener('pieceend', () => {
    let seen = false; try { seen = localStorage.getItem(KEY) === '1'; localStorage.setItem(KEY, '1'); } catch (e) {}
    if (!seen) show('🎹 You reached the end! Fun fact:', true);
  });
}
'''
