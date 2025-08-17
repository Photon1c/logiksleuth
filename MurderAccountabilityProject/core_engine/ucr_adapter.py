"""
UCR Adapter
Convert aggregate UCR rows into per-incident JSONL for the pipeline.

Input CSV columns: ORI,Name,YEAR,MRD,CLR,Source,State,County,Agency

Usage (PowerShell):
  python -m ucr_adapter
Writes to data/ucr_incidents.jsonl by default.
"""

import csv, json, math
from pathlib import Path

IN = Path("data/ucr_sample.csv")         # change if needed
OUT = Path("data/ucr_incidents.jsonl")
OUT.parent.mkdir(exist_ok=True, parents=True)

def normalize_county(s: str) -> str:
    # Examples come like: "Anchorage, AK" — keep county/city text before the comma.
    if not s:
        return ""
    return s.split(",")[0].strip()

def emit(record, fh):
    fh.write(json.dumps(record) + "\n")

def safe_int(val):
    """
    Convert messy numeric strings to int.
    Handles floats like '152.00000000000009' or blanks gracefully.
    """
    if val is None or str(val).strip() == "":
        return 0
    try:
        return int(val)
    except ValueError:
        try:
            return int(round(float(val)))
        except ValueError:
            return 0


def main():
    with IN.open("r", encoding="utf-8") as f, OUT.open("w", encoding="utf-8") as out:
        r = csv.DictReader(f)
        for row in r:
            year = int(row["YEAR"])
            mrd = safe_int(row.get("MRD"))
            clr = safe_int(row.get("CLR"))

            open_cnt = max(0, mrd - clr)
            county = normalize_county(row.get("County", ""))

            base = {
                # Provenance
                "source": row.get("Source", "UCR"),
                "ori": row.get("ORI"),
                "agency": row.get("Agency") or row.get("Name"),
                # Minimal fields our pipeline understands
                "date": f"{year}-07-01",          # mid-year anchor (banded later)
                "county": county,
                "state": row.get("State"),
                "mo_tags": [],                    # aggregate rows don’t include MO
                "geo_precision": "county"         # coarse by design
            }

            # just before the emit loops in main()
            if open_cnt or clr:
                # quick pulse log; comment out later
                if open_cnt and clr:
                    pass  # both present
                # print(f"YEAR={year} COUNTY={county} MRD={mrd} CLR={clr} OPEN={open_cnt}")



            # Emit CLOSED incidents (CLR)
            for _ in range(clr):
                rec = dict(base)
                rec["case_status"] = "closed"
                rec["conviction_status"] = "cleared"  # UCR “cleared” ≠ conviction, but closed for our purposes
                emit(rec, out)

            # Emit ACTIVE incidents (MRD-CLR)
            for _ in range(open_cnt):
                rec = dict(base)
                rec["case_status"] = "active"
                emit(rec, out)

    print(f"Wrote JSONL incidents → {OUT}")

if __name__ == "__main__":
    main()
