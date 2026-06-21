"""OCR-Scanner — schnell & robust.

Erkennung (champion-zentriert, schnell):
  - Ein (Champion, Spell, Sicherheit) wird getrackt, sobald er
    MIN_SIGHTINGS-mal innerhalb von CONFIRM_WINDOW Sekunden gelesen wurde.
    -> reagiert in ~1 s, filtert einmalige Fehllesungen ("Fantasien").
  - Nur Zeilen mit Timestamp zählen (Hintergrund-Müll fällt weg).

Zeiten (aus dem Chat-Timestamp):
  - Aktuelle Spielzeit = höchster gesehener Timestamp.
  - Restzeit = Cooldown - (Spielzeit - Flash-Timestamp).
  - Bereits abgelaufene (alte History-)Flashes werden übersprungen.

Re-Flash: sobald ein Timer abgelaufen ist, kann derselbe Champ erneut
getrackt werden.
"""
import time
import threading
from collections import Counter


class Scanner:
    def __init__(self, manager, on_event=None):
        self.manager = manager
        self.on_event = on_event
        self._thread = None
        self._enabled = False
        self._running = False
        self.status = "aus"
        self.sightings = {}      # (champ, spell, certain) -> list[(t, stamp)]
        self.committed = set()
        self.game_now = 0        # höchste gesehene Spielzeit (Sekunden)
        self.last_decision = ""

    def reset(self):
        self.sightings.clear()
        self.committed.clear()
        self.game_now = 0
        self.last_decision = ""

    def is_enabled(self):
        return self._enabled

    def start(self):
        self._enabled = True
        if self._thread and self._thread.is_alive():
            return True, "Scan aktiv"
        try:
            from capture import capture_chat   # noqa: F401
            from ocr import read_chat          # noqa: F401
            from parser import parse_chat      # noqa: F401
        except Exception as e:
            self._enabled = False
            self.status = f"Fehler: {e}"
            return False, str(e)
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.status = "aktiv"
        return True, "Scan gestartet"

    def stop(self):
        self._enabled = False
        self._running = False
        self.status = "aus"

    def _update_clock(self, events):
        from parser import stamp_seconds
        secs = [stamp_seconds(e["stamp"]) for e in events]
        secs = [x for x in secs if x is not None]
        if not secs:
            return
        cand = max(secs)
        # Nur vorwärts und keine absurden Sprünge (Schutz vor Stempel-Jitter).
        if self.game_now == 0 or 0 < cand - self.game_now <= 90:
            self.game_now = cand

    def process(self, events):
        """Events einsortieren und fällige Timer setzen (auch vom Debug-Tool)."""
        from config import (CONFIRM_WINDOW, MIN_SIGHTINGS, REQUIRE_STAMP,
                            TIMING_FROM_STAMP, SPELL_COOLDOWNS)
        from parser import stamp_seconds
        now = time.time()

        self._update_clock(events)

        for e in events:
            if REQUIRE_STAMP and not e["stamp"]:
                continue
            key = (e["champion"], e["spell"], e["certain"])
            self.sightings.setdefault(key, []).append((now, e["stamp"]))

        # Abgelaufene Timer aus 'committed' entfernen -> Re-Flash möglich.
        active = {f"{t.champion}_{t.spell}" for t in self.manager.get_active()}
        self.committed = {k for k in self.committed if f"{k[0]}_{k[1]}" in active}

        for key in list(self.sightings.keys()):
            lst = [(t, s) for (t, s) in self.sightings[key] if now - t <= CONFIRM_WINDOW]
            if not lst:
                del self.sightings[key]
                continue
            self.sightings[key] = lst
            if key in self.committed or len(lst) < MIN_SIGHTINGS:
                continue

            champ, spell, certain = key
            cd = SPELL_COOLDOWNS.get(spell, 300)
            elapsed = 0
            up_game = None
            if TIMING_FROM_STAMP:
                stamp = Counter(s for _, s in lst).most_common(1)[0][0]
                ssec = stamp_seconds(stamp)
                if ssec is not None:
                    up_game = ssec + cd            # Spielzeit, wann wieder up
                    if self.game_now:
                        elapsed = max(0, self.game_now - ssec)

            self.committed.add(key)
            if elapsed >= cd:
                self.last_decision = f"{champ} {spell}: schon up (übersprungen)"
                continue
            changed = self.manager.add(champ, spell, cd, certain=certain,
                                       elapsed=elapsed, up_game=up_game)
            self.last_decision = (
                f"{champ} {spell} ({'used' if certain else 'ping'}, -{int(elapsed)}s)"
            )
            if changed and self.on_event:
                self.on_event(champ, spell)

    def _loop(self):
        from capture import capture_chat
        from ocr import read_chat
        from parser import parse_chat
        from config import SCAN_INTERVAL

        while self._running:
            if not self._enabled:
                time.sleep(0.2)
                continue
            try:
                text = read_chat(capture_chat())
                self.process(parse_chat(text))
                self.status = "aktiv"
            except Exception as e:
                self.status = f"Fehler: {e}"
            time.sleep(SCAN_INTERVAL)
