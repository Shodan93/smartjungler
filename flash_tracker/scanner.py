"""OCR-Scanner als Hintergrund-Thread.

Schwere Abhängigkeiten (mss, cv2, pytesseract) werden erst beim Start
des Scans importiert, damit die GUI auch ohne sie läuft.

Dedup- & Bestätigungs-Strategie:
  - Jedes Event hat einen Game-Timestamp. Ein (stamp, champ, spell,
    certain) muss in MIN_SIGHTINGS Scans gesehen werden, bevor ein Timer
    startet — das filtert einmalige OCR-Fehllesungen heraus, während
    echte (mehrfach gelesene) Zeilen durchkommen.
  - Danach wird dasselbe Event nicht erneut gezählt (kein Doppel-Zählen).
  - Ein "used"-Event (sicher) hat eine andere Sicherheit als ein Ping und
    darf daher eine vorhandene Schätzung überschreiben.
"""
import time
import threading


class Scanner:
    def __init__(self, manager, on_event=None):
        self.manager = manager
        self.on_event = on_event          # Callback(champion, spell)
        self._thread = None
        self._enabled = False
        self._running = False
        self.status = "aus"
        self.sightings = {}               # key -> Anzahl Sichtungen
        self.committed = set()            # bereits getrackte keys

    def reset(self):
        self.sightings.clear()
        self.committed.clear()

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

    def _loop(self):
        from capture import capture_chat
        from ocr import read_chat
        from parser import parse_chat
        from config import SCAN_INTERVAL, MIN_SIGHTINGS

        while self._running:
            if not self._enabled:
                time.sleep(0.2)
                continue
            try:
                text = read_chat(capture_chat())
                for e in parse_chat(text):
                    stamp = e.get("stamp")
                    key = (stamp, e["champion"], e["spell"], e["certain"])
                    if key in self.committed:
                        continue
                    # Bestätigung sammeln: erst nach MIN_SIGHTINGS Scans
                    # wird der Timer gesetzt (filtert OCR-Aussetzer).
                    self.sightings[key] = self.sightings.get(key, 0) + 1
                    if self.sightings[key] < MIN_SIGHTINGS:
                        continue
                    self.committed.add(key)
                    changed = self.manager.add(
                        e["champion"], e["spell"], e["cooldown"],
                        certain=e["certain"], stamp=stamp,
                    )
                    if changed and self.on_event:
                        self.on_event(e["champion"], e["spell"])
                self.status = "aktiv"
            except Exception as e:
                self.status = f"Fehler: {e}"
            time.sleep(SCAN_INTERVAL)
