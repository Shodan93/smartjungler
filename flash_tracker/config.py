# ============================================================
#  Flash Tracker — zentrale Konfiguration
#  Bildschirm: 2560x1440 (Chat unten links, Overlay oben rechts)
#  Betriebssystem: Windows
# ============================================================

# ---- Chat-Region (mit calibrate.py exakt bestimmen) --------
# Bereich, der per OCR gescannt wird. Bei 2560x1440 liegt der
# Chat unten links. Werte ggf. mit calibrate.py anpassen.
CHAT_REGION = {
    "top":    1100,   # Startpunkt Y
    "left":   0,      # Startpunkt X
    "width":  600,    # Breite des Chatfensters
    "height": 220,    # Höhe des Chatfensters
}

# ---- Scan / Loop -------------------------------------------
SCAN_INTERVAL = 0.5    # Sekunden zwischen OCR-Scans

# ---- Summoner-Spell Cooldowns (Sekunden) -------------------
# Hinweis: Basis-Cooldowns ohne Cosmic Insight / Items.
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

# ---- Overlay -----------------------------------------------
OVERLAY_X = 2200
OVERLAY_Y = 100

# ---- OCR Preprocessing -------------------------------------
OCR_SCALE_FACTOR = 3          # Bild vergrößern für bessere OCR-Genauigkeit
OCR_CONFIG       = "--psm 6"  # Tesseract Page Segmentation Mode

# Windows: Pfad zur Tesseract-Executable.
# Standard-Installationspfad des UB-Mannheim Installers.
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---- Audio -------------------------------------------------
ALERT_SOUND = "sounds/alert.wav"

# ---- Hotkeys (global, funktionieren auch im Spiel) ---------
# Tippt alle laufenden Timer ins League-Chatfenster:
#   z.B. "jhin 2 40, lux 5 39"
PASTE_HOTKEY = "f8"
# Setzt alle Timer zurück (z.B. nach Spielende):
RESET_HOTKEY = "f9"
# Beendet das Programm sauber:
QUIT_HOTKEY  = "f10"

# Taste, mit der League das Chatfenster öffnet/sendet.
# "enter" = Team-Chat, "shift+enter" könnte All-Chat sein.
CHAT_OPEN_KEY = "enter"
# Vor "All-Chat" wird zusätzlich diese Taste benutzt (leer lassen
# für Team-Chat). League: Shift+Enter öffnet All-Chat.
PASTE_TO_ALL_CHAT = False
