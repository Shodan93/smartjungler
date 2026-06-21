# ============================================================
#  Flash Tracker — zentrale Konfiguration
#  Bildschirm: 2560x1440 (Chat unten links)
#  Betriebssystem: Windows
# ============================================================

# ---- Chat-Region (mit calibrate.py exakt bestimmen) --------
# Bereich, der per OCR gescannt wird. Bei 2560x1440 liegt der
# Chat unten links. Werte ggf. mit calibrate.py anpassen.
CHAT_REGION = {
    "top":    840,    # Startpunkt Y  (nochmal 20px tiefer -> neueste/unterste Zeile wird erfasst)
    "left":   0,      # Startpunkt X
    "width":  1050,   # Breite des Chatfensters
    "height": 240,    # Höhe des Chatfensters
}

# ---- Scan / Loop -------------------------------------------
SCAN_INTERVAL = 0.3          # Sekunden zwischen OCR-Scans (schneller = flotter)
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

# ---- Erkennung / Parsing -----------------------------------
# Ähnlichkeits-Schwelle fürs Champion-Fuzzy-Matching (0..1).
# Höher = strenger (weniger Fehltreffer, aber mehr verworfene Reads).
FUZZY_CUTOFF = 0.7

# --- Sofort-Erkennung + Selbst-Verifizierung ---
# Ein Flash erscheint SOFORT beim ersten Read (provisorisch, grau im HUD).
# Wird er innerhalb von CONFIRM_WINDOW Sekunden insgesamt MIN_SIGHTINGS-mal
# gelesen -> bestätigt (grün). Wird er nur 1x gesehen (Fantasie) -> nach
# Ablauf des Fensters automatisch wieder entfernt (Selbstkorrektur).
CONFIRM_WINDOW = 1.5   # Zeit zum Verifizieren nach der ersten Sichtung
MIN_SIGHTINGS  = 2     # Reads bis "bestätigt"

# Timer nur für Zeilen MIT erkennbarem Timestamp (kill für Hintergrund-Müll)
REQUIRE_STAMP = True

# Restzeit aus dem Chat-Timestamp berechnen statt immer 5:00:
#   Restzeit = Cooldown - (aktuelle Spielzeit - Flash-Zeitstempel)
# Macht Zeiten korrekt und überspringt automatisch alte History-Flashes.
TIMING_FROM_STAMP = True

# Zeilen, die einen dieser Texte enthalten, werden ignoriert
# (Countdown-/Erinnerungs-Pings, keine frischen Flashes).
IGNORE_PHRASES = ["wait for", "has selected", "quest complete", "/help"]

# ---- Auto-Copy ---------------------------------------------
# League akzeptiert KEIN Strg+V im Chat -> Auto-Copy standardmäßig AUS
# (konservativ, belegt nicht dauernd die Windows-Zwischenablage).
# Zum Teilen im Chat lieber den Tipp-Hotkey (siehe unten) verwenden.
AUTO_COPY_DEFAULT = False

# ---- Chat-Tippen (Windows) ---------------------------------
# ACHTUNG: League/Vanguard blockt simulierte Tastatureingaben. Das
# Auto-Tippen funktioniert daher i.d.R. NICHT -> standardmäßig aus.
# Team-Sharing: Timer am HUD ablesen und selbst tippen.
CHAT_TYPING_ENABLED = False
CHAT_TYPE_HOTKEY  = "z"
# Chat ist beim Drücken bereits OFFEN -> Trigger-Zeichen ('z') wird per
# Backspace entfernt, kein Enter zum Öffnen.
CHAT_ALREADY_OPEN = True
CHAT_AUTO_SEND    = True    # nach dem Tippen automatisch mit Enter absenden
PASTE_TO_ALL_CHAT = False   # True = All-Chat (Shift+Enter); nur ohne ALREADY_OPEN

# ---- Minimal-HUD -------------------------------------------
HUD_X = 0          # ganz oben links
HUD_Y = 0
HUD_ALPHA = 0.85
HUD_DEFAULT = True

# ---- GUI-Fenster -------------------------------------------
WINDOW_X = 2150
WINDOW_Y = 80
ALWAYS_ON_TOP_DEFAULT = True

# ---- OCR Preprocessing -------------------------------------
OCR_SCALE_FACTOR = 3          # Bild vergrößern für bessere OCR-Genauigkeit
OCR_CONFIG       = "--psm 6"  # Tesseract Page Segmentation Mode
# Schwellwert fürs Schwarz-Weiß. Wir nutzen den Helligkeits-(Value-)Kanal,
# damit auch farbige Namen (rot/orange) sauber lesbar werden.
OCR_THRESHOLD    = 110

# Champion-/Spell-Wortliste an Tesseract übergeben (bessere Erkennung).
# Datei muss im Arbeitsverzeichnis liegen (kein Leerzeichen im Namen!).
# Vorerst aus: manche Tesseract-Versionen liefern damit leeren Text.
# Das Fuzzy-Matching gegen die Champion-Liste übernimmt die Korrektur.
OCR_USE_WORDLIST  = False
OCR_WORDLIST_FILE = "champion_words.txt"

# Windows: Pfad zur Tesseract-Executable.
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---- Audio -------------------------------------------------
ALERT_SOUND = "sounds/alert.wav"
