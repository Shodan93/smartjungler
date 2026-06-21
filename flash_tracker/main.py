"""Einstiegspunkt — startet die Flash-Tracker-GUI.

    python main.py        (mit Konsole)
    Flash Tracker.vbs     (Doppelklick, ohne Konsole)

WICHTIG: Beim Start über pythonw/VBS (ohne Konsole) ist sys.stdout/err
None. Jeder print() würde dann den jeweiligen Thread crashen (z.B. der
Scan-Thread beim Tracken). Deshalb leiten wir die Ausgaben ganz am
Anfang auf eine Logdatei (oder devnull) um — VOR allen anderen Imports.
"""
import sys
import os


def _redirect_std():
    if sys.stdout is not None and sys.stderr is not None:
        return
    candidates = []
    try:
        here = os.path.dirname(os.path.abspath(sys.argv[0]))
        candidates.append(os.path.join(here, "flashtracker.log"))
    except Exception:
        pass
    candidates.append(os.path.join(os.getcwd(), "flashtracker.log"))
    candidates.append(os.devnull)

    target = None
    for path in candidates:
        try:
            target = open(path, "w", buffering=1, encoding="utf-8")
            break
        except Exception:
            target = None
    if target is not None:
        if sys.stdout is None:
            sys.stdout = target
        if sys.stderr is None:
            sys.stderr = target


_redirect_std()

from gui import FlashTrackerGUI   # noqa: E402  (erst nach der Umleitung)


def main():
    print("Flash Tracker GUI gestartet …")
    FlashTrackerGUI().run()
    print("Flash Tracker beendet.")


if __name__ == "__main__":
    main()
