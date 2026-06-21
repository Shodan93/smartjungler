import re
from config import SPELL_COOLDOWNS

# Matched z.B. "Jhin Flash", "Wait For Diana Flash - 13s"
# Gruppe 1 = Champion (Wort direkt vor dem Spell), Gruppe 2 = Spell.
PATTERN = re.compile(
    r"([A-Za-z0-9'\.]+)\s+"
    r"(Flash|Ignite|Heal|Ghost|Barrier|Exhaust|Teleport|Cleanse|Smite)",
    re.IGNORECASE,
)


def parse_chat(text):
    """Sucht in OCR-Text nach Spell-Pings.

    Returns:
        Liste von dicts, z.B.
        [{"champion": "Jhin", "spell": "flash", "cooldown": 300}]
    """
    results = []
    for line in text.splitlines():
        for match in PATTERN.finditer(line):
            champ = match.group(1).strip()
            spell = match.group(2).lower().strip()
            cd = SPELL_COOLDOWNS.get(spell, 300)
            results.append({
                "champion": champ,
                "spell":    spell,
                "cooldown": cd,
            })
    return results
