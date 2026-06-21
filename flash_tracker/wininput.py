"""Windows-Tastatureingabe über reines Win32-API (ctypes).

Wird genutzt, um die Timer ins League-Chatfenster zu TIPPEN (League
akzeptiert kein Ctrl+V). Braucht keine Admin-Rechte und keine externen
Pakete. Auf Nicht-Windows-Systemen sind alle Funktionen No-Ops, damit
die GUI trotzdem startet (zum Testen).
"""
import sys
import time
import ctypes
from ctypes import wintypes

HAS_WIN_INPUT = False
_user32 = None
if sys.platform == "win32":
    try:
        _user32 = ctypes.WinDLL("user32", use_last_error=True)
        HAS_WIN_INPUT = True
    except Exception:
        HAS_WIN_INPUT = False

if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
else:
    ULONG_PTR = ctypes.c_ulong


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_RETURN = 0x0D
VK_BACK = 0x08


def _send(vk=0, scan=0, flags=0):
    if not HAS_WIN_INPUT:
        return
    ki = KEYBDINPUT(vk, scan, flags, 0, 0)
    inp = INPUT(INPUT_KEYBOARD, _INPUTUNION(ki=ki))
    _user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def press_key(vk):
    """Drückt + löst eine virtuelle Taste (z.B. VK_RETURN)."""
    _send(vk=vk, flags=0)
    _send(vk=vk, flags=KEYEVENTF_KEYUP)


VK_CONTROL = 0x11


def chord_ctrl(vk):
    """Strg + Taste (z.B. Strg+A zum Alles-Markieren)."""
    _send(vk=VK_CONTROL)
    _send(vk=vk)
    _send(vk=vk, flags=KEYEVENTF_KEYUP)
    _send(vk=VK_CONTROL, flags=KEYEVENTF_KEYUP)


def is_printable_key(name):
    """True, wenn die Taste ein Zeichen erzeugt (Buchstabe/Ziffer/Space)."""
    name = (name or "").strip().lower()
    return len(name) == 1 or name in ("space", "tab")


def type_char(ch):
    """Tippt ein einzelnes Unicode-Zeichen (layout-unabhängig)."""
    code = ord(ch)
    _send(scan=code, flags=KEYEVENTF_UNICODE)
    _send(scan=code, flags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP)


def type_text(text, delay=0.006):
    """Tippt einen ganzen String Zeichen für Zeichen."""
    for ch in text:
        type_char(ch)
        time.sleep(delay)


def key_down(vk):
    """True, wenn die Taste vk gerade gedrückt ist (global)."""
    if not HAS_WIN_INPUT:
        return False
    return bool(_user32.GetAsyncKeyState(vk) & 0x8000)


# Tastennamen -> Virtual-Key-Code (für die Hotkey-Konfiguration).
def name_to_vk(name):
    name = name.strip().lower()
    specials = {
        "enter": 0x0D, "space": 0x20, "tab": 0x09,
        "insert": 0x2D, "delete": 0x2E, "home": 0x24,
        "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
    }
    if name in specials:
        return specials[name]
    if name.startswith("f") and name[1:].isdigit():
        n = int(name[1:])
        if 1 <= n <= 12:
            return 0x70 + (n - 1)   # F1=0x70 .. F12=0x7B
    if len(name) == 1:
        return ord(name.upper())    # Buchstaben/Ziffern
    return None
