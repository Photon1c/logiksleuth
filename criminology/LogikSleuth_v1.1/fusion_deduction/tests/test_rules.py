from src.game_state import GameState, Triplet
from src.rules import handle_question, handle_probe, handle_accuse


def _gs():
    settings = {
        "screen": {"w": 1280, "h": 800, "fps": 60},
        "board": {"size": 5, "evidence_nodes": 1},
        "limits": {"questions_per_round": 5, "wrong_accuse_lock": 1},
        "ai": {"accuse_threshold": 0.9, "probe_explore_weight": 0.35},
        "dev_seed": 42,
    }
    return GameState.from_settings(settings, dev=True)


def test_handle_question():
    gs = _gs()
    pred = lambda t: t.suspect == gs.true_triplet.suspect
    ans, _ = handle_question(gs, pred)
    assert ans is True
    assert gs.player_knowledge.questions_left == 4


def test_handle_probe_and_accuse():
    gs = _gs()
    # probe somewhere
    hit, _ = handle_probe(gs, (0, 0))
    assert isinstance(hit, bool)

    # accuse wrong
    wrong = ("ZZ", "YY", "XX")
    ok, msg = handle_accuse(gs, *wrong)
    assert ok is False
    assert gs.turn.locks["player"] == 1

