# ============================================================
#  Flash Tracker — zentrale Konfiguration
#  Bildschirm: 2560x1440 (Chat unten links)
#  Betriebssystem: Windows
# ============================================================

# ---- Chat-Region (mit calibrate.py exakt bestimmen) --------
# Bereich, der per OCR gescannt wird. Bei 2560x1440 liegt der
# Chat unten links. Werte ggf. mit calibrate.py anpassen.
CHAT_REGION = {
    "top":    800,    # Startpunkt Y  (Chat liegt ~820–990 bei 1440p)
    "left":   0,      # Startpunkt X
    "width":  1050,   # Breite des Chatfensters
    "height": 240,    # Höhe des Chatfensters
}

# ---- Scan / Loop -------------------------------------------
SCAN_INTERVAL = 0.5          # Sekunden zwischen OCR-Scans
SCAN_ENABLED_DEFAULT = False  # OCR beim Start aus (erst zum Testen GUI)

# ---- Summoner-Spell Cooldowns (Sekunden) -------------------
# Basis-Cooldowns ohne Cosmic Insight / Items.
SPELL_COOLDOWNS = {
    "flash":    300,   # 5:00
    "ignite":   180,   # 3:00
    "heal":     240,   # 4:00
    "ghost":    210,   # 3:30
    "barrier":  180,   # 3:00
    "exhaust":  210,   # 3:30
    "teleport": 360,   # 6:00 (variiert mit Level)
    "cleanse":  210,   # 3:30
    "smite":     90,   # 1:30
}

# Reihenfolge der Spells im GUI-Dropdown.
SPELLS = list(SPELL_COOLDOWNS.keys())

# ---- GUI-Fenster -------------------------------------------
WINDOW_X = 2150
WINDOW_Y = 80
ALWAYS_ON_TOP_DEFAULT = True

# ---- OCR Preprocessing -------------------------------------
OCR_SCALE_FACTOR = 3          # Bild vergrößern für bessere OCR-Genauigkeit
OCR_CONFIG       = "--psm 6"  # Tesseract Page Segmentation Mode

# Windows: Pfad zur Tesseract-Executable.
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---- Audio -------------------------------------------------
ALERT_SOUND = "sounds/alert.wav"
