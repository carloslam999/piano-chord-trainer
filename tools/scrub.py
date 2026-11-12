# exec'd at the end of theme.py: drag / swipe / tap / wheel on the sheet music to move through the piece.

old_note = '<span class="fold-note">simplified: no rests or ties</span>'
assert old_note in body
body = body.replace(old_note, '<span class="fold-note">Drag to move · tap to jump · simplified score</span>', 1)
body = body.replace('<canvas id="sheet" aria-label="Scrolling sheet music"></canvas>',
                    '<canvas id="sheet" aria-label="Scrolling sheet music. Drag sideways to move, tap to jump to a bar."></canvas><div class="scrub-tip" id="scrubTip" hidden></div>', 1)
assert 'id="scrubTip"' in body

css += '''
#foldSheet { position: relative; }
#sheet { cursor: grab; touch-action: pan-y; user-select: none; -webkit-user-select: none; }
#sheet.dragging { cursor: grabbing; }
.scrub-tip { position: absolute; top: 44px; transform: translateX(-50%); background: var(--ink); color: var(--bg); font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; pointer-events: none; white-space: nowrap; box-shadow: 2px 2px 0 var(--sun); }
'''

js += r'''
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
'''

# ---------- sound on iPhones with the silent switch on ----------
exec(open(f'{SP}/ios_audio.py').read())
_a = '  ac = new (window.AudioContext || window.webkitAudioContext)();'
assert _a in js and js.count('initAudio(); ac.resume();') >= 3
js = js.replace(_a, "  try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}\n" + _a, 1)
js = js.replace('initAudio(); ac.resume();', 'initAudio(); iosAudioUnlock(); ac.resume();')
js = js.replace('/* ---------- audio ---------- */', '/* ---------- audio ---------- */\n' + IOS_UNLOCK, 1)
