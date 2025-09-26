from __future__ import annotations

from typing import Callable, Tuple

from .game_state import GameState, Triplet
from .logic.elimination import filter_list_by_predicate
from .logic.deduction import update_posterior_yes_no


def handle_question(gs: GameState, predicate: Callable[[Triplet], bool]) -> Tuple[bool, str]:
    if gs.turn.locks[gs.turn.current] > 0:
        print(f"[Turn] {gs.turn.current} is locked; question blocked")
        return False, "Locked"
    knowledge = gs.player_knowledge if gs.turn.current == "player" else gs.ai_knowledge
    if knowledge.questions_left <= 0:
        print(f"[Question] {gs.turn.current} has no questions left")
        return False, "No questions left"
    knowledge.questions_left -= 1
    answer = bool(predicate(gs.true_triplet))
    # Elimination across each component using trait-aware predicate wrapper
    knowledge.remaining_suspects = filter_list_by_predicate(
        knowledge.remaining_suspects,
        lambda s: predicate(Triplet(s, gs.true_triplet.item, gs.true_triplet.location)) == answer,
        True,
    )
    knowledge.remaining_items = filter_list_by_predicate(
        knowledge.remaining_items,
        lambda i: predicate(Triplet(gs.true_triplet.suspect, i, gs.true_triplet.location)) == answer,
        True,
    )
    knowledge.remaining_locations = filter_list_by_predicate(
        knowledge.remaining_locations,
        lambda l: predicate(Triplet(gs.true_triplet.suspect, gs.true_triplet.item, l)) == answer,
        True,
    )
    knowledge.posterior = update_posterior_yes_no(knowledge.posterior, predicate, answer)
    msg = "Yes" if answer else "No"
    print(f"[Question] {gs.turn.current} -> {msg}; remaining={knowledge.questions_left}")
    # Log
    gs.logs.append({
        "type": "question",
        "actor": gs.turn.current,
        "turn": gs.turn.turn_count,
        "answer": bool(answer),
        "remaining": int(knowledge.questions_left),
    })
    return answer, msg


def handle_probe(gs: GameState, cell: Tuple[int, int]) -> Tuple[bool, str]:
    if gs.turn.locks[gs.turn.current] > 0:
        print(f"[Turn] {gs.turn.current} is locked; probe blocked")
        return False, "Locked"
    # Probe the opponent's board
    board = gs.ai_board if gs.turn.current == "player" else gs.player_board
    hit = board.probe(cell)
    msg = "Hit" if hit else "Miss"
    target = "AI" if gs.turn.current == "player" else "Player"
    print(f"[Probe] {gs.turn.current} -> {cell} on {target} = {msg}")
    # Log
    gs.logs.append({
        "type": "probe",
        "actor": gs.turn.current,
        "turn": gs.turn.turn_count,
        "cell": [int(cell[0]), int(cell[1])],
        "hit": bool(hit),
        "target": target.lower(),
    })
    return hit, msg


def handle_accuse(gs: GameState, suspect: str, item: str, location: str) -> Tuple[bool, str]:
    if gs.turn.locks[gs.turn.current] > 0:
        print(f"[Turn] {gs.turn.current} is locked; accuse blocked")
        return False, "Locked"
    win = (suspect == gs.true_triplet.suspect and item == gs.true_triplet.item and location == gs.true_triplet.location)
    if win:
        gs.winner = gs.turn.current  # changed: set winner
        print(f"[Accuse] {gs.turn.current} -> ({suspect}, {item}, {location}) = WIN")
        gs.logs.append({
            "type": "accuse",
            "actor": gs.turn.current,
            "turn": gs.turn.turn_count,
            "guess": [suspect, item, location],
            "win": True,
        })
        return True, "Win"
    # wrong accusation: lock N turns
    gs.turn.locks[gs.turn.current] = gs.settings["limits"]["wrong_accuse_lock"]
    print(f"[Accuse] {gs.turn.current} -> ({suspect}, {item}, {location}) = WRONG; lock={gs.turn.locks[gs.turn.current]}")
    gs.logs.append({
        "type": "accuse",
        "actor": gs.turn.current,
        "turn": gs.turn.turn_count,
        "guess": [suspect, item, location],
        "win": False,
        "lock": int(gs.turn.locks[gs.turn.current]),
    })
    return False, "Wrong"


def end_turn(gs: GameState) -> None:
    # decrease locks
    for side in ("player", "ai"):
        if gs.turn.locks[side] > 0:
            gs.turn.locks[side] -= 1
    gs.turn.turn_count += 1
    gs.turn.current = "ai" if gs.turn.current == "player" else "player"
    print(f"[Turn] -> turn_count={gs.turn.turn_count} next={gs.turn.current} locks={gs.turn.locks}")
    # Log snapshot of hypotheses
    def _top(hyp: dict) -> Tuple[Tuple[str, str, str], float]:
        items = list(hyp.items())
        items.sort(key=lambda kv: kv[1], reverse=True)
        return items[0]
    p_top_key, p_top_prob = _top(gs.player_knowledge.posterior)
    a_top_key, a_top_prob = _top(gs.ai_knowledge.posterior)
    true_key = (gs.true_triplet.suspect, gs.true_triplet.item, gs.true_triplet.location)
    gs.logs.append({
        "type": "turn_end",
        "turn": int(gs.turn.turn_count),
        "next": gs.turn.current,
        "locks": {"player": int(gs.turn.locks["player"]), "ai": int(gs.turn.locks["ai"])},
        "player_top": [p_top_key[0], p_top_key[1], p_top_key[2], float(p_top_prob)],
        "ai_top": [a_top_key[0], a_top_key[1], a_top_key[2], float(a_top_prob)],
        "player_p_true": float(gs.player_knowledge.posterior.get(true_key, 0.0)),
        "ai_p_true": float(gs.ai_knowledge.posterior.get(true_key, 0.0)),
    })

