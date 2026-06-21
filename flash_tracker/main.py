"""Einstiegspunkt — startet die Flash-Tracker-GUI.

    python main.py
"""
from gui import FlashTrackerGUI


def main():
    print("Flash Tracker GUI gestartet …")
    FlashTrackerGUI().run()
    print("Flash Tracker beendet.")


if __name__ == "__main__":
    main()
