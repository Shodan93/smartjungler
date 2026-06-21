"""Dauer-Verifikation der OCR-Erkennung.

Läuft in einer Schleife, scannt fortlaufend den Chat und zeigt live:
  - jede geparste Lesart pro Scan (Champion + sicher/Ping)
  - die Mehrheits-Entscheidung pro Chat-Zeile (übernommen / verworfen)
  - die resultierenden aktiven Timer

So kannst du über mehrere Minuten beobachten, ob Flashes zuverlässig
getrackt werden und ob "Fantasien" auftauchen.

Start (League mit Chat im Vordergrund):
    python debug_watch.py

Beenden mit Strg+C.
"""
import time

from capture import capture_chat
from ocr import read_chat
from parser import parse_chat
from timers import TimerManager
from scanner import Scanner
from config import SCAN_INTERVAL


def main():
    manager = TimerManager()
    scanner = Scanner(manager)
    print("Dauer-Scan läuft … (Strg+C zum Beenden)\n")

    scan_no = 0
    last_decision = ""
    try:
        while True:
            scan_no += 1
            text = read_chat(capture_chat())
            events = parse_chat(text)

            reads = ", ".join(
                f"{e['champion']}{'!' if e['certain'] else '?'}@{e['stamp']}"
                for e in events
            )
            scanner.process(events)

            line = (f"[Scan {scan_no:>4}] Spielzeit~{scanner.game_now//60}:"
                    f"{scanner.game_now % 60:02d} | Lesarten: {reads or '—'}")
            if scanner.last_decision and scanner.last_decision != last_decision:
                line += f"   >>> ENTSCHEIDUNG: {scanner.last_decision}"
                last_decision = scanner.last_decision
            print(line)

            active = manager.get_active()
            if active:
                print("            Aktive Timer:",
                      " | ".join(t.display() for t in active))

            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\nBeendet. Finale Timer:")
        for t in manager.get_active():
            print("  ", t.display())


if __name__ == "__main__":
    main()
