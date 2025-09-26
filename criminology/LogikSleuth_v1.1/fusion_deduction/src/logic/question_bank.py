from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List

from .traits import has_glasses, hair_color_is, profession_in
from ..game_state import GameState, Triplet


_FN_MAP = {
    "has_glasses": has_glasses,
    "hair_color_is": hair_color_is,
    "profession_in": lambda s, arr: profession_in(s, set(arr)),
}


def _suspect_lookup(gs: GameState) -> Dict[str, dict]:
    return {c["name"]: c for c in gs.candidates}


def build_predicates(gs: GameState) -> List[Callable[[Triplet], bool]]:
    # If Manhunt mode is on, build simple CSV-derived predicates; else use questions.json
    if bool(gs.settings.get("manhunt", {}).get("enabled", False)):
        preds: List[Callable[[Triplet], bool]] = []
        # Predicates on suspect encoding "Race-Sex"
        def suspect_race_is(race: str) -> Callable[[Triplet], bool]:
            return lambda t: t.suspect.split("-")[0] == race
        def suspect_sex_is(sex: str) -> Callable[[Triplet], bool]:
            return lambda t: t.suspect.split("-")[1] == sex
        # Predicates on weapon category and location bucket
        def weapon_is(w: str) -> Callable[[Triplet], bool]:
            return lambda t: t.item == w
        def location_is(loc: str) -> Callable[[Triplet], bool]:
            return lambda t: t.location == loc

        # Build a small, generic set from current supports
        suspects = set(s.split("-")[0] for s in gs.player_knowledge.remaining_suspects)
        sexes = set(s.split("-")[1] for s in gs.player_knowledge.remaining_suspects if "-" in s)
        weapons = set(gs.player_knowledge.remaining_items)
        locations = set(gs.player_knowledge.remaining_locations)

        for race in list(suspects)[:3]:
            preds.append(suspect_race_is(race))
        for sex in list(sexes)[:2]:
            preds.append(suspect_sex_is(sex))
        for w in list(weapons)[:3]:
            preds.append(weapon_is(w))
        for loc in list(locations)[:3]:
            preds.append(location_is(loc))
        return preds
    else:
        data_dir = Path(__file__).resolve().parent.parent / "data"
        with (data_dir / "questions.json").open("r", encoding="utf-8") as f:
            questions = json.load(f)
        suspects = _suspect_lookup(gs)
        preds: List[Callable[[Triplet], bool]] = []

        for q in questions:
            typ = q.get("type")
            fn_spec = q.get("predicate", {})
            fn_name = fn_spec.get("fn")
            args = fn_spec.get("args", [])
            base_fn = _FN_MAP.get(fn_name)
            if not base_fn:
                continue
            if typ == "suspect":
                def make_pred(f=base_fn, a=args):
                    return lambda t: f(suspects[t.suspect], *a)
                preds.append(make_pred())
            # Future: items/locations
        return preds

