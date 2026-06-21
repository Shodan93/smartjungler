"""OCR-Scanner als Hintergrund-Thread mit Mehrheits-Abstimmung.

Problem: einzelne OCR-Scans liefern manchmal Fantasien (falsche Champs)
oder verpassen einen Read. Lösung: Jede Chat-Zeile ist über ihren
Game-Timestamp eindeutig. Wir sammeln über ein kurzes Zeitfenster ALLE
Champion-Lesarten für denselben (Timestamp, Spell, Sicherheit) und
übernehmen am Ende die HÄUFIGSTE Lesart — sofern sie oft genug gesehen
wurde. Dadurch:
  - einmalige Fehllesungen ("Fantasien") bleiben in der Minderheit -> raus
  - echte Flashes kommen durch, auch wenn einzelne Reads daneben liegen

Schwere Abhängigkeiten (mss, cv2, pytesseract) werden erst beim Start
des Scans importiert, damit die GUI auch ohne sie läuft.
"""
import time
import threading
from collections import Counter


class _Slot:
    """Sammelt Champion-Stimmen für eine Chat-Zeile (= ein Timestamp)."""
    def __init__(self):
        self.votes = Counter()
        self.first_seen = time.time()
        self.committed = False


class Scanner:
    def __init__(self, manager, on_event=None):
        self.manager = manager
        self.on_event = on_event          # Callback(champion, spell)
        self._thread = None
        self._enabled = False
        self._running = False
        self.status = "aus"
        self.slots = {}                   # (stamp, spell, certain) -> _Slot
        self.last_decision = ""           # für Debug-Anzeige

    def reset(self):
        self.slots.clear()
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

    def _ingest(self, events):
        """Eine Liste geparster Events in die Stimm-Sammlung einsortieren."""
        from config import REQUIRE_STAMP
        for e in events:
            stamp = e.get("stamp")
            if REQUIRE_STAMP and not stamp:
                continue
            slot_key = (stamp, e["spell"], e["certain"])
            slot = self.slots.get(slot_key)
            if slot is None:
                slot = self.slots[slot_key] = _Slot()
            if not slot.committed:
                slot.votes[e["champion"]] += 1

    def _decide(self):
        """Abgelaufene Stimm-Fenster auswerten und Timer setzen."""
        from config import VOTE_WINDOW, MIN_VOTES, SPELL_COOLDOWNS
        now = time.time()
        for (stamp, spell, certain), slot in self.slots.items():
            if slot.committed:
                continue
            if now - slot.first_seen < VOTE_WINDOW:
                continue
            if not slot.votes:
                slot.committed = True
                continue
            champ, count = slot.votes.most_common(1)[0]
            slot.committed = True
            if count < MIN_VOTES:
                self.last_decision = f"verworfen: {champ}? ({count} Stimmen)"
                continue
            cd = SPELL_COOLDOWNS.get(spell, 300)
            changed = self.manager.add(champ, spell, cd, certain=certain, stamp=stamp)
            self.last_decision = (
                f"{champ} {spell} "
                f"({'used' if certain else 'ping'}, {count} Stimmen)"
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
                self._ingest(parse_chat(text))
                self._decide()
                self.status = "aktiv"
            except Exception as e:
                self.status = f"Fehler: {e}"
            time.sleep(SCAN_INTERVAL)
