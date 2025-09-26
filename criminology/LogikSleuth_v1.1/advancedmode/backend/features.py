from __future__ import annotations

from typing import Dict, List
import math


class FeatureEncoder:
    def __init__(self) -> None:
        self._cat_maps: Dict[str, Dict[str, int]] = {}
        self._num_cols = ["Year", "Month", "VicAge", "OffAge"]
        self._cat_cols = ["VicSex", "VicRace", "OffSex", "OffRace", "Weapon", "Relationship", "MSA", "State"]

    def _one_hot(self, col: str, val: str) -> List[float]:
        m = self._cat_maps.setdefault(col, {})
        if val not in m:
            m[val] = len(m)
        size = len(m)
        vec = [0.0] * size
        vec[m[val]] = 1.0
        return vec

    def _num(self, val: str) -> float:
        try:
            return float(val)
        except Exception:
            return 0.0

    def fit_transform_partial(self, rows: List[Dict[str, str]]) -> List[List[float]]:
        X: List[List[float]] = []
        for r in rows:
            v: List[float] = []
            # numerical
            for c in self._num_cols:
                v.append(self._num(r.get(c, "0")))
            # categorical
            for c in self._cat_cols:
                v.extend(self._one_hot(c, str(r.get(c, ""))))
            # L2 normalize
            s = sum(x * x for x in v)
            if s > 0:
                inv = 1.0 / math.sqrt(s)
                v = [x * inv for x in v]
            X.append(v)
        return X


