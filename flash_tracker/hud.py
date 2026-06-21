"""Minimales, immer-oben HUD: nur Champ + runterzählender Flash-Timer.

Rahmenlos, halbtransparent, mit der Maus verschiebbar. Zeigt z.B.:
    jhin ⚡ 4:47
    anivia ⚡ 3:12 ?
('?' = nur Ping/Schätzung, noch nicht bestätigt)
"""
import tkinter as tk
from config import HUD_X, HUD_Y, HUD_ALPHA

BG = "#0a0c10"


class MiniHUD:
    def __init__(self, root):
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", HUD_ALPHA)
        self.win.configure(bg=BG)
        self.win.geometry(f"+{HUD_X}+{HUD_Y}")

        self.text = tk.Text(
            self.win, width=16, height=6, bg=BG, fg="#00ff88",
            font=("Consolas", 16, "bold"), bd=0, padx=10, pady=8,
            highlightthickness=0, cursor="fleur", wrap="none",
        )
        self.text.pack(fill="both", expand=True)
        self.text.tag_config("ready", foreground="#ff5555")   # < 30s
        self.text.tag_config("soon", foreground="#ffcc44")    # < 60s
        self.text.tag_config("ok", foreground="#00ff88")
        self.text.config(state="disabled")

        # Verschiebbar machen.
        for w in (self.win, self.text):
            w.bind("<Button-1>", self._start)
            w.bind("<B1-Motion>", self._drag)
        self._ox = self._oy = 0
        self.visible = True

    def _start(self, e):
        self._ox, self._oy = e.x_root - self.win.winfo_x(), e.y_root - self.win.winfo_y()

    def _drag(self, e):
        self.win.geometry(f"+{e.x_root - self._ox}+{e.y_root - self._oy}")

    def update(self, timers):
        if not self.visible:
            return
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        if not timers:
            self.text.insert("end", "— keine Flashes —", "ok")
        else:
            for t in timers:
                m, s = t.mmss()
                icon = "⚡" if t.spell == "flash" else "•"
                mark = "" if t.certain else " ?"
                line = f"{t.champion.lower()} {icon} {m}:{s:02d}{mark}\n"
                rem = t.remaining()
                tag = "ready" if rem < 30 else ("soon" if rem < 60 else "ok")
                self.text.insert("end", line, tag)
        self.text.config(state="disabled")

    def show(self):
        self.win.deiconify()
        self.visible = True

    def hide(self):
        self.win.withdraw()
        self.visible = False
