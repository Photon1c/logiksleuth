from __future__ import annotations

import json
from pathlib import Path


class Telemetry:
    def __init__(self, filename: str = "telemetry.jsonl"):
        self.path = Path(__file__).resolve().parent / filename

    def log(self, record: dict) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

