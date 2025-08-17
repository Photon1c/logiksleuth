# eagle_scanner.py
# Scan ACTIVE records in a JSONL to find top states/counties for watchlists.

import json, argparse
from collections import Counter
from pathlib import Path

def year_of(d): 
    try: return int((d or "1900")[:4])
    except: return 1900

def scan(path: Path, recent_year: int):
    c_state, c_county = Counter(), Counter()
    total = act = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            r = json.loads(line)
            total += 1
            if (r.get("case_status") or "").lower() != "active": continue
            if year_of(r.get("date")) < recent_year: continue
            act += 1
            st = (r.get("state") or "").strip()
            co = (r.get("county") or "").strip()
            if st: c_state[st] += 1
            if co: c_county[co] += 1
    return total, act, c_state, c_county

def main():
    ap = argparse.ArgumentParser(description="Eagle Scanner: find ACTIVE hotspots.")
    ap.add_argument("jsonl", type=Path)
    ap.add_argument("--recent-year", type=int, default=2010)
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()

    total, act, c_state, c_county = scan(args.jsonl, args.recent_year)

    print(f"\nScanned: {total:,} records | ACTIVE since {args.recent_year}: {act:,}\n")

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
    print(f"set CLASSIFIER_RECENT_YEAR={args.recent_year}")

if __name__ == "__main__":
    main()
