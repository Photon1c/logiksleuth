# agent_classifier.py
"""
Rule-first classifier with optional LLM check to decide if an ACTIVE record
should be sent for human review (e.g., to Restricted Vault).
- No PII required; uses coarse fields (county/state/date/mo_tags).
- LLM is OFF by default; enable via env VARS (see below).
"""

from datetime import date
import json
import os
from dotenv import load_dotenv
from config import get_cfg
# --- add near top (after imports) ---
import logging
from functools import lru_cache
from typing import Set, Tuple
from openai import OpenAI

load_dotenv()

# Budget knobs (env-var overrideable)
MAX_TOKENS = int(os.getenv("LLM_CLASSIFIER_MAX_TOKENS", "64"))
TEMPERATURE = float(os.getenv("LLM_CLASSIFIER_TEMPERATURE", "0"))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Unified LLM mode: off|estimate|on
MODE = os.getenv("LLM_MODE", os.getenv("ENABLE_LLM_CLASSIFIER", "0") == "1" and "on" or "off").lower()
LLM_ENABLED = MODE == "on"
ESTIMATE_ONLY = MODE == "estimate"
_CFG = get_cfg()
_MODEL_DEFAULT = (((_CFG or {}).get("classifier") or {}).get("model")) or "gpt-5"
MODEL_NAME = os.getenv("LLM_CLASSIFIER_MODEL", _MODEL_DEFAULT)

# Token budget (multi-process safe via append-only file)
BUDGET = int(os.getenv("LLM_MAX_TOKENS", "0"))
BUDGET_FILE = os.getenv("LLM_BUDGET_FILE", ".llm_budget.log")

