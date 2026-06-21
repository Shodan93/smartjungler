# Flash Tracker — League of Legends Summoner Spell Timer (GUI)

Kleine **GUI**, die Summoner-Spell-Timer verwaltet und sie dir in die
**Zwischenablage** legt, damit du sie mit **Strg+V** in den League-Chat
einfügen kannst (League akzeptiert keine simulierten Tastatureingaben —
deshalb Clipboard statt Auto-Tippen).

Format der kopierten Zeile (alles klein, komma-getrennt):

```
jhin 2 40, lux 5 39, diana 0 02
```

Optional kann zusätzlich der League-Chat per **OCR** automatisch
gescannt werden (`00:06 Scripter02 (Diana): Jhin Flash` → Timer startet
von selbst).

---

## Schnellstart (zum Testen — ganz ohne League/OCR)

Du brauchst nur Python. tkinter ist beim normalen Windows-Installer
bereits dabei.

```bash
cd flash_tracker
python main.py
```

Es öffnet sich ein kleines Fenster. Dort kannst du **sofort testen**:

1. **„Demo"** klicken → fügt einen zufälligen Timer hinzu.
2. Oder unten **manuell** einen Champion eintippen, Spell wählen, **„+"**.
3. **„📋 In Zwischenablage"** klicken → die Zeile (`jhin 2 40, ...`)
   liegt in der Zwischenablage. Irgendwo mit **Strg+V** einfügen zum Prüfen.
4. **„Reset"** leert alle Timer.

> Für diesen Testlauf musst du **nichts** zusätzlich installieren
> (kein Tesseract, kein opencv).

---

## Bedienung im Spiel

1. Flash Tracker starten: `python main.py`
2. Fenster z.B. auf den zweiten Monitor schieben (oder „Immer oben" an).
3. Timer pflegen — zwei Wege:
   - **Manuell**: Champion + Spell eintragen, **„+"**. (zuverlässigster Weg)
   - **Automatisch (OCR)**: Häkchen **„OCR-Scan"** setzen (siehe unten).
4. Wenn du den Team-Stand teilen willst: **„📋 In Zwischenablage"**,
   dann im League-Chat (Enter) **Strg+V** und absenden.

---

## Optional: Automatischer OCR-Scan

Nur nötig, wenn die Timer automatisch aus dem Chat gelesen werden sollen.

1. **Tesseract OCR installieren**
   https://github.com/UB-Mannheim/tesseract/wiki → Windows-Installer,
   Standard-Pfad lassen (`C:\Program Files\Tesseract-OCR\`).
   Anderer Pfad? → `TESSERACT_CMD` in `config.py` anpassen.
2. **OCR-Pakete installieren**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Chat-Region kalibrieren** (League im Spiel, Chat sichtbar):
   ```bash
   python calibrate.py
   ```
   Rechteck um das Chatfenster ziehen → ausgegebene `CHAT_REGION`-Werte
   in `config.py` eintragen.
4. In der GUI das Häkchen **„OCR-Scan"** setzen. Erkennt das Tool keine
   OCR-Pakete, bleibt das Häkchen aus und es erscheint ein Hinweis —
   manuelles Eintragen funktioniert trotzdem.

---

## GUI-Elemente

| Element              | Funktion                                                |
|----------------------|---------------------------------------------------------|
| Timer-Liste          | Laufende Timer, nach Restzeit sortiert                  |
| „Chat: …" Vorschau   | Genau der Text, der in die Zwischenablage kopiert wird  |
| 📋 In Zwischenablage | Kopiert die Chat-Zeile → mit Strg+V einfügen            |
| Demo                 | Fügt einen Beispiel-Timer hinzu (zum Testen)            |
| Reset                | Löscht alle Timer                                       |
| Champion + Spell + „+"| Timer manuell hinzufügen                               |
| OCR-Scan             | Automatisches Chat-Lesen an/aus                         |
| Immer oben           | Fenster bleibt über League                              |

---

## Dateien

| Datei           | Zweck                                  |
|-----------------|----------------------------------------|
| `main.py`       | Start der GUI                          |
| `gui.py`        | Die GUI (Tkinter) + Clipboard          |
| `scanner.py`    | Optionaler OCR-Scan-Thread             |
| `capture.py`    | Chat-Screenshot (mss)                  |
| `ocr.py`        | Tesseract OCR + Preprocessing          |
| `parser.py`     | Regex Spell-Erkennung                  |
| `timers.py`     | Timer-Verwaltung + Chat-Format         |
| `alert.py`      | Optionaler Audio-Alert                 |
| `calibrate.py`  | Chat-Region bestimmen                  |
| `config.py`     | Alle Einstellungen                     |

---

## Troubleshooting

- **`ModuleNotFoundError: tkinter`** → kommt auf normalen Windows-Python
  nicht vor; nur bei minimalen Installationen. tkinter ist Teil der
  Standard-Python-Installation.
- **OCR-Häkchen springt zurück** → OCR-Pakete oder Tesseract fehlen; per
  `pip install -r requirements.txt` nachinstallieren. Manuell geht weiter.
- **OCR liest Mist** → Chat-Region neu kalibrieren; `OCR_SCALE_FACTOR`
  erhöhen oder Threshold in `ocr.py` anpassen.
- **Clipboard leer nach Schließen** → einfach Tool offen lassen, bis du
  eingefügt hast.
