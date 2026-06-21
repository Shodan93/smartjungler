import time

try:
    import pygame
    _HAS_PYGAME = True
except Exception:
    _HAS_PYGAME = False


class AlertSystem:
    def __init__(self, sound_path="sounds/alert.wav"):
        self.sound = None
        self.last = 0
        if not _HAS_PYGAME:
            print("[ALERT] pygame nicht verfügbar — Audio deaktiviert")
            return
        try:
            pygame.mixer.init()
            self.sound = pygame.mixer.Sound(sound_path)
        except Exception as e:
            print(f"[ALERT] Sound konnte nicht geladen werden ({e}) — Audio deaktiviert")
            self.sound = None

    def trigger(self):
        if self.sound and time.time() - self.last > 2:
            self.sound.play()
            self.last = time.time()
