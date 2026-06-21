"""Flash Tracker — kleine GUI.

- Zeigt laufende Spell-Timer live an.
- Button "In Zwischenablage" kopiert alle Timer im authentischen
  Format ("jhin 2 40, lux 5 39") in die Zwischenablage -> mit Ctrl+V
  im League-Chat einfügen.
- Manuelles Hinzufügen von Timern (auch ohne OCR/League testbar).
- OCR-Scan optional zuschaltbar.
"""
import random
import tkinter as tk
from tkinter import ttk

from timers import TimerManager
from scanner import Scanner
from alert import AlertSystem
from hud import MiniHUD
from chat_paste import send_to_chat
from wininput import HAS_WIN_INPUT, key_down, name_to_vk
from config import (
    SPELLS,
    SPELL_COOLDOWNS,
    WINDOW_X,
    WINDOW_Y,
    ALWAYS_ON_TOP_DEFAULT,
    SCAN_ENABLED_DEFAULT,
    AUTO_COPY_DEFAULT,
    ALERT_SOUND,
    CHAT_TYPE_HOTKEY,
    HUD_DEFAULT,
)

BG = "#11141a"
FG = "#e8e8e8"
ACCENT = "#00ff88"
DIM = "#7a8290"

DEMO_CHAMPS = ["jhin", "lux", "diana", "ahri", "thresh", "leesin", "kaisa"]


