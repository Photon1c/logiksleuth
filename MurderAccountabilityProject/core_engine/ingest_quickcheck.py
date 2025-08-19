r"""
Ingest Quickcheck
Quick JSONL ingest to exercise the pipeline and print sink counts and samples.

Examples (PowerShell):
  # Zero-spend preflight
  $env:LLM_MODE='off'
  python -m ingest_quickcheck .\\data\\ucr_incidents.sample.jsonl --estimate-llm --estimate-only

  # Safe ingest with progress
  $env:LLM_MODE='off'
  python -m ingest_quickcheck .\\data\\ucr_incidents.sample.jsonl --show 2 --top-restricted 5 --heartbeat 1000
"""
import argparse, json
import time
from pathlib import Path

from pipeline import ingest_record
import storage  # holds RESEARCH_LAKE, RESTRICTED_VAULT, QUARANTINE
from status_resolver import resolve_status
from transforms import minimal_active
from agent_classifier import _rule_based, MODE, LLM_ENABLED, ESTIMATE_ONLY, MODEL_NAME
from agent_classifier import MAX_TOKENS, TEMPERATURE, BUDGET

def reset_storage():
    storage.RESEARCH_LAKE.clear()
    storage.RESTRICTED_VAULT.clear()
    storage.QUARANTINE.clear()

