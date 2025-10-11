# Hard safety rails: forbid operational detail, weapons, targeting, or PII.

from typing import Dict

BANNED_KEYWORDS = [
    "how to build", "procure weapon", "escape route details",
    "target home address", "fabricate id", "jamming police",
    "kill", "assassinate", "bomb", "poison",
]

def safety_guard(text: str) -> Dict[str, str]:
    t = text.lower()
    for k in BANNED_KEYWORDS:
        if k in t:
            return {"status":"blocked","reason":f"Contains banned pattern: {k}"}
    return {"status":"ok","reason":"pass"}
