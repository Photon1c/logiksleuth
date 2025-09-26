from __future__ import annotations

from typing import Any, Dict


def has_glasses(suspect: Dict[str, Any]) -> bool:
    return bool(suspect.get("traits", {}).get("glasses", False))


def hair_color_is(suspect: Dict[str, Any], color: str) -> bool:
    return suspect.get("traits", {}).get("hair_color") == color


def profession_in(suspect: Dict[str, Any], allowed: set) -> bool:
    return suspect.get("traits", {}).get("profession") in allowed

