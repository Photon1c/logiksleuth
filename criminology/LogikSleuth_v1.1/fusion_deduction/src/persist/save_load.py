from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..game_state import GameState


def save_slot1(gs: GameState, path: Optional[Path] = None) -> Path:
    if path is None:
        path = Path(__file__).resolve().parent / "save_slot1.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(gs.to_json(), f, indent=2)
    return path


def load_slot1(path: Optional[Path] = None) -> dict:
    if path is None:
        path = Path(__file__).resolve().parent / "save_slot1.json"
    if not path.exists():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

