import time


class SpellTimer:
    def __init__(self, champion, spell, cooldown, certain=False, stamp=None):
        self.champion = champion
        self.spell = spell
        self.cooldown = cooldown
        self.certain = certain      # True = "used" (sicher), False = Ping
        self.stamp = stamp          # Game-Timestamp der ersten Sichtung
        self.started = time.time()

    def remaining(self):
        elapsed = time.time() - self.started
        return max(0, self.cooldown - elapsed)

    def is_done(self):
        return self.remaining() <= 0

    def mmss(self):
        r = int(round(self.remaining()))
        return r // 60, r % 60

    def display(self):
        m, s = self.mmss()
        icon = "⚡" if self.spell == "flash" else "•"
        mark = "" if self.certain else " ?"   # ? = nur Ping/Schätzung
        return f"{self.champion} {icon} {self.spell.capitalize()} — {m}:{s:02d}{mark}"

    def chat_format(self):
        """Authentisches Chat-Format, alles klein: 'jhin 2 40'."""
        m, s = self.mmss()
        return f"{self.champion.lower()} {m} {s:02d}"


class TimerManager:
    def __init__(self):
        self.timers = {}  # key: "champion_spell"

    def add(self, champion, spell, cooldown, certain=False, stamp=None):
        """Fügt einen Timer hinzu / aktualisiert ihn.

        Regeln:
          - Läuft schon ein Timer: gleiche/niedrigere Sicherheit -> ignorieren
            (die erste Sichtung/Stamp gewinnt, kein Doppel-Zählen).
          - "used" (certain) überschreibt eine reine Ping-Schätzung und
            startet den Timer als sicher neu (das bestätigte Event gilt).

        Returns:
            True, wenn ein Timer neu gesetzt/überschrieben wurde.
        """
        key = f"{champion}_{spell}"
        cur = self.timers.get(key)
        if cur and not cur.is_done():
            if certain and not cur.certain:
                self.timers[key] = SpellTimer(champion, spell, cooldown, True, stamp)
                print(f"[TIMER] {champion} {spell} BESTÄTIGT (used) — überschreibt Ping")
                return True
            return False  # bereits getrackt

        self.timers[key] = SpellTimer(champion, spell, cooldown, certain, stamp)
        tag = "used/sicher" if certain else "Ping"
        print(f"[TIMER] {champion} {spell} ({tag}) — {cooldown}s")
        return True

    def reset(self):
        self.timers.clear()
        print("[TIMER] Alle Timer zurückgesetzt")

    def cleanup(self):
        self.timers = {k: v for k, v in self.timers.items() if not v.is_done()}

    def get_active(self):
        self.cleanup()
        return sorted(self.timers.values(), key=lambda t: t.remaining())

    def chat_line(self):
        """Alle laufenden Timer als eine Chat-Zeile: 'jhin 2 40, lux 5 39'."""
        return ", ".join(t.chat_format() for t in self.get_active())
