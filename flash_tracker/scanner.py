"""OCR-Scanner — Sofort-Erkennung mit Selbst-Verifizierung.

Ablauf pro erkanntem (Champion, Spell, Sicherheit):
  1. ERSTER Read -> Timer wird SOFORT gesetzt (provisorisch, confirmed=False).
  2. Wird er innerhalb CONFIRM_WINDOW insgesamt MIN_SIGHTINGS-mal gelesen
     -> bestätigt (confirmed=True).
  3. Bleibt es bei 1 Read (Fantasie) -> Timer entfernt sich nach Ablauf
     des Fensters wieder (Selbstkorrektur).

Zeiten kommen aus dem Chat-Timestamp (Spielzeit, wann der Spell up ist);
alte History-Flashes (>Cooldown) werden gar nicht erst angezeigt.

Schwere Abhängigkeiten werden erst beim Start des Scans importiert.
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
        self.tracks = {}         # (champ, spell, certain) -> dict
        self.game_now = 0
        self.last_decision = ""

    def reset(self):
        self.tracks.clear()
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
        if self.game_now == 0 or 0 < cand - self.game_now <= 90:
            self.game_now = cand

    def _timing(self, track, cd):
        """(elapsed, up_game) aus dem häufigsten Timestamp der Sichtungen."""
        from config import TIMING_FROM_STAMP
        from parser import stamp_seconds
        if not TIMING_FROM_STAMP or not track["stamps"]:
            return 0, None
        stamp = track["stamps"].most_common(1)[0][0]
        ssec = stamp_seconds(stamp)
        if ssec is None:
            return 0, None
        up_game = ssec + cd
        elapsed = max(0, self.game_now - ssec) if self.game_now else 0
        return elapsed, up_game

    def process(self, events):
        from config import (CONFIRM_WINDOW, MIN_SIGHTINGS, REQUIRE_STAMP,
                            SPELL_COOLDOWNS)
        now = time.time()
        self._update_clock(events)

        # Abgelaufene Timer -> Track zurücksetzen (Re-Flash möglich).
        active = {f"{t.champion}_{t.spell}" for t in self.manager.get_active()}
        for key in list(self.tracks):
            ch, sp, _ = key
            if self.tracks[key]["committed"] and f"{ch}_{sp}" not in active:
                del self.tracks[key]

        # --- Sichtungen einsortieren + SOFORT committen ---
        for e in events:
            if REQUIRE_STAMP and not e["stamp"]:
                continue
            key = (e["champion"], e["spell"], e["certain"])
            tr = self.tracks.get(key)
            if tr is None:
                tr = self.tracks[key] = {
                    "first": now, "count": 0, "committed": False,
                    "verified": False, "stamps": Counter(),
                }
            tr["count"] += 1
            if e["stamp"]:
                tr["stamps"][e["stamp"]] += 1

            if not tr["committed"]:
                champ, spell, certain = key
                cd = SPELL_COOLDOWNS.get(spell, 300)
                elapsed, up_game = self._timing(tr, cd)
                tr["committed"] = True
                if elapsed >= cd and self.game_now:      # längst wieder up
                    tr["verified"] = True
                    self.last_decision = f"{champ} {spell}: schon up (übersprungen)"
                    continue
                self.manager.add(champ, spell, cd, certain=certain,
                                 elapsed=elapsed, up_game=up_game, confirmed=False)
                self.last_decision = f"{champ} {spell}: SOFORT (provisorisch)"
                if self.on_event:
                    self.on_event(champ, spell)

        # --- Verifizierung / Selbstkorrektur ---
        for key in list(self.tracks):
            tr = self.tracks[key]
            if not tr["committed"] or tr["verified"]:
                continue
            champ, spell, certain = key
            if tr["count"] >= MIN_SIGHTINGS:
                tr["verified"] = True
                self.manager.set_confirmed(champ, spell, True)
                self.last_decision = f"{champ} {spell}: BESTÄTIGT ({tr['count']}x)"
            elif now - tr["first"] > CONFIRM_WINDOW:
                # Nur 1x gesehen -> Fantasie -> provisorischen Timer entfernen.
                if self.manager.remove(champ, spell, only_unconfirmed=True):
                    self.last_decision = f"{champ} {spell}: verworfen (nur 1x)"
                del self.tracks[key]

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
