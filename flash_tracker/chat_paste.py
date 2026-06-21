"""Tippt die laufenden Timer ins League-Chatfenster.

League akzeptiert kein Ctrl+V — daher tippen wir die Zeichen per
Windows-API (siehe wininput.py). League muss im Vordergrund sein, wenn
der Hotkey gedrückt wird. Läuft in einem eigenen Thread, damit die GUI
während des Tippens nicht einfriert.
"""
import time
import threading

from wininput import HAS_WIN_INPUT, press_key, type_text, VK_RETURN
from config import PASTE_TO_ALL_CHAT


def send_to_chat(text):
    if not text:
        return False
    if not HAS_WIN_INPUT:
        print(f"[CHAT] (kein Windows-Input) würde tippen: {text}")
        return False

    def run():
        # Chat öffnen.
        if PASTE_TO_ALL_CHAT:
            # Shift+Enter = All-Chat
            from wininput import _send, KEYEVENTF_KEYUP
            VK_SHIFT = 0x10
            _send(vk=VK_SHIFT)
            press_key(VK_RETURN)
            _send(vk=VK_SHIFT, flags=KEYEVENTF_KEYUP)
        else:
            press_key(VK_RETURN)
        time.sleep(0.15)
        type_text(text)
        time.sleep(0.10)
        press_key(VK_RETURN)   # absenden
        print(f"[CHAT] Getippt: {text}")

    threading.Thread(target=run, daemon=True).start()
    return True
