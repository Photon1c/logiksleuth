from __future__ import annotations

import json
import random
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .logic.board import Board
from .persist.manhunt import load_cases_stream


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class Triplet:
    suspect: str
    item: str
    location: str


@dataclass
class Knowledge:
    remaining_suspects: List[str]
    remaining_items: List[str]
    remaining_locations: List[str]
    questions_left: int
    posterior: Dict[Tuple[str, str, str], float]


@dataclass
class TurnState:
    current: str  # "player" or "ai"
    locks: Dict[str, int] = field(default_factory=lambda: {"player": 0, "ai": 0})
    turn_count: int = 0
    last_ai_action: str = ""


@dataclass
class GameState:
    rng: random.Random
    settings: dict
    dev: bool
    candidates: List[dict]
    items: List[str]
    locations: List[str]
    true_triplet: Triplet
    player_board: Board
    ai_board: Board
    player_knowledge: Knowledge
    ai_knowledge: Knowledge
    logs: List[dict] = field(default_factory=list)
    turn: TurnState = field(default_factory=lambda: TurnState(current="player"))
    winner: str = ""  # changed: track winner

    @staticmethod
    def from_settings(settings: dict, dev: bool = False) -> "GameState":
        seed = settings.get("dev_seed") if dev else None
        rng = random.Random(seed)
        # Data loading: default JSONs or Manhunt CSV
        data_dir = Path(__file__).resolve().parent / "data"
        manhunt_cfg = settings.get("manhunt", {})
        if manhunt_cfg.get("enabled"):
            # Minimal mapping: derive sets from CSV columns (stream first N rows)
            csv_path = Path(__file__).resolve().parent.parent / manhunt_cfg.get("data_file", "")
            # Stream a sample to avoid loading huge files
            sample = list(load_cases_stream(str(csv_path), limit=5000))
            if not sample:
                raise ValueError(f"Manhunt CSV had no rows: {csv_path}")
            # suspects from unique OffRace/OffSex bins
            suspects_set = set()
            items_set = set()
            locations_set = set()
            for row in sample:
                suspects_set.add(f"{row.get('OffRace','?')}-{row.get('OffSex','?')}")
                items_set.add(row.get("Weapon", "Unknown"))
                # prefer MSA, fallback State
                loc = row.get("MSA") or row.get("State") or "Unknown"
                locations_set.add(loc)
            suspect_names = sorted(suspects_set)
            item_names = sorted(items_set)
            location_names = sorted(locations_set)
            candidates = [{"name": s} for s in suspect_names]
            # pick a solved case as truth if available else random from sample
            solved = [r for r in sample if (str(r.get("Solved","No")).lower() in ("yes","true","1"))]
            pick = rng.choice(solved or sample)
            true_triplet = Triplet(
                suspect=f"{pick.get('OffRace','?')}-{pick.get('OffSex','?')}",
                item=pick.get("Weapon", "Unknown"),
                location=(pick.get("MSA") or pick.get("State") or "Unknown"),
            )
        else:
            candidates = _load_json(data_dir / "candidates.json")
            items = _load_json(data_dir / "items.json")
            locations = _load_json(data_dir / "locations.json")

            suspect_names = [c["name"] for c in candidates]
            item_names = items["items"]
            location_names = locations["locations"]

            true_triplet = Triplet(
                suspect=rng.choice(suspect_names),
                item=rng.choice(item_names),
                location=rng.choice(location_names),
            )

        # Grid sizing: if manhunt, scale board to sqrt of unique locations (cap [6, 20])
        if manhunt_cfg.get("enabled"):
            approx_cells = max(1, len(location_names))
            side = int(max(6, min(20, round(approx_cells ** 0.5))))
            size = side
        else:
            size = settings["board"]["size"]
        evidence_nodes = settings["board"]["evidence_nodes"]
        player_board = Board(size=size, rng=rng, evidence_nodes=evidence_nodes)
        ai_board = Board(size=size, rng=rng, evidence_nodes=evidence_nodes)

        def init_knowledge() -> Knowledge:
            hyp = {}
            total = 0
            for s in suspect_names:
                for i in item_names:
                    for l in location_names:
                        hyp[(s, i, l)] = 1.0
                        total += 1
            for k in list(hyp.keys()):
                hyp[k] /= total
            return Knowledge(
                remaining_suspects=list(suspect_names),
                remaining_items=list(item_names),
                remaining_locations=list(location_names),
                questions_left=settings["limits"]["questions_per_round"],
                posterior=hyp,
            )

        return GameState(
            rng=rng,
            settings=settings,
            dev=dev,
            candidates=candidates,
            items=item_names,
            locations=location_names,
            true_triplet=true_triplet,
            player_board=player_board,
            ai_board=ai_board,
            player_knowledge=init_knowledge(),
            ai_knowledge=init_knowledge(),
        )

    def to_json(self) -> dict:
        data = asdict(self)
        data["true_triplet"] = asdict(self.true_triplet)
        # Remove RNG non-serializable
        data.pop("rng", None)
        # Custom boards
        data["player_board"] = {
            "size": self.player_board.size,
            "evidence_nodes": self.player_board.evidence_nodes,
            "probes": {f"{x},{y}": v for (x, y), v in self.player_board.probes.items()},
            "evidence": [list(t) for t in self.player_board._evidence_cells],
        }
        data["ai_board"] = {
            "size": self.ai_board.size,
            "evidence_nodes": self.ai_board.evidence_nodes,
            "probes": {f"{x},{y}": v for (x, y), v in self.ai_board.probes.items()},
            "evidence": [list(t) for t in self.ai_board._evidence_cells],
        }
        return data

