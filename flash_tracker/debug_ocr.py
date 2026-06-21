"""OCR-Debug-Tool.

Macht EINEN Screenshot der aktuellen CHAT_REGION aus config.py,
speichert das Roh- und das aufbereitete Bild und zeigt, welchen Text
Tesseract erkennt und welche Spell-Pings der Parser findet.

So siehst du sofort, ob
  - der Bildausschnitt stimmt  (schau dir debug_raw.png an)
  - die OCR den Text liest      (siehe Konsole)
  - der Parser ihn versteht     (siehe Konsole)

Aufruf (League mit offenem Chat im Vordergrund lassen):
    python debug_ocr.py
"""
import cv2

from capture import capture_chat
from ocr import preprocess, read_chat
from parser import parse_chat
from config import CHAT_REGION


def main():
    print("CHAT_REGION:", CHAT_REGION)

    img = capture_chat()
    print("Screenshot-Größe (H x B):", img.shape[:2])

    # Bilder speichern, damit du den Ausschnitt prüfen kannst.
    raw_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) if img.shape[-1] == 4 else img
    cv2.imwrite("debug_raw.png", raw_bgr)
    cv2.imwrite("debug_processed.png", preprocess(img))
    print("Gespeichert: debug_raw.png  und  debug_processed.png")

    text = read_chat(img)
    print("\n----- OCR-TEXT -----")
    print(text if text.strip() else "(nichts erkannt)")
    print("--------------------")

    events = parse_chat(text)
    print("\nErkannte Spell-Pings:")
    if events:
        for e in events:
            print("  ", e)
    else:
        print("   (keine)")


if __name__ == "__main__":
    main()
