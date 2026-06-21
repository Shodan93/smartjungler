import cv2
import numpy as np
import pytesseract
from PIL import Image
from config import OCR_SCALE_FACTOR, OCR_CONFIG, TESSERACT_CMD

# Windows: Pfad zur Tesseract-Executable setzen.
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def preprocess(img):
    """Bereitet das Chat-Bild für die OCR auf.

    - Graustufen
    - Upscale (bessere Genauigkeit bei kleinem Text)
    - Threshold (heller Text auf dunklem Hintergrund)
    """
    # mss liefert BGRA -> auf 3 Kanäle reduzieren
    if img.shape[-1] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape
    scaled = cv2.resize(
        gray,
        (w * OCR_SCALE_FACTOR, h * OCR_SCALE_FACTOR),
        interpolation=cv2.INTER_LINEAR,
    )

    _, thresh = cv2.threshold(scaled, 100, 255, cv2.THRESH_BINARY)
    return thresh


def read_chat(img):
    """OCR über das aufbereitete Bild, liefert erkannten Text."""
    processed = preprocess(img)
    pil_img = Image.fromarray(processed)
    text = pytesseract.image_to_string(pil_img, config=OCR_CONFIG)
    return text
