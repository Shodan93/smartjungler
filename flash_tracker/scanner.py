"""OCR-Scanner als Hintergrund-Thread.

Die schweren Abhängigkeiten (mss, cv2, pytesseract) werden erst beim
Start des Scans importiert. So läuft die GUI auch ohne installiertes
Tesseract/OpenCV — du kannst alles manuell testen und den OCR-Scan
nur dann aktivieren, wenn League läuft.
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
        self.seen = set()

    def is_enabled(self):
        return self._enabled

    def start(self):
        """Startet (oder reaktiviert) den Scan-Thread."""
        self._enabled = True
        if self._thread and self._thread.is_alive():
            return True, "Scan aktiv"
        # Abhängigkeiten erst hier laden.
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
        from config import SCAN_INTERVAL

        while self._running:
            if not self._enabled:
                time.sleep(0.2)
                continue
            try:
                text = read_chat(capture_chat())
                for e in parse_chat(text):
                    key = f"{e['champion']}_{e['spell']}"
                    if key not in self.seen:
                        self.seen.add(key)
                        self.manager.add(e["champion"], e["spell"], e["cooldown"])
                        if self.on_event:
                            self.on_event(e["champion"], e["spell"])
                active = {f"{t.champion}_{t.spell}" for t in self.manager.get_active()}
                self.seen.intersection_update(active)
                self.status = "aktiv"
            except Exception as e:
                self.status = f"Fehler: {e}"
            time.sleep(SCAN_INTERVAL)
