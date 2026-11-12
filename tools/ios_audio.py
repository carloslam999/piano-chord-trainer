# exec'd by scrub.py and index_page.py: make sound play on iPhones even when the ring/silent switch is on silent.
# iOS treats Web Audio like a ringtone (muted by the switch) unless the page says it is media playback.
# Safari 16.4+ has navigator.audioSession for that; older iOS needs a silent <audio> element playing during a tap.
import io as _io, wave as _wave, base64 as _b64
_b = _io.BytesIO(); _w = _wave.open(_b, 'wb'); _w.setnchannels(1); _w.setsampwidth(1); _w.setframerate(8000)
_w.writeframes(bytes([128]) * 400); _w.close()
SILENT_WAV = 'data:audio/wav;base64,' + _b64.b64encode(_b.getvalue()).decode()

IOS_UNLOCK = r'''function iosAudioUnlock() {
  try { if (navigator.audioSession) { navigator.audioSession.type = 'playback'; return; } } catch (e) {}
  if (iosAudioUnlock.el || !/iP(hone|ad|od)|Macintosh/.test(navigator.userAgent) || !('ontouchend' in document)) return;
  const el = iosAudioUnlock.el = document.createElement('audio');
  el.src = '%s'; el.loop = true; el.setAttribute('playsinline', ''); el.setAttribute('x-webkit-airplay', 'deny');
  const p = el.play(); if (p && p.catch) p.catch(() => { iosAudioUnlock.el = null; });
}
''' % SILENT_WAV
