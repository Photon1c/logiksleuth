from __future__ import annotations

from typing import Callable, Iterable, List


def filter_candidates(cands, predicate, answer_yes: bool):
    return [c for c in cands if bool(predicate(c)) is answer_yes]


def filter_list_by_predicate(items: Iterable, predicate: Callable, keep_true: bool) -> List:
    return [x for x in items if bool(predicate(x)) is keep_true]

