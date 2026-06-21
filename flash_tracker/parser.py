import re
import difflib

from config import SPELL_COOLDOWNS, FUZZY_CUTOFF, IGNORE_PHRASES
from champions import CHAMPIONS

SPELL_NAMES = "Flash|Ignite|Heal|Ghost|Barrier|Exhaust|Teleport|Cleanse|Smite"

# Bestätigt: "Jhin used Flash!"  -> sicher (im Spiel gesehen)
USED_PATTERN = re.compile(
    r"([A-Za-z][A-Za-z0-9'\.\-]*)\s+used\s+(" + SPELL_NAMES + r")",
    re.IGNORECASE,
)
# Ping/Schätzung: "<EnemyChamp> Flash"  -> unsicher (gerufen)
CALL_PATTERN = re.compile(
    r"([A-Za-z][A-Za-z0-9'\.\-]*)\s+(" + SPELL_NAMES + r")",
    re.IGNORECASE,
)
# Game-Timestamp am Zeilenanfang, z.B. "00:06" oder "7:22"
STAMP_PATTERN = re.compile(r"\b(\d{1,2}:\d{2})\b")


def _norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


_CHAMP_BY_NORM = {_norm(c): c for c in CHAMPIONS}
_NORMS = list(_CHAMP_BY_NORM.keys())


def match_champion(word):
    """Mappt ein (evtl. fehlerhaftes) Wort auf einen echten Champion.
    None, wenn nichts hinreichend passt."""
    n = _norm(word)
    if len(n) < 2:
        return None
    if n in _CHAMP_BY_NORM:
        return _CHAMP_BY_NORM[n]
    m = difflib.get_close_matches(n, _NORMS, n=1, cutoff=FUZZY_CUTOFF)
    return _CHAMP_BY_NORM[m[0]] if m else None


def parse_chat(text):
    """Findet Spell-Events im OCR-Text.

    Returns Liste von dicts:
        {"champion","spell","cooldown","certain","stamp"}
      - certain=True  -> "X used Flash!" (sicher)
      - certain=False -> "<Champ> Flash" (Ping/Schätzung)
    """
    results = []
    for line in text.splitlines():
        low = line.lower()
        if any(p in low for p in IGNORE_PHRASES):
            continue

        sm = STAMP_PATTERN.search(line)
        stamp = sm.group(1) if sm else None

        # 1) Sichere "used"-Events zuerst.
        used_found = False
        for m in USED_PATTERN.finditer(line):
            champ = match_champion(m.group(1))
            if not champ:
                continue
            spell = m.group(2).lower()
            results.append({
                "champion": champ, "spell": spell,
                "cooldown": SPELL_COOLDOWNS.get(spell, 300),
                "certain": True, "stamp": stamp,
            })
            used_found = True
        if used_found:
            continue  # "used"-Zeile nicht zusätzlich als Ping werten

        # 2) Ping/Schätzung — nur den Teil nach "):" (Poster ignorieren).
        msg = line.split("):", 1)[1] if "):" in line else line
        for m in CALL_PATTERN.finditer(msg):
            champ = match_champion(m.group(1))
            if not champ:
                continue
            spell = m.group(2).lower()
            results.append({
                "champion": champ, "spell": spell,
                "cooldown": SPELL_COOLDOWNS.get(spell, 300),
                "certain": False, "stamp": stamp,
            })
    return results
