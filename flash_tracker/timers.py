import time


class SpellTimer:
    def __init__(self, champion, spell, cooldown):
        self.champion = champion
        self.spell = spell
        self.cooldown = cooldown
        self.started = time.time()

    def remaining(self):
        elapsed = time.time() - self.started
        return max(0, self.cooldown - elapsed)

    def is_done(self):
        return self.remaining() <= 0

    def mmss(self):
        """Verbleibende Zeit als (Minuten, Sekunden)."""
        r = int(round(self.remaining()))
        return r // 60, r % 60

    def display(self):
        m, s = self.mmss()
        spell_icon = "⚡" if self.spell == "flash" else "•"
        return f"{self.champion} {spell_icon} {self.spell.capitalize()} — {m}:{s:02d}"

    def chat_format(self):
        """Authentisches Chat-Format, alles klein: 'jhin 2 40'."""
        m, s = self.mmss()
        return f"{self.champion.lower()} {m} {s:02d}"


class TimerManager:
    def __init__(self):
        self.timers = {}  # key: "champion_spell"

    def add(self, champion, spell, cooldown):
        key = f"{champion}_{spell}"
        # Nicht überschreiben, wenn bereits ein laufender Timer existiert.
        if key not in self.timers or self.timers[key].is_done():
            self.timers[key] = SpellTimer(champion, spell, cooldown)
            print(f"[TIMER] {champion} {spell} — {cooldown}s")

    def reset(self):
        self.timers.clear()
        print("[TIMER] Alle Timer zurückgesetzt")

    def cleanup(self):
        self.timers = {k: v for k, v in self.timers.items() if not v.is_done()}

    def get_active(self):
        self.cleanup()
        # Nach verbleibender Zeit sortiert (am dringendsten zuerst).
        return sorted(self.timers.values(), key=lambda t: t.remaining())

    def chat_line(self):
        """Alle laufenden Timer als eine Chat-Zeile.

        Beispiel: 'jhin 2 40, lux 5 39'
        """
        active = self.get_active()
        return ", ".join(t.chat_format() for t in active)
