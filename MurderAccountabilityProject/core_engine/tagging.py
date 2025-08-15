def tag_access(rec, status: str, pii_risk: float) -> dict:
    r = dict(rec)
    r["case_status"] = status
    r["pii_risk"] = round(pii_risk, 3)
    if status == "closed" and pii_risk < 0.6:
        r["access"] = "research"
        r["linkable"] = True
    elif status == "active" and pii_risk < 0.6:
        r["access"] = "research"  # minimalized already; safe cohort
        r["linkable"] = False     # joins off for actives
    else:
        r["access"] = "restricted"
        r["linkable"] = False
    return r