def _accumulate(n: int) -> int:
    with open(BUDGET_FILE, "a", encoding="utf-8") as f:
        f.write(f"{n}\n")
    total = 0
    with open(BUDGET_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.isdigit():
                total += int(line)
    return total

def _env_list(name: str) -> Set[str]:
    raw = os.getenv(name, "")
    return {x.strip().lower() for x in raw.split(",") if x.strip()}

# --- simple, transparent rules ---
WATCHLIST_COUNTIES = _env_list("CLASSIFIER_WATCHLIST_COUNTIES")
RECENT_YEAR = int(os.getenv("CLASSIFIER_RECENT_YEAR", "2010"))
FORCE_REVIEW_STATES = _env_list("CLASSIFIER_FORCE_REVIEW_STATES")
MO_KEYWORDS = _env_list("CLASSIFIER_MO_KEYWORDS")

# Announce LLM usage mode at import time
if LLM_ENABLED:
    logging.info(
        "LLM classifier mode=on model=%s max_tokens=%s temperature=%s budget=%s file=%s",
        MODEL_NAME,
        MAX_TOKENS,
        TEMPERATURE,
        BUDGET or "none",
        BUDGET_FILE,
    )
elif ESTIMATE_ONLY:
    logging.info("LLM classifier mode=estimate (no LLM calls; rules-only)")
else:
    logging.info("LLM classifier mode=off (no token spend)")

def _year_of(rec) -> int:
    # rec["date"] like 'YYYY-MM-DD'
    d = (rec.get("date") or "1900-01-01")
    try:
        return int(d[:4])
    except Exception:
        return 1900

def _rule_based(rec: dict) -> Tuple[bool, str]:
    if (rec.get("case_status") or "").lower() != "active":
        return (False, "non-active")

    # 1) recent cases → higher sensitivity
    yr = _year_of(rec)
    if yr >= RECENT_YEAR:
        # 2) watchlist counties
        county = (rec.get("county") or "").strip().lower()
        if county and county in {c.lower() for c in WATCHLIST_COUNTIES}:
            return (True, f"recent>= {RECENT_YEAR} & watchlist_county={county}")


        # 3) state-level override
        st = (rec.get("state") or "").strip()
        if st and st in FORCE_REVIEW_STATES:
            return (True, f"recent>= {RECENT_YEAR} & state_override={st}")

        # 4) MO keywords (if present in actives pipeline)
        mos = [str(m).lower() for m in rec.get("mo_tags") or []]
        if MO_KEYWORDS and any(m in MO_KEYWORDS for m in mos):
            return (True, "recent & mo_keyword")

    return (False, "no-rule-trigger")

# --- replace _llm_check with this adapter ---
@lru_cache(maxsize=4096)
def _llm_check_cached(serialized: str) -> Tuple[bool, str]:
    """
    Memoized LLM call: serialized is compact JSON string of the small record slice.
    Returns (review?, 'llm:<reason>') or (False, 'llm_error:<...>').
    """
    # Guard for disabled/estimate modes or disabled model names
    if not LLM_ENABLED or ESTIMATE_ONLY or MODEL_NAME.lower() in ("off", "disabled", "none"):
        return (False, "estimate-only" if ESTIMATE_ONLY else "llm_off")
    try:
        # 1) Prefer your local llm.py
        try:
            import llm  # your file
            messages = [
                {"role":"system","content":"Return strict JSON: {\"review\":bool,\"reason\":string}"},
                {"role":"user","content":serialized}
            ]
            txt = llm.chat(messages, model=MODEL_NAME, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
        except Exception:
            # 2) Fallback to OpenAI SDK
            client = OpenAI(timeout=15)
            rsp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role":"system","content":"Return strict JSON: {\"review\":bool,\"reason\":string}"},
                    {"role":"user","content":serialized}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            txt = rsp.choices[0].message.content
            # Audit usage and enforce optional budget
            try:
                u = getattr(rsp, "usage", None)
                logging.info(
                    "LLM used model=%s total=%s prompt=%s completion=%s",
                    getattr(rsp, "model", "?"),
                    getattr(u, "total_tokens", "?"),
                    getattr(u, "prompt_tokens", "?"),
                    getattr(u, "completion_tokens", "?")
                )
                if BUDGET and u and getattr(u, "total_tokens", None):
                    total = _accumulate(u.total_tokens)
                    if total > BUDGET:
                        raise RuntimeError(f"LLM budget exceeded: {total}>{BUDGET}")
            except Exception:
                pass

        data = json.loads(txt.strip())
        return (bool(data.get("review", False)), f"llm:{data.get('reason','')[:60]}")
    except Exception as e:
        return (False, f"llm_error:{type(e).__name__}")

def _llm_check(rec: dict) -> Tuple[bool, str]:
    # Keep the payload tiny: only fields that affect triage
    payload = {
        "case_status": rec.get("case_status"),
        "date": rec.get("date"),
        "county": rec.get("county"),
        "state": rec.get("state"),
        "mo_tags": rec.get("mo_tags") or [],
        "ori": rec.get("ori"),
        "agency": rec.get("agency"),
    }
    # single-line JSON to minimize tokens
    return _llm_check_cached(json.dumps(payload, separators=(",",":")))

def should_route_for_review(rec: dict) -> Tuple[bool, str]:
    """
    Returns (should_review, reason).
    Pipeline calls this AFTER minimalization of ACTIVE records.
    """
    if (rec.get("case_status") or "").lower() == "active" and os.getenv("CLASSIFIER_DEBUG_ACTIVE") == "1":
        print("DEBUG:", rec.get("state"), rec.get("county"))
    rule, why = _rule_based(rec)
    if rule:
        return (True, why)
    if ESTIMATE_ONLY or not LLM_ENABLED:
        return (False, "estimate-only" if ESTIMATE_ONLY else "passed-rules")
    return _llm_check(rec)

def _print_effective_config() -> None:
    print("Effective classifier config:")
    print(f"  MODE: {MODE}")
    print(f"  MODEL_NAME: {MODEL_NAME}")
    print(f"  MAX_TOKENS: {MAX_TOKENS}")
    print(f"  TEMPERATURE: {TEMPERATURE}")
    print(f"  BUDGET: {BUDGET}  FILE: {BUDGET_FILE}")
    print(f"  RECENT_YEAR: {RECENT_YEAR}")
    print(f"  WATCHLIST_COUNTIES: {len(WATCHLIST_COUNTIES)} entries")
    print(f"  FORCE_REVIEW_STATES: {len(FORCE_REVIEW_STATES)} entries")
    print(f"  MO_KEYWORDS: {len(MO_KEYWORDS)} entries")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Agent classifier utilities")
    ap.add_argument("--print-config", action="store_true", help="Print effective configuration and exit")
    args = ap.parse_args()
    if args.print_config:
        _print_effective_config()
