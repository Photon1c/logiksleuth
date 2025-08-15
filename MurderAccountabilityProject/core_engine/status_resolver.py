def resolve_status(rec) -> str:
    """
    Return 'closed' | 'active' | 'unknown'.
    Stub: prefer explicit field; else heuristics.
    """
    s = (rec.get("case_status") or "").lower()
    if s in ("closed", "convicted"):
        return "closed"
    if s in ("active", "pending", "open"):
        return "active"
    return "unknown"
