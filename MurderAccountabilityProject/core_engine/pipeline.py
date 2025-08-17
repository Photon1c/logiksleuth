# --- AFTER (drop in) ---
from status_resolver import resolve_status
from pii import scan_pii
from transforms import minimal_active
from tagging import tag_access
from config import get_cfg
from storage import to_research, to_restricted, to_quarantine
# add import at top
from agent_classifier import should_route_for_review
from dotenv import load_dotenv

load_dotenv()


# add near top (after imports)
def _ensure_access(rec: dict, default_access: str, linkable: bool) -> dict:
    if "access" not in rec:
        rec = dict(rec)
        rec["access"] = default_access
        rec["linkable"] = linkable
    return rec


def retain_fields(rec, keep):
    return {k: rec.get(k) for k in keep if k in rec}

def ingest_record(rec: dict) -> str:
    cfg = get_cfg()
    status = resolve_status(rec)
    pii_pre = scan_pii(rec)
    high_pre = pii_pre["risk"] >= cfg["pii_scanner"]["thresholds"]["high"]

    # --- UNKNOWN branch ---
    if status == "unknown":
        rec = tag_access(rec, "unknown", pii_pre["risk"])
        to_quarantine(rec)
        return "quarantine"

    # --- ACTIVE branch ---
    if status == "active":
        # Minimalize first, then rescan
        rec2 = minimal_active(rec)
        pii_post = scan_pii(rec2)
        high_active = (
            pii_post["risk"] >= 0.30
            or any(m in ("EMAIL", "PHONE", "SSN") for m in pii_post["matches"])
        )
        rec2 = retain_fields(rec2, cfg["policy"]["active_cases"]["retain_fields"])
        rec2 = tag_access(rec2, "active", pii_post["risk"])
        rec2 = _ensure_access(rec2, "research", False)

        # Optional Galton-board classifier
        review, reason = should_route_for_review(rec2)
        if review and not high_active:
            sink = (cfg.get("classifier", {}) or {}).get("route_active_review_to", "restricted")
            rec2["review_reason"] = reason
            if sink == "quarantine":
                to_quarantine(rec2)
                return "quarantine"
            else:
                to_restricted(rec2)
                return "restricted"

        if high_active:
            to_quarantine(rec2)
            return "quarantine"

        to_research(rec2)
        return "research"

    # --- CLOSED branch ---
    keep = cfg["policy"]["closed_cases"]["retain_fields"]
    rec3 = retain_fields(rec, keep)
    rec3 = tag_access(rec3, "closed", pii_pre["risk"])
    rec3 = _ensure_access(rec3, "research", True)

    if high_pre:
        to_restricted(rec3)
        return "restricted"

    to_research(rec3)
    return "research"