def read_jsonl(p: Path):
    # Use utf-8-sig to gracefully handle BOM if present
    with p.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def main():
    ap = argparse.ArgumentParser(
        description="Ingest JSONL and summarize sinks.")
    ap.add_argument("jsonl", type=Path, help="Path to mock_records.jsonl")
    ap.add_argument("--recent-year", type=int, help="Alias of --from-year")
    ap.add_argument("--from-year", type=int, help="Inclusive lower bound (e.g., 2015)")
    ap.add_argument("--to-year", type=int, help="Inclusive upper bound (e.g., 2020)")
    ap.add_argument("--year-range", type=str, help="Shorthand 'YYYY-YYYY' (e.g., 2010-2015)")
    ap.add_argument("--show", type=int, default=3,
                    help="Show N examples per sink (default: 3)")
    ap.add_argument("--top-restricted", type=int, default=0,
                    help="Show top N Restricted by county/state and review_reason (0=skip)")
    ap.add_argument("--estimate-llm", action="store_true",
                    help="Preflight: estimate how many ACTIVE records would consult the LLM (rules-only, no token spend)")
    ap.add_argument("--estimate-only", action="store_true",
                    help="Run only the preflight estimate and exit (no ingest)")
    ap.add_argument("--max-records", type=int, default=0,
                    help="Max records to process (0=all)")
    ap.add_argument("--bisect", action="store_true",
                    help="Stop on first failing row; print index and traceback")
    ap.add_argument("--heartbeat", type=int, default=0,
                    help="Print a heartbeat every N records (0=off)")
    args = ap.parse_args()

    if not args.jsonl.exists():
        print(f"Config error: Not found: {args.jsonl}")
        raise SystemExit(78)

    reset_storage()

    def resolve_year_bounds(args):
        lo = hi = None
        if getattr(args, "year_range", None):
            a, b = args.year_range.split("-", 1)
            lo, hi = (int(a), int(b))
        lo = lo if lo is not None else (getattr(args, "from_year", None) or getattr(args, "recent_year", None))
        hi = hi if hi is not None else getattr(args, "to_year", None)
        return lo, hi

    year_lo, year_hi = resolve_year_bounds(args)

    # Announce LLM mode and configuration
    if LLM_ENABLED:
        print(f"LLM classifier mode=on: model={MODEL_NAME} max_tokens={MAX_TOKENS} temperature={TEMPERATURE} budget={BUDGET or 'none'}")
    elif ESTIMATE_ONLY:
        print("LLM classifier mode=estimate: rules-only, no LLM calls")
    else:
        print("LLM classifier mode=off: no token spend")

    if args.estimate_llm:
        # Preflight estimate: rules-only pass to count potential LLM calls
        est_total = 0
        est_active = 0
        est_llm_candidates = 0
        reasons_rules = {"rules->watchlist_county":0, "rules->state_override":0, "rules->mo_keyword":0, "rules->recent_year":0, "rules->other":0}
        for rec in read_jsonl(args.jsonl):
            est_total += 1
            status = resolve_status(rec)
            if status == "active":
                est_active += 1
                y = rec.get("year") or int(str(rec.get("date") or "0")[:4] or 0)
                if year_lo is not None and y < year_lo: 
                    continue
                if year_hi is not None and y > year_hi:
                    continue
                rec2 = minimal_active(rec)
                rule, why = _rule_based(rec2)
                if rule:
                    w = str(why).lower()
                    if "watchlist" in w:
                        reasons_rules["rules->watchlist_county"] += 1
                    elif "state_override" in w:
                        reasons_rules["rules->state_override"] += 1
                    elif "mo_keyword" in w:
                        reasons_rules["rules->mo_keyword"] += 1
                    elif w.startswith("recent"):
                        reasons_rules["rules->recent_year"] += 1
                    else:
                        reasons_rules["rules->other"] += 1
                else:
                    est_llm_candidates += 1
        print(f"\nPreflight estimate (no LLM calls made):")
        print(f"  total records: {est_total}")
        print(f"  active records: {est_active}")
        print(f"  would consult LLM if enabled: {est_llm_candidates}")
        print("  rule-trigger reasons:")
        for k in ["rules->watchlist_county","rules->recent_year","rules->mo_keyword","rules->state_override","rules->other"]:
            v = reasons_rules[k]
            if v:
                print(f"    {k}: {v}")
        if args.estimate_only:
            return

    total = 0
    start_time = time.time()
    for idx, rec in enumerate(read_jsonl(args.jsonl), start=1):
        try:
            total += 1
            y = rec.get("year") or int(str(rec.get("date") or "0")[:4] or 0)
            if year_lo is not None and y < year_lo:
                continue
            if year_hi is not None and y > year_hi:
                continue
            ingest_record(rec)
            if args.heartbeat and (idx % args.heartbeat == 0):
                print(f"... processed {idx} records")
            if args.max_records and total >= args.max_records:
                break
        except Exception as e:
            if args.bisect:
                import traceback
                print(f"Bisection stop at line {idx} due to: {type(e).__name__}: {e}")
                traceback.print_exc()
                raise SystemExit(2)
            else:
                raise

    rl, rv, q = storage.RESEARCH_LAKE, storage.RESTRICTED_VAULT, storage.QUARANTINE
    print(f"\nTotal ingested: {total}")
    print(f"Research Lake:   {len(rl)}")
    print(f"Restricted Vault:{len(rv)}")
    print(f"Quarantine:      {len(q)}")
    elapsed = max(0.000001, time.time() - start_time)
    print(f"Processed {total:,} in {elapsed:.1f}s (~{(total/elapsed):,.0f} rec/s)")

    def show_samples(name, items):
        print(f"\n== {name} (showing up to {args.show}) ==")
        for i, r in enumerate(items[:args.show], 1):
            # Minimal peek; avoid PII
            print(f"{i}. status={r.get('case_status')}, "
                  f"access={r.get('access')}, "
                  f"linkable={r.get('linkable')}, "
                  f"geo={r.get('geo_precision')}, "
                  f"keys={sorted(r.keys())[:8]}...")

    show_samples("Research Lake", rl)
    show_samples("Restricted Vault", rv)
    show_samples("Quarantine", q)
    
    # --- after ingest loop, before printing counts ---
    routed_rules = sum(1 for r in storage.RESTRICTED_VAULT if str(r.get("review_reason","")).startswith(("recent", "llm_error", "no-rule", "state_override", "recent>=", "watchlist")))
    routed_llm   = sum(1 for r in storage.RESTRICTED_VAULT if str(r.get("review_reason","")).startswith("llm:"))

    print(f"\nRestricted routed by rules: {routed_rules}")
    print(f"Restricted routed by LLM:   {routed_llm}")

    # Optional: top Restricted by county/state and review_reason
    if args.top_restricted and len(rv):
        from collections import Counter
        county_counts = Counter((r.get("county") or "").strip() for r in rv if r.get("county"))
        state_counts = Counter((r.get("state") or "").strip() for r in rv if r.get("state"))
        reason_counts = Counter(str(r.get("review_reason", "")).strip() for r in rv if r.get("review_reason"))

        print(f"\nTop Restricted by county (top {args.top_restricted}):")
        for k, c in county_counts.most_common(args.top_restricted):
            print(f"  {k}: {c}")

        print(f"\nTop Restricted by state (top {args.top_restricted}):")
        for k, c in state_counts.most_common(args.top_restricted):
            print(f"  {k}: {c}")

        if reason_counts:
            print(f"\nTop review_reason in Restricted (top {args.top_restricted}):")
            for k, c in reason_counts.most_common(args.top_restricted):
                print(f"  {k}: {c}")



    # after total ingest loop
    status_counts = {}
    linkable_counts = {"linkable_true": 0, "linkable_false": 0}

    for r in rl:  # rl = storage.RESEARCH_LAKE
        s = r.get("case_status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
        if r.get("linkable"): linkable_counts["linkable_true"] += 1
        else: linkable_counts["linkable_false"] += 1

    print("\nBreakdown (Research Lake):")
    for k in sorted(status_counts):
        print(f"  {k}: {status_counts[k]}")
    print(f"  linkable=True:  {linkable_counts['linkable_true']}")
    print(f"  linkable=False: {linkable_counts['linkable_false']}")
    
    
    

if __name__ == "__main__":
    main()
