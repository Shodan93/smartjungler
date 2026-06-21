# Flash Tracker — League of Legends Summoner Spell Timer

Scannt den League-Chat per OCR, erkennt Summoner-Spell-Pings
(`00:06 Scripter02 (Diana): Jhin Flash`), startet automatisch Timer
und zeigt sie in einem Always-on-Top-Overlay.

Zusätzlich kannst du per Hotkey **alle laufenden Timer authentisch in
den League-Chat tippen** lassen:

```
jhin 2 40, lux 5 39, diana 0 02
```

(alles klein, komma-getrennt — sieht aus wie von Hand getippt)

---

## Voraussetzungen (Windows, 2560×1440)

1. **Tesseract OCR installieren**
   https://github.com/UB-Mannheim/tesseract/wiki → Windows-Installer,
   Standard-Pfad lassen (`C:\Program Files\Tesseract-OCR\`).
   Falls du einen anderen Pfad wählst: `TESSERACT_CMD` in `config.py` anpassen.

2. **Python-Pakete installieren**
   ```bash
   pip install -r requirements.txt
   ```

> Hinweis: Die `keyboard`-Bibliothek braucht unter Windows i.d.R.
> **Administrator-Rechte**, damit Hotkeys/Tippen im Spiel funktionieren.
> Starte die Konsole als Administrator.

---

## Start (Schnellstart, direkt ins Spiel)

```bash
cd flash_tracker
python main.py
```

Reihenfolge:

1. League starten und in ein Spiel gehen.
2. (Einmalig) `python calibrate.py` ausführen → Rechteck um den Chat
   ziehen → ausgegebene `CHAT_REGION`-Werte in `config.py` eintragen.
3. `python main.py` starten.
4. Ein Mitspieler/Gegner pingt einen Spell im Chat → Timer erscheint
   automatisch im Overlay oben rechts.

---

## Hotkeys (funktionieren auch im Spiel)

| Taste | Funktion                                                        |
|-------|-----------------------------------------------------------------|
| `F8`  | Tippt alle laufenden Timer in den Chat: `jhin 2 40, lux 5 39`    |
| `F9`  | Setzt alle Timer zurück (z.B. neues Spiel)                       |
| `F10` | Beendet das Programm                                             |

Tasten lassen sich in `config.py` ändern (`PASTE_HOTKEY`, `RESET_HOTKEY`,
`QUIT_HOTKEY`). Mit `PASTE_TO_ALL_CHAT = True` wird in den All-Chat statt
Team-Chat geschrieben.

---

## Kalibrierung

`python calibrate.py` macht einen Vollbild-Screenshot. Ziehe ein
Rechteck um das Chatfenster — die passenden `CHAT_REGION`-Werte werden in
der Konsole ausgegeben.

---

## Dateien

| Datei            | Zweck                                  |
|------------------|----------------------------------------|
| `main.py`        | Hauptloop, Hotkeys, Overlay            |
| `capture.py`     | Chat-Screenshot (mss)                  |
| `ocr.py`         | Tesseract OCR + Preprocessing          |
| `parser.py`      | Regex Spell-Erkennung                  |
| `timers.py`      | Timer-Verwaltung + Chat-Format         |
| `overlay.py`     | Transparentes Always-on-Top Overlay    |
| `alert.py`       | Audio-Alert                            |
| `chat_paste.py`  | Tippt Timer in den League-Chat         |
| `calibrate.py`   | Chat-Region bestimmen                  |
| `config.py`      | Alle Einstellungen                     |

---

## Troubleshooting

- **OCR erkennt nichts** → Chat-Region neu kalibrieren; ggf.
  `OCR_SCALE_FACTOR` erhöhen oder Threshold in `ocr.py` anpassen.
- **Hotkeys reagieren nicht** → Konsole als Administrator starten.
- **Tesseract not found** → `TESSERACT_CMD` in `config.py` prüfen.
- **Falsche Champion-Namen** (z.B. „Jh1n") → Phase-2-Feature
  Fuzzy-Matching; aktuell wird der erkannte Name 1:1 verwendet.
