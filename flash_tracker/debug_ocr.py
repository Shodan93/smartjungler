"""OCR-Debug-Tool mit Countdown.

Weil League meist im Vordergrund sein muss (sonst ist der Chat weg),
wartet das Tool ein paar Sekunden, bevor es den Screenshot macht.
Du startest es im Terminal und wechselst dann zu League.

Aufrufe:
    python debug_ocr.py            -> scannt die CHAT_REGION (5s Countdown)
    python debug_ocr.py full       -> Vollbild-Screenshot zum Position finden
    python debug_ocr.py 8          -> Countdown auf 8 Sekunden setzen
    python debug_ocr.py full 8     -> Vollbild + 8s Countdown

Tipp: League auf "Randlos" (Borderless) stellen, sonst sind Screenshots
unter Umständen schwarz.
"""
import sys
import time

import cv2
import numpy as np
import mss

from capture import capture_chat
from ocr import preprocess, read_chat
from parser import parse_chat
from config import CHAT_REGION


def countdown(seconds):
    print(f"Wechsle JETZT zu League (offener Chat)! Screenshot in {seconds}s …")
    for i in range(seconds, 0, -1):
        print(f"  {i} …", flush=True)
        time.sleep(1)
    print("  *klick*")


def grab_fullscreen():
    with mss.mss() as sct:
        return np.array(sct.grab(sct.monitors[1]))


def run_full(secs):
    countdown(secs)
    img = grab_fullscreen()
    bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    cv2.imwrite("debug_fullscreen.png", bgr)
    h, w = bgr.shape[:2]
    print(f"\nVollbild gespeichert: debug_fullscreen.png  ({w} x {h} px)")
    print("Öffne das Bild und lies grob die Pixel-Koordinaten des")
    print("Chatfensters ab (oben-links = 0,0). Dann CHAT_REGION setzen,")
    print("oder mit 'python calibrate.py' ein Rechteck ziehen.")


def run_region(secs):
    print("CHAT_REGION:", CHAT_REGION)
    countdown(secs)

    img = capture_chat()
    print("Ausschnitt-Größe (H x B):", img.shape[:2])

    raw = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[-1] == 4 else img
    cv2.imwrite("debug_raw.png", raw)
    cv2.imwrite("debug_processed.png", preprocess(img))
    print("Gespeichert: debug_raw.png  und  debug_processed.png")

    from config import OCR_USE_WORDLIST, IGNORE_PHRASES
    print("OCR-Wortliste aktiv:", OCR_USE_WORDLIST)

    text = read_chat(img)
    print("\n----- OCR-TEXT (roh) -----")
    print(text if text.strip() else "(nichts erkannt)")
    print("--------------------------")

    print("\n----- Zeilen-Analyse -----")
    for line in text.splitlines():
        if not line.strip():
            continue
        low = line.lower()
        ign = next((p for p in IGNORE_PHRASES if p in low), None)
        if ign:
            print(f"  IGNORIERT (enthält '{ign}'): {line!r}")
        else:
            print(f"  geprüft: {line!r}")
    print("--------------------------")

    events = parse_chat(text)
    print("\nErkannte Spell-Pings:")
    if events:
        for e in events:
            print("  ", e)
    else:
        print("   (keine)")


def main():
    args = [a.lower() for a in sys.argv[1:]]
    full = "full" in args
    secs = 5
    for a in args:
        if a.isdigit():
            secs = int(a)
    if full:
        run_full(secs)
    else:
        run_region(secs)


if __name__ == "__main__":
    main()
