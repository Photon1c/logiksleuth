from __future__ import annotations

from typing import Callable, Dict, Tuple

from ..game_state import Triplet


def update_posterior_yes_no(posterior: Dict[Tuple[str, str, str], float], predicate: Callable[[Triplet], bool], answer: bool):
    # Likelihood model: predicate(hyp) equals answer -> weight 1, else epsilon
    eps = 1e-6
    weights = {}
    total = 0.0
    for hyp, p in posterior.items():
        like = 1.0 if bool(predicate(Triplet(*hyp))) is answer else eps
        w = like * p
        weights[hyp] = w
        total += w
    if total <= 0:
        return posterior
    for hyp in list(weights.keys()):
        weights[hyp] /= total
    return weights

