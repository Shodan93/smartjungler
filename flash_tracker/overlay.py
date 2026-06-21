import tkinter as tk
from config import OVERLAY_X, OVERLAY_Y, PASTE_HOTKEY, RESET_HOTKEY


class FlashOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.configure(bg="black")
        self.root.geometry(f"300x420+{OVERLAY_X}+{OVERLAY_Y}")

        self.title = tk.Label(
            self.root,
            text="⚡ Flash Tracker",
            bg="black",
            fg="#00ff88",
            font=("Consolas", 13, "bold"),
            anchor="w",
            padx=10,
            pady=4,
        )
        self.title.pack(fill="x")

        self.label = tk.Label(
            self.root,
            text="— kein Spell gesichtet —",
            bg="black",
            fg="#e0e0e0",
            font=("Consolas", 13, "bold"),
            justify="left",
            anchor="nw",
            padx=10,
            pady=5,
        )
        self.label.pack(fill="both", expand=True)

        self.hint = tk.Label(
            self.root,
            text=f"[{PASTE_HOTKEY.upper()}] Chat  ·  [{RESET_HOTKEY.upper()}] Reset",
            bg="black",
            fg="#777777",
            font=("Consolas", 9),
            anchor="w",
            padx=10,
            pady=4,
        )
        self.hint.pack(fill="x", side="bottom")

    def update(self, timers):
        if not timers:
            self.label.config(text="— kein Spell gesichtet —")
        else:
            lines = [t.display() for t in timers]
            self.label.config(text="\n".join(lines))
        self.root.update_idletasks()
        self.root.update()

    def destroy(self):
        try:
            self.root.destroy()
        except Exception:
            pass
