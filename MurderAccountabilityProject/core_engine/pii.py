import re

PATTERNS = {
    "EMAIL": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "PHONE": re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "PLATE": re.compile(r"\b[A-Z0-9]{5,8}\b"),
    "STREET_ADDR": re.compile(r"\b\d{1,5}\s+[A-Za-z0-9.\-]+\s+(?:St|Ave|Rd|Blvd|Dr)\b", re.I),
    "HANDLE": re.compile(r"@[A-Za-z0-9_]{3,30}"),
    "GPS_COORD": re.compile(r"\b-?\d{1,2}\.\d{3,},\s?-?\d{1,3}\.\d{3,}\b"),
}

def scan_pii(record: dict) -> dict:
    """Return risk score in [0,1] and matched keys."""
    hits = set()
    text_fields = []
    for k, v in record.items():
        if v is None: 
            continue
        s = str(v)
        text_fields.append(s)
        for name, rx in PATTERNS.items():
            if rx.search(s):
                hits.add(name)
    # crude score: 1 - exp(-hits/4)
    import math
    score = 1 - math.exp(-len(hits)/4 or 0)
    return {"risk": score, "matches": sorted(hits)}
