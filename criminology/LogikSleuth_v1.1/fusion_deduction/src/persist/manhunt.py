from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict, Iterator, Optional


def load_cases(csv_path: str) -> List[Dict[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def load_cases_stream(csv_path: str, limit: Optional[int] = None) -> Iterator[Dict[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            yield row
            if limit is not None and idx + 1 >= limit:
                break