class FlashTrackerGUI:
    def __init__(self):
        self.manager = TimerManager()
        self.alert = AlertSystem(ALERT_SOUND)
        self.scanner = Scanner(self.manager, on_event=lambda c, s: self.alert.trigger())

        self._last_clip = None
        self._hotkey_vk = name_to_vk(CHAT_TYPE_HOTKEY)
        self._hotkey_was_down = False

        self.root = tk.Tk()
        self.root.title("Flash Tracker")
        self.root.configure(bg=BG)
        self.root.geometry(f"320x540+{WINDOW_X}+{WINDOW_Y}")
        self.root.attributes("-topmost", ALWAYS_ON_TOP_DEFAULT)

        self.hud = MiniHUD(self.root)
        if not HUD_DEFAULT:
            self.hud.hide()

        self._build_ui()
        self._tick()

    # ----------------------------------------------------- UI
    def _build_ui(self):
        # Kopfzeile
        tk.Label(
            self.root, text="⚡ Flash Tracker", bg=BG, fg=ACCENT,
            font=("Consolas", 15, "bold"), anchor="w", padx=12, pady=8,
        ).pack(fill="x")

        # Timer-Anzeige
        self.timer_box = tk.Label(
            self.root, text="— keine Timer —", bg="#0a0c10", fg=FG,
            font=("Consolas", 13, "bold"), justify="left", anchor="nw",
            padx=12, pady=10,
        )
        self.timer_box.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Vorschau der Chat-Zeile
        self.preview = tk.Label(
            self.root, text="", bg=BG, fg=DIM,
            font=("Consolas", 10), anchor="w", justify="left",
            wraplength=300, padx=12,
        )
        self.preview.pack(fill="x")

        # Haupt-Buttons
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=10, pady=6)
        self._btn(row, "📋 In Zwischenablage", self.copy_to_clipboard,
                  bg=ACCENT, fg="#062012").pack(side="left", expand=True, fill="x")

        row2 = tk.Frame(self.root, bg=BG)
        row2.pack(fill="x", padx=10, pady=(0, 6))
        self._btn(row2, "Demo", self.add_demo).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self._btn(row2, "Reset", self.reset).pack(side="left", expand=True, fill="x", padx=(4, 0))

        # Manuelles Hinzufügen
        sep = tk.Frame(self.root, bg="#222831", height=1)
        sep.pack(fill="x", padx=10, pady=4)
        tk.Label(self.root, text="Manuell hinzufügen:", bg=BG, fg=DIM,
                 font=("Consolas", 9), anchor="w", padx=12).pack(fill="x")

        add = tk.Frame(self.root, bg=BG)
        add.pack(fill="x", padx=10, pady=4)
        self.champ_var = tk.StringVar()
        ent = tk.Entry(add, textvariable=self.champ_var, width=10,
                       bg="#0a0c10", fg=FG, insertbackground=FG,
                       font=("Consolas", 11), relief="flat")
        ent.pack(side="left", ipady=3, padx=(0, 4))
        ent.bind("<Return>", lambda e: self.add_manual())

        self.spell_var = tk.StringVar(value=SPELLS[0])
        ttk.Combobox(add, textvariable=self.spell_var, values=SPELLS,
                     width=8, state="readonly").pack(side="left", padx=(0, 4))
        self._btn(add, "+", self.add_manual, width=3).pack(side="left")

        # Steuerzeile unten
        ctrl = tk.Frame(self.root, bg=BG)
        ctrl.pack(fill="x", padx=10, pady=(6, 4))

        self.scan_var = tk.BooleanVar(value=SCAN_ENABLED_DEFAULT)
        tk.Checkbutton(
            ctrl, text="OCR-Scan", variable=self.scan_var, command=self.toggle_scan,
            bg=BG, fg=FG, selectcolor="#0a0c10", activebackground=BG,
            activeforeground=FG, font=("Consolas", 10),
        ).pack(side="left")

        self.top_var = tk.BooleanVar(value=ALWAYS_ON_TOP_DEFAULT)
        tk.Checkbutton(
            ctrl, text="Immer oben", variable=self.top_var, command=self.toggle_top,
            bg=BG, fg=FG, selectcolor="#0a0c10", activebackground=BG,
            activeforeground=FG, font=("Consolas", 10),
        ).pack(side="left", padx=8)

        self.hud_var = tk.BooleanVar(value=HUD_DEFAULT)
        tk.Checkbutton(
            ctrl, text="HUD", variable=self.hud_var, command=self.toggle_hud,
            bg=BG, fg=FG, selectcolor="#0a0c10", activebackground=BG,
            activeforeground=FG, font=("Consolas", 10),
        ).pack(side="left")

        self.autocopy_var = tk.BooleanVar(value=AUTO_COPY_DEFAULT)
        tk.Checkbutton(
            ctrl, text="Auto-Copy", variable=self.autocopy_var,
            bg=BG, fg=FG, selectcolor="#0a0c10", activebackground=BG,
            activeforeground=FG, font=("Consolas", 10),
        ).pack(side="left", padx=8)

        # Hinweis zum Team-Sharing.
        from config import CHAT_TYPING_ENABLED
        if CHAT_TYPING_ENABLED and HAS_WIN_INPUT:
            hint = f"Chat offen + [{CHAT_TYPE_HOTKEY.upper()}] -> tippt Timer (Spielzeit)"
        else:
            hint = "Team-Sharing: Spielzeit am HUD/Liste ablesen u. selbst tippen"
        tk.Label(self.root, text=hint, bg=BG, fg=DIM, font=("Consolas", 9),
                 anchor="w", justify="left", wraplength=300, padx=12).pack(fill="x")

        self.status = tk.Label(self.root, text="", bg=BG, fg=DIM,
                               font=("Consolas", 9), anchor="w", padx=12)
        self.status.pack(fill="x", side="bottom", pady=(0, 4))

        if SCAN_ENABLED_DEFAULT:
            self.toggle_scan()

    def _btn(self, parent, text, cmd, bg="#1c2531", fg=FG, width=None):
        return tk.Button(
            parent, text=text, command=cmd, bg=bg, fg=fg, width=width,
            activebackground="#2a3645", activeforeground=fg, relief="flat",
            font=("Consolas", 10, "bold"), cursor="hand2", padx=6, pady=6,
            borderwidth=0,
        )

    # ------------------------------------------------- Aktionen
    def copy_to_clipboard(self):
        text = self.manager.chat_line()
        if not text:
            self._flash_status("Keine Timer zum Kopieren")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # hält den Inhalt nach Programm-Fokuswechsel
        self._flash_status("Kopiert! Im Chat mit Strg+V einfügen.")

    def add_manual(self):
        champ = self.champ_var.get().strip()
        spell = self.spell_var.get().strip().lower()
        if not champ:
            self._flash_status("Champion-Name eingeben")
            return
        cd = SPELL_COOLDOWNS.get(spell, 300)
        up = (self.scanner.game_now + cd) if self.scanner.game_now else None
        # Manuell = sicher (überschreibt eine evtl. unsichere Schätzung).
        self.manager.add(champ, spell, cd, certain=True, up_game=up)
        self.champ_var.set("")
        self._flash_status(f"{champ} {spell} hinzugefügt")

    def add_demo(self):
        champ = random.choice(DEMO_CHAMPS)
        spell = random.choice(["flash", "ignite", "teleport"])
        cd = SPELL_COOLDOWNS[spell]
        up = (self.scanner.game_now + cd) if self.scanner.game_now else None
        self.manager.add(champ, spell, cd, certain=True, up_game=up)
        self.alert.trigger()
        self._flash_status(f"Demo: {champ} {spell}")

    def reset(self):
        self.manager.reset()
        self.scanner.reset()
        self._last_clip = None
        self._flash_status("Alle Timer zurückgesetzt")

    def toggle_scan(self):
        if self.scan_var.get():
            ok, msg = self.scanner.start()
            if not ok:
                self.scan_var.set(False)
                self._flash_status(f"OCR aus: {msg}")
            else:
                self._flash_status("OCR-Scan aktiv")
        else:
            self.scanner.stop()
            self._flash_status("OCR-Scan aus")

    def toggle_top(self):
        self.root.attributes("-topmost", self.top_var.get())

    def toggle_hud(self):
        if self.hud_var.get():
            self.hud.show()
        else:
            self.hud.hide()

    def _check_hotkey(self):
        """Pollt die Tipp-Taste; tippt bei Tastendruck die Timer in League."""
        from config import CHAT_TYPING_ENABLED
        if not CHAT_TYPING_ENABLED or not HAS_WIN_INPUT or self._hotkey_vk is None:
            return
        down = key_down(self._hotkey_vk)
        if down and not self._hotkey_was_down:
            if send_to_chat(self.manager.chat_line()):
                self._flash_status("In League-Chat getippt")
        self._hotkey_was_down = down

    def _flash_status(self, msg):
        self.status.config(text=msg)

    # ------------------------------------------------- Loop
    def _tick(self):
        timers = self.manager.get_active()
        line = self.manager.chat_line()
        if timers:
            self.timer_box.config(text="\n".join(t.display() for t in timers))
            self.preview.config(text="Chat: " + line)
        else:
            self.timer_box.config(text="— keine Timer —")
            self.preview.config(text="")

        self.hud.update(timers)
        self._check_hotkey()

        # Auto-Copy (standardmäßig aus): Zwischenablage aktuell halten.
        if self.autocopy_var.get() and line and line != self._last_clip:
            self.root.clipboard_clear()
            self.root.clipboard_append(line)
            self._last_clip = line

        self.root.after(150, self._tick)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FlashTrackerGUI().run()
