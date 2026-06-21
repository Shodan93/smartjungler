import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from config import (
    OCR_SCALE_FACTOR, OCR_CONFIG, TESSERACT_CMD, OCR_THRESHOLD,
    OCR_USE_WORDLIST, OCR_WORDLIST_FILE,
)

# Windows: Pfad zur Tesseract-Executable setzen.
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Optional die Champion-/Spell-Wortliste an Tesseract übergeben.
# (Dateiname ohne Leerzeichen, im Arbeitsverzeichnis — sonst splittet
#  pytesseract den Pfad falsch.)
_config = OCR_CONFIG
if OCR_USE_WORDLIST and os.path.exists(OCR_WORDLIST_FILE) and " " not in OCR_WORDLIST_FILE:
    _config = f"{OCR_CONFIG} --user-words {OCR_WORDLIST_FILE}"

_wordlist_ok = True


def preprocess(img):
    """Value-Kanal -> Upscale -> Threshold.

    Statt Luminanz nutzen wir den Helligkeits-(Value-)Kanal = max(B,G,R).
    Damit werden auch FARBIGE Namen (rot/orange, z.B. Anivia & Gegner)
    hell und sauber lesbar — Graustufen hatten rote Schrift zerlegt.
    """
    if img.shape[-1] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    value = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 2]   # = max der Kanäle
    h, w = value.shape
    scaled = cv2.resize(
        value, (w * OCR_SCALE_FACTOR, h * OCR_SCALE_FACTOR),
        interpolation=cv2.INTER_CUBIC,
    )
    _, thresh = cv2.threshold(scaled, OCR_THRESHOLD, 255, cv2.THRESH_BINARY)
    return thresh


def read_chat(img):
    """OCR über das aufbereitete Bild, liefert erkannten Text.

    Fällt automatisch auf die Standard-Config zurück, falls die
    Wortliste Tesseract Probleme bereitet."""
    global _config, _wordlist_ok
    pil_img = Image.fromarray(preprocess(img))
    try:
        return pytesseract.image_to_string(pil_img, config=_config)
    except Exception:
        if _wordlist_ok and _config != OCR_CONFIG:
            _wordlist_ok = False
            _config = OCR_CONFIG  # Wortliste verwerfen, ohne sie weiter
            return pytesseract.image_to_string(pil_img, config=_config)
        raise
