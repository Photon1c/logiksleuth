from __future__ import annotations

import csv
from typing import Dict, Iterator, List


def stream_cases(csv_path: str, batch_size: int = 1000) -> Iterator[List[Dict[str, str]]]:
    batch: List[Dict[str, str]] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch


