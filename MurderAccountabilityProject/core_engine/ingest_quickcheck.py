# ingest_quickcheck.py
# Quick JSONL ingest → prints sink counts & a few samples.

import argparse, json
from pathlib import Path

from pipeline import ingest_record
import storage  # holds RESEARCH_LAKE, RESTRICTED_VAULT, QUARANTINE

def reset_storage():
    storage.RESEARCH_LAKE.clear()
    storage.RESTRICTED_VAULT.clear()
    storage.QUARANTINE.clear()

def read_jsonl(p: Path):
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def main():
    ap = argparse.ArgumentParser(
        description="Ingest JSONL and summarize sinks.")
    ap.add_argument("jsonl", type=Path, help="Path to mock_records.jsonl")
    ap.add_argument("--show", type=int, default=3,
                    help="Show N examples per sink (default: 3)")
    args = ap.parse_args()

    if not args.jsonl.exists():
        raise SystemExit(f"Not found: {args.jsonl}")

    reset_storage()

    total = 0
    for rec in read_jsonl(args.jsonl):
        total += 1
        ingest_record(rec)

    rl, rv, q = storage.RESEARCH_LAKE, storage.RESTRICTED_VAULT, storage.QUARANTINE
    print(f"\nTotal ingested: {total}")
    print(f"Research Lake:   {len(rl)}")
    print(f"Restricted Vault:{len(rv)}")
    print(f"Quarantine:      {len(q)}")

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

if __name__ == "__main__":
    main()
