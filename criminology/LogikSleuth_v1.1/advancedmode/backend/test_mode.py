from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


REQUIRED_FIELDS = {
    "Year": ["Year"],
    "MSA": ["MSA"],
    "VicSex": ["VicSex", "VictimSex", "Victim's Sex"],
    "Weapon": ["Weapon"],
    "Solved": ["Solved", "Clearance"],
}


def _map_fields(fieldnames: List[str]) -> Tuple[Dict[str, str], List[str]]:
    mapping: Dict[str, str] = {}
    missing: List[str] = []
    fields_set = set(fieldnames or [])
    for std, alts in REQUIRED_FIELDS.items():
        found = None
        for a in alts:
            if a in fields_set:
                found = a
                break
        if found is None:
            missing.append(std)
        else:
            mapping[std] = found
    return mapping, missing


def test_procedure_mappability(csv_path: str, sample_limit: int = 10000) -> Dict[str, object]:
    path = Path(csv_path)
    if not path.exists():
        return {"ok": False, "error": f"CSV not found: {csv_path}"}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        mapping, missing = _map_fields(reader.fieldnames or [])
        if missing:
            return {"ok": False, "error": "Missing required fields", "missing": missing, "available": reader.fieldnames}
        year_f = mapping["Year"]
        msa_f = mapping["MSA"]
        sex_f = mapping["VicSex"]
        wep_f = mapping["Weapon"]
        sol_f = mapping["Solved"]

        total = 0
        nonempty = Counter()
        sex_counts = Counter()
        weapon_counts = Counter()
        msa_counts = Counter()
        solved_counts = Counter()
        examples: List[Dict[str, str]] = []
        for row in reader:
            total += 1
            if row.get(year_f):
                nonempty["Year"] += 1
            if row.get(msa_f):
                nonempty["MSA"] += 1
            if row.get(sex_f):
                nonempty["VicSex"] += 1
                sex_counts[row.get(sex_f)] += 1
            if row.get(wep_f):
                nonempty["Weapon"] += 1
                weapon_counts[row.get(wep_f)] += 1
            if row.get(sol_f) is not None:
                nonempty["Solved"] += 1
                solved_counts[str(row.get(sol_f)).lower()] += 1
            if len(examples) < 5:
                examples.append({k: row.get(v, "") for k, v in mapping.items()})
            if total >= sample_limit:
                break

        coverage = {k: (nonempty[k], total) for k in REQUIRED_FIELDS.keys()}
        # Evaluate whether typical filters from procedure are feasible
        feasible = True
        reasons: List[str] = []
        if nonempty["MSA"] == 0:
            feasible = False
            reasons.append("MSA field empty in sample")
        if nonempty["VicSex"] == 0:
            feasible = False
            reasons.append("VicSex field empty in sample")
        if nonempty["Weapon"] == 0:
            feasible = False
            reasons.append("Weapon field empty in sample")

        return {
            "ok": feasible,
            "total_sampled": total,
            "coverage": coverage,
            "sex_counts": sex_counts.most_common(10),
            "weapon_counts": weapon_counts.most_common(10),
            "msa_examples": [m for m, _ in msa_counts.most_common(5)],
            "solved_counts": solved_counts,
            "field_mapping": mapping,
            "missing": [],
            "examples": examples,
            "notes": reasons,
        }


