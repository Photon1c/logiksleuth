# mock_data_generator.py
# Generates data/mock_records.jsonl for quick pipeline checks.

from pathlib import Path
import json, random

DATA_PATH = Path("data")
OUT = DATA_PATH / "mock_records.jsonl"
DATA_PATH.mkdir(exist_ok=True)

def rand_phone():
    return f"{random.choice([206,503,312])}-{random.randint(200,999)}-{random.randint(1000,9999)}"

def rand_email():
    users = ["alpha","bravo","charlie","delta","echo"]
    doms = ["mail.com","example.org","site.net"]
    return f"{random.choice(users)}@{random.choice(doms)}"

def write_jsonl(rows, path):
    with path.open("w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r) + "\n")

records = [
    # 1) CLOSED, low-PII ⇒ should land in Research Lake w/ joins allowed
    {
        "case_status": "closed",
        "name": "John Doe",
        "conviction_status": "convicted",
        "mo_tags": ["strangulation"],
        "date": "2021-05-12",
        "county": "Clark",
        "geo_precision": "hex9"
    },
    # 2) ACTIVE, contains obvious PII ⇒ quarantine
    {
        "case_status": "active",
        "mo_tags": ["burns"],
        "date": "2025-06-20",
        "county": "Multnomah",
        "narrative": f"Contact at {rand_phone()} or {rand_email()}",
    },
    # 3) ACTIVE, typical minimalization path ⇒ research (not linkable)
    {
        "case_status": "active",
        "name": "Jane Roe",
        "exact_dob": "1990-04-01",
        "address": "123 Main St",
        "gps_exact": "47.6123,-122.3344",
        "phone": rand_phone(),
        "email": rand_email(),
        "mo_tags": ["asphyxiation"],
        "date": "2025-07-01",
        "county": "King"
    },
]

write_jsonl(records, OUT)
print(f"Wrote {len(records)} mock records → {OUT}")
