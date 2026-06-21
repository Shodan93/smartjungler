"""Tippt die laufenden Timer ins League-Chatfenster.

Format (authentisch, alles klein):  'jhin 2 40, lux 5 39'

Verwendet die 'keyboard'-Bibliothek, um Tastendrücke an das aktive
Fenster (League) zu schicken. League muss im Vordergrund sein, wenn
der Hotkey gedrückt wird.
"""
import time

try:
    import keyboard
    _HAS_KEYBOARD = True
except Exception:
    _HAS_KEYBOARD = False

from config import CHAT_OPEN_KEY, PASTE_TO_ALL_CHAT


def paste_to_chat(text):
    """Öffnet den Chat, tippt den Text und sendet ihn ab."""
    if not text:
        print("[CHAT] Keine aktiven Timer zum Senden")
        return
    if not _HAS_KEYBOARD:
        print("[CHAT] 'keyboard' nicht verfügbar — kann nicht tippen.")
        print(f"[CHAT] (würde senden): {text}")
        return

    # Chat öffnen. All-Chat = Shift+Enter, Team-Chat = Enter.
    if PASTE_TO_ALL_CHAT:
        keyboard.send("shift+enter")
    else:
        keyboard.send(CHAT_OPEN_KEY)

    time.sleep(0.08)
    # Text als echte Tastatureingabe schreiben.
    keyboard.write(text, delay=0.01)
    time.sleep(0.05)
    # Absenden.
    keyboard.send("enter")
    print(f"[CHAT] Gesendet: {text}")
