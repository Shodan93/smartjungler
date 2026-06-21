"""Tippt die Timer ins League-Chatfenster.

League akzeptiert kein Ctrl+V — daher tippen wir die Zeichen per
Windows-API (siehe wininput.py). Läuft in einem eigenen Thread, damit
die GUI nicht einfriert.

Modus CHAT_ALREADY_OPEN: der Chat ist beim Hotkey schon offen. Das
Trigger-Zeichen (z.B. 'z') landet dann im Eingabefeld und wird per
Backspace wieder entfernt, bevor die Timer getippt werden.
"""
import time
import threading

from wininput import HAS_WIN_INPUT, press_key, type_text, VK_RETURN, VK_BACK
from config import CHAT_ALREADY_OPEN, CHAT_AUTO_SEND, PASTE_TO_ALL_CHAT


def send_to_chat(text):
    if not text:
        return False
    if not HAS_WIN_INPUT:
        print(f"[CHAT] (kein Windows-Input) würde tippen: {text}")
        return False

    def run():
        if CHAT_ALREADY_OPEN:
            # Trigger-Zeichen (z.B. 'z') aus dem offenen Eingabefeld löschen.
            time.sleep(0.05)
            press_key(VK_BACK)
            time.sleep(0.05)
        else:
            # Chat erst öffnen.
            if PASTE_TO_ALL_CHAT:
                from wininput import _send, KEYEVENTF_KEYUP
                VK_SHIFT = 0x10
                _send(vk=VK_SHIFT)
                press_key(VK_RETURN)
                _send(vk=VK_SHIFT, flags=KEYEVENTF_KEYUP)
            else:
                press_key(VK_RETURN)
            time.sleep(0.15)

        type_text(text)

        if CHAT_AUTO_SEND:
            time.sleep(0.08)
            press_key(VK_RETURN)
        print(f"[CHAT] Getippt: {text}")

    threading.Thread(target=run, daemon=True).start()
    return True
