import time
import threading

from capture import capture_chat
from ocr import read_chat
from parser import parse_chat
from timers import TimerManager
from overlay import FlashOverlay
from alert import AlertSystem
from chat_paste import paste_to_chat
from config import (
    SCAN_INTERVAL,
    ALERT_SOUND,
    PASTE_HOTKEY,
    RESET_HOTKEY,
    QUIT_HOTKEY,
)

try:
    import keyboard
    _HAS_KEYBOARD = True
except Exception:
    _HAS_KEYBOARD = False

manager = TimerManager()
overlay = FlashOverlay()
alert = AlertSystem(ALERT_SOUND)
running = True

# Bereits getrackte Spell-Pings nicht doppelt zählen.
seen = set()


def scan_loop():
    while running:
        try:
            img = capture_chat()
            text = read_chat(img)
            events = parse_chat(text)

            for e in events:
                key = f"{e['champion']}_{e['spell']}"
                if key not in seen:
                    seen.add(key)
                    manager.add(e["champion"], e["spell"], e["cooldown"])
                    alert.trigger()

            # Seen-Cache mit aktiven Timern abgleichen, damit ein
            # erneuter Ping nach Ablauf wieder getrackt wird.
            active_keys = {f"{t.champion}_{t.spell}" for t in manager.get_active()}
            seen.intersection_update(active_keys)
        except Exception as e:
            print(f"[SCAN] Fehler: {e}")

        time.sleep(SCAN_INTERVAL)


def on_paste():
    paste_to_chat(manager.chat_line())


def on_reset():
    manager.reset()
    seen.clear()


def on_quit():
    global running
    running = False


def register_hotkeys():
    if not _HAS_KEYBOARD:
        print("[HOTKEY] 'keyboard' nicht verfügbar — Hotkeys deaktiviert.")
        return
    keyboard.add_hotkey(PASTE_HOTKEY, on_paste)
    keyboard.add_hotkey(RESET_HOTKEY, on_reset)
    keyboard.add_hotkey(QUIT_HOTKEY, on_quit)
    print(f"[HOTKEY] {PASTE_HOTKEY.upper()}=Chat  "
          f"{RESET_HOTKEY.upper()}=Reset  {QUIT_HOTKEY.upper()}=Quit")


def main():
    global running
    print("=" * 50)
    print(" Flash Tracker gestartet")
    print(f" Paste-Hotkey: {PASTE_HOTKEY.upper()}  ->  z.B. 'jhin 2 40, lux 5 39'")
    print("=" * 50)

    register_hotkeys()

    scanner = threading.Thread(target=scan_loop, daemon=True)
    scanner.start()

    # Overlay-Update-Loop läuft im Main-Thread (tkinter-Anforderung).
    try:
        while running:
            overlay.update(manager.get_active())
            time.sleep(0.1)
    except KeyboardInterrupt:
        running = False
    finally:
        overlay.destroy()
        print("[EXIT] Flash Tracker beendet.")


if __name__ == "__main__":
    main()
