from __future__ import annotations

from typing import Callable, List, Tuple

from .game_state import GameState, Triplet
from . import rules


def _posterior_top_hypothesis(gs: GameState) -> Tuple[Tuple[str, str, str], float]:
    items = list(gs.ai_knowledge.posterior.items())
    items.sort(key=lambda kv: kv[1], reverse=True)
    return items[0]


def select_question(gs: GameState, predicates: List[Callable[[Triplet], bool]]) -> Callable[[Triplet], bool]:
    # choose predicate that splits remaining posterior closest to 50/50
    best_pred = predicates[0]
    best_score = 1.0
    post = gs.ai_knowledge.posterior
    for p in predicates:
        yes = sum(prob for hyp, prob in post.items() if p(Triplet(*hyp)))
        split = abs(0.5 - yes)
        if split < best_score:
            best_score = split
            best_pred = p
    return best_pred


def select_probe(gs: GameState) -> Tuple[int, int]:
    # explore cells with no probes
    # AI probes the player's board
    board = gs.player_board
    unexplored = board.unprobed_cells()
    if not unexplored:
        return (0, 0)
    # simple random for baseline
    return gs.rng.choice(unexplored)


def maybe_accuse(gs: GameState, threshold: float) -> Tuple[bool, Tuple[str, str, str], float]:
    (s, i, l), prob = _posterior_top_hypothesis(gs)
    return (prob >= threshold, (s, i, l), prob)


def take_turn(gs: GameState, predicates: List[Callable[[Triplet], bool]]) -> str:
    # accuse if confident
    ok, hyp, prob = maybe_accuse(gs, gs.settings["ai"]["accuse_threshold"])
    if ok:
        print(f"[AI] Decide: accuse {hyp} p={prob:.2f}")
        won, _ = rules.handle_accuse(gs, *hyp)
        return "accuse-win" if won else "accuse-fail"
    # else question if available
    if gs.ai_knowledge.questions_left > 0 and predicates:
        pred = select_question(gs, predicates)
        print("[AI] Decide: ask question")
        ans, _ = rules.handle_question(gs, pred)
        return f"ask-{'Y' if ans else 'N'}"
    # else probe
    cell = select_probe(gs)
    print(f"[AI] Decide: probe {cell}")
    hit, _ = rules.handle_probe(gs, cell)
    return f"probe-{'H' if hit else 'M'}"

