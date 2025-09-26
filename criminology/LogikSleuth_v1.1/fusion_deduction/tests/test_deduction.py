from src.logic.deduction import update_posterior_yes_no
from src.game_state import Triplet


def test_update_posterior_yes_no():
    posterior = {
        ("A", "X", "L1"): 0.5,
        ("B", "X", "L1"): 0.5,
    }
    pred = lambda t: t.suspect == "A"
    updated = update_posterior_yes_no(posterior, pred, True)
    assert updated[("A", "X", "L1")] > updated[("B", "X", "L1")]

