r"""
Eagle Scanner
Scan ACTIVE records in a JSONL to find recent hotspots by state and county.

Usage (PowerShell):
  python -m eagle_scanner .\data\ucr_incidents.sample.jsonl --recent-year 2015 --top 15
  # or exact window:
  python -m eagle_scanner .\data\ucr_incidents.sample.jsonl --year-range 2010-2015 --top 15

Outputs top ACTIVE states/counties since the given year and prints
copy-paste environment suggestions for:
  - CLASSIFIER_FORCE_REVIEW_STATES
  - CLASSIFIER_WATCHLIST_COUNTIES
  - CLASSIFIER_RECENT_YEAR
"""

import json, argparse
from collections import Counter
from pathlib import Path

def year_of(d): 
    try: return int((d or "1900")[:4])
    except: return 1900

def resolve_year_bounds(args):
    lo = hi = None
    if getattr(args, "year_range", None):
        a, b = args.year_range.split("-", 1)
        lo, hi = (int(a), int(b))
    lo = lo if lo is not None else (getattr(args, "from_year", None) or getattr(args, "recent_year", None))
    hi = hi if hi is not None else getattr(args, "to_year", None)
    return lo, hi

def scan(path: Path, year_lo: int | None, year_hi: int | None):
    c_state, c_county = Counter(), Counter()
    total = act = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            r = json.loads(line)
            total += 1
            if (r.get("case_status") or "").lower() != "active": continue
            y = r.get("year") or year_of(r.get("date"))
            if year_lo is not None and y < year_lo: continue
            if year_hi is not None and y > year_hi: continue
            act += 1
            st = (r.get("state") or "").strip()
            co = (r.get("county") or "").strip()
            if st: c_state[st] += 1
            if co: c_county[co] += 1
    return total, act, c_state, c_county

def main():
    ap = argparse.ArgumentParser(description="Eagle Scanner: find ACTIVE hotspots.")
    ap.add_argument("jsonl", type=Path)
    ap.add_argument("--recent-year", type=int, help="Alias of --from-year")
    ap.add_argument("--from-year", type=int, help="Inclusive lower bound (e.g., 2015)")
    ap.add_argument("--to-year", type=int, help="Inclusive upper bound (e.g., 2020)")
    ap.add_argument("--year-range", type=str, help="Shorthand 'YYYY-YYYY' (e.g., 2010-2015)")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    lo, hi = resolve_year_bounds(args)
    total, act, c_state, c_county = scan(args.jsonl, lo, hi)

    if lo is not None and hi is not None:
        window = f"{lo}-{hi}"
    elif lo is not None:
        window = f"since {lo}"
    elif hi is not None:
        window = f"through {hi}"
    else:
        window = "(all years)"
    print(f"\nScanned: {total:,} records | ACTIVE {window}: {act:,}\n")

    ts = c_state.most_common(args.top)
    tc = c_county.most_common(args.top)

    print("Top states (ACTIVE):")
    for s, n in ts: print(f"  {s:<3} {n:>8,}")
    print("\nTop counties (ACTIVE):")
    for c, n in tc: print(f"  {c:<24} {n:>8,}")

    # Quick env var suggestions (copy/paste)
    if ts:
        states_csv = ",".join([s for s,_ in ts])
        print(f"\nset CLASSIFIER_FORCE_REVIEW_STATES={states_csv}")
    if tc:
        counties_csv = ",".join([c for c,_ in tc[:8]])  # keep short
        print(f"set CLASSIFIER_WATCHLIST_COUNTIES={counties_csv}")
    if lo is not None:
        print(f"set CLASSIFIER_RECENT_YEAR={lo}")

if __name__ == "__main__":
    main()
