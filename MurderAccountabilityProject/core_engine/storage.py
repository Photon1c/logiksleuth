RESEARCH_LAKE = []
RESTRICTED_VAULT = []
QUARANTINE = []

def to_research(rec):
    assert rec.get("access") in {"research","restricted","quarantine"}
    RESEARCH_LAKE.append(rec)
def to_restricted(rec):
    assert rec.get("access") in {"research","restricted","quarantine"}
    RESTRICTED_VAULT.append(rec)
def to_quarantine(rec):
    assert rec.get("access") in {"research","restricted","quarantine"}
    QUARANTINE.append(rec)
