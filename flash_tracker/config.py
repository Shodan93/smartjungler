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

# ---- Erkennung / Parsing -----------------------------------
# Ähnlichkeits-Schwelle fürs Champion-Fuzzy-Matching (0..1).
# Höher = strenger (weniger Fehltreffer, aber mehr verworfene Reads).
FUZZY_CUTOFF = 0.7

# --- Mehrheits-Abstimmung gegen OCR-Fehler ---
# Pro Chat-Zeile (per Timestamp identifiziert) sammeln wir über ein
# kurzes Zeitfenster ALLE Champion-Lesarten und übernehmen am Ende die
# häufigste. Das filtert "Fantasien" (einmalige Fehllesungen) UND fängt
# echte Flashes, selbst wenn einzelne Reads daneben liegen.
VOTE_WINDOW = 1.6     # Sekunden sammeln, bevor entschieden wird
MIN_VOTES   = 2       # so oft muss der Gewinner-Champ gelesen worden sein
# Timer nur für Zeilen MIT erkennbarem Timestamp (kill für Hintergrund-Müll)
REQUIRE_STAMP = True

# Zeilen, die einen dieser Texte enthalten, werden ignoriert
# (Countdown-/Erinnerungs-Pings, keine frischen Flashes).
IGNORE_PHRASES = ["wait for", "has selected", "quest complete", "/help"]

# ---- Auto-Copy ---------------------------------------------
# League akzeptiert KEIN Strg+V im Chat -> Auto-Copy standardmäßig AUS
# (konservativ, belegt nicht dauernd die Windows-Zwischenablage).
# Zum Teilen im Chat lieber den Tipp-Hotkey (siehe unten) verwenden.
AUTO_COPY_DEFAULT = False

# ---- Chat-Tippen (Windows) ---------------------------------
# Da League kein Einfügen erlaubt, werden die Timer per Tastendruck
# ins Chatfenster getippt. League muss dabei im Vordergrund sein.
# Hotkey: am besten eine in LoL UNBELEGTE Taste wählen (Standard F8).
CHAT_TYPE_HOTKEY  = "f8"
PASTE_TO_ALL_CHAT = False   # True = All-Chat (Shift+Enter)

# ---- Minimal-HUD -------------------------------------------
HUD_X = 1150
HUD_Y = 60
HUD_ALPHA = 0.85
HUD_DEFAULT = True

# ---- GUI-Fenster -------------------------------------------
WINDOW_X = 2150
WINDOW_Y = 80
ALWAYS_ON_TOP_DEFAULT = True

# ---- OCR Preprocessing -------------------------------------
OCR_SCALE_FACTOR = 3          # Bild vergrößern für bessere OCR-Genauigkeit
OCR_CONFIG       = "--psm 6"  # Tesseract Page Segmentation Mode

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
