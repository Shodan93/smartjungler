import time


class SpellTimer:
    def __init__(self, champion, spell, cooldown, certain=False, stamp=None,
                 elapsed=0, up_game=None, confirmed=True):
        self.champion = champion
        self.spell = spell
        self.cooldown = cooldown
        self.certain = certain      # True = "used" (sicher), False = Ping
        self.confirmed = confirmed  # False = provisorisch (OCR prüft noch)
        self.stamp = stamp          # Game-Timestamp der ersten Sichtung
        # up_game = absolute Spielzeit (Sekunden), wann der Spell WIEDER UP
        # ist. Für den Team-Callout ("jhin 27 30"). None = unbekannt.
        self.up_game = up_game
        # elapsed = bereits vergangene Sekunden (aus dem Chat-Timestamp),
        # damit alte Flashes mit korrekter Restzeit starten.
        self.started = time.time() - elapsed

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
        """Team-Callout als SPIELZEIT, wann der Flash wieder up ist.

        z.B. 'jhin 27 30' (Flash ist bei Spielminute 27:30 zurück).
        Fällt auf Countdown zurück, wenn keine Spielzeit bekannt ist.
        """
        if self.up_game is not None:
            m, s = divmod(int(self.up_game), 60)
            return f"{self.champion.lower()} {m:02d} {s:02d}"
        m, s = self.mmss()
        return f"{self.champion.lower()} {m} {s:02d}"


class TimerManager:
    def __init__(self):
        self.timers = {}  # key: "champion_spell"

    def set_confirmed(self, champion, spell, value=True):
        t = self.timers.get(f"{champion}_{spell}")
        if t:
            t.confirmed = value

    def remove(self, champion, spell, only_unconfirmed=False):
        key = f"{champion}_{spell}"
        t = self.timers.get(key)
        if t and (not only_unconfirmed or not t.confirmed):
            del self.timers[key]
            return True
        return False

    def add(self, champion, spell, cooldown, certain=False, stamp=None,
            elapsed=0, up_game=None, confirmed=True):
        """Fügt einen Timer hinzu / aktualisiert ihn.

        Regeln:
          - Läuft schon ein Timer: gleiche/niedrigere Sicherheit -> ignorieren.
          - "used" (certain) überschreibt eine reine Ping-Schätzung.
          - elapsed = bereits vergangene Sekunden (aus dem Timestamp).
          - up_game = absolute Spielzeit, wann der Spell wieder up ist.

        Returns:
            True, wenn ein Timer neu gesetzt/überschrieben wurde.
        """
        key = f"{champion}_{spell}"
        cur = self.timers.get(key)
        if cur and not cur.is_done():
            if certain and not cur.certain:
                self.timers[key] = SpellTimer(champion, spell, cooldown, True,
                                              stamp, elapsed, up_game, confirmed)
                print(f"[TIMER] {champion} {spell} BESTÄTIGT (used)")
                return True
            return False  # bereits getrackt

        self.timers[key] = SpellTimer(champion, spell, cooldown, certain,
                                      stamp, elapsed, up_game, confirmed)
        tag = "used" if certain else "ping"
        print(f"[TIMER] {champion} {spell} ({tag}, -{int(elapsed)}s)")
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
