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
from config import (
    SPELLS,
    SPELL_COOLDOWNS,
    WINDOW_X,
    WINDOW_Y,
    ALWAYS_ON_TOP_DEFAULT,
    SCAN_ENABLED_DEFAULT,
    AUTO_COPY_DEFAULT,
    ALERT_SOUND,
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

        self.root = tk.Tk()
        self.root.title("Flash Tracker")
        self.root.configure(bg=BG)
        self.root.geometry(f"320x510+{WINDOW_X}+{WINDOW_Y}")
        self.root.attributes("-topmost", ALWAYS_ON_TOP_DEFAULT)

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

        self.autocopy_var = tk.BooleanVar(value=AUTO_COPY_DEFAULT)
        tk.Checkbutton(
            ctrl, text="Auto-Copy", variable=self.autocopy_var,
            bg=BG, fg=FG, selectcolor="#0a0c10", activebackground=BG,
            activeforeground=FG, font=("Consolas", 10),
        ).pack(side="left")

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
        # Manuell = sicher (überschreibt eine evtl. unsichere Schätzung).
        self.manager.add(champ, spell, cd, certain=True)
        self.champ_var.set("")
        self._flash_status(f"{champ} {spell} hinzugefügt")

    def add_demo(self):
        champ = random.choice(DEMO_CHAMPS)
        spell = random.choice(["flash", "ignite", "teleport"])
        self.manager.add(champ, spell, SPELL_COOLDOWNS[spell], certain=True)
        self.alert.trigger()
        self._flash_status(f"Demo: {champ} {spell}")

    def reset(self):
        self.manager.reset()
        self.scanner.processed.clear()
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

        # Auto-Copy: Zwischenablage laufend aktuell halten.
        if self.autocopy_var.get() and line and line != self._last_clip:
            self.root.clipboard_clear()
            self.root.clipboard_append(line)
            self._last_clip = line

        self.root.after(200, self._tick)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FlashTrackerGUI().run()
