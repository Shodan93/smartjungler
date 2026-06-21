"""Pfad-Helfer — funktioniert sowohl als .py als auch als PyInstaller-.exe."""
import os
import sys


def resource_path(rel):
    """Pfad zu einer mitgelieferten Datei (Sound, Wortliste …).

    Im PyInstaller-Bundle liegen Daten in sys._MEIPASS, sonst neben
    diesem Skript.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)
