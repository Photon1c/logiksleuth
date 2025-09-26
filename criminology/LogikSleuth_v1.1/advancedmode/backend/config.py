from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class AppConfig:
    csv_path: str = "fusion_deduction/data/SHR65_23.csv"
    similarity_threshold: float = 0.7
    year_window: int = 5
    geo_window: Optional[int] = None
    sample_limit: int = 48  # heatmap size (<= 64 recommended)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def update_from(self, data: Dict[str, Any]) -> None:
        for k, v in data.items():
            if not hasattr(self, k):
                continue
            setattr(self, k, v)


CONFIG = AppConfig()


