import re
import difflib

from config import SPELL_COOLDOWNS, FUZZY_CUTOFF, IGNORE_PHRASES
from champions import CHAMPIONS

# Wort (Champion) direkt vor einem Spell-Namen.
SPELL_NAMES = "Flash|Ignite|Heal|Ghost|Barrier|Exhaust|Teleport|Cleanse|Smite"
PATTERN = re.compile(
    r"([A-Za-z][A-Za-z0-9'\.\-]*)\s+(" + SPELL_NAMES + r")",
    re.IGNORECASE,
)

# Champion-Namen normalisiert (nur Kleinbuchstaben) -> Originalname.
def _norm(s):
    return re.sub(r"[^a-z]", "", s.lower())

_CHAMP_BY_NORM = {_norm(c): c for c in CHAMPIONS}
_NORMS = list(_CHAMP_BY_NORM.keys())


def match_champion(word):
    """Mappt ein (evtl. fehlerhaft erkanntes) Wort auf einen echten
    Champion-Namen. Gibt None zurück, wenn nichts hinreichend passt."""
    n = _norm(word)
    if len(n) < 2:
        return None
    if n in _CHAMP_BY_NORM:           # exakter Treffer
        return _CHAMP_BY_NORM[n]
    m = difflib.get_close_matches(n, _NORMS, n=1, cutoff=FUZZY_CUTOFF)
    return _CHAMP_BY_NORM[m[0]] if m else None


def parse_chat(text):
    """Findet frische Spell-Pings im OCR-Text.

    - Ignoriert Countdown-/Erinnerungszeilen ("Wait For ... Flash - 13s").
    - Nimmt nur den Teil NACH "):" (der Poster/Champion-in-Klammern wird
      ignoriert, relevant ist der Ziel-Champion in der Nachricht).
    - Mappt erkannte Namen per Fuzzy-Matching auf echte Champions und
      verwirft unleserlichen Müll.

    Returns:
        [{"champion": "Jhin", "spell": "flash", "cooldown": 300}, ...]
    """
    results = []
    for line in text.splitlines():
        low = line.lower()
        if any(p in low for p in IGNORE_PHRASES):
            continue

        # Poster-Präfix "Name (Champ): " abtrennen, falls vorhanden.
        msg = line.split("):", 1)[1] if "):" in line else line

        for m in PATTERN.finditer(msg):
            champ = match_champion(m.group(1))
            if not champ:
                continue
            spell = m.group(2).lower()
            results.append({
                "champion": champ,
                "spell":    spell,
                "cooldown": SPELL_COOLDOWNS.get(spell, 300),
            })
    return results
