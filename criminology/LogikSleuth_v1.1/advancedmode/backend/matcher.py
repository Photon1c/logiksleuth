from __future__ import annotations

from typing import List, Tuple


class SimilarityMatcher:
    def __init__(self, block_size: int = 2048) -> None:
        self._blocks: List[List[List[float]]] = []
        self._id_blocks: List[List[str]] = []
        self._block_size = block_size
        self._threshold = 0.7

    def add_block(self, X: List[List[float]], ids: List[str]) -> None:
        self._blocks.append(X)
        self._id_blocks.append(ids)

    def _dot(self, a: List[float], b: List[float]) -> float:
        n = min(len(a), len(b))
        s = 0.0
        for i in range(n):
            s += a[i] * b[i]
        return s

    def find_matches(self, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        self._threshold = threshold
        pairs: List[Tuple[str, str, float]] = []
        # Brute-force across blocks (demo); replace with numpy for speed in real use
        for bi, (A, Aids) in enumerate(zip(self._blocks, self._id_blocks)):
            for bj, (B, Bids) in enumerate(zip(self._blocks, self._id_blocks)):
                # upper triangle including diagonal
                if bj < bi:
                    continue
                for i, va in enumerate(A):
                    for j, vb in enumerate(B):
                        if bi == bj and j <= i:
                            continue
                        sim = self._dot(va, vb)  # vectors already L2-normalized
                        if sim >= self._threshold:
                            pairs.append((str(Aids[i]), str(Bids[j]), float(sim)))
        # Sort by similarity desc and cap for heatmap sampling
        pairs.sort(key=lambda t: t[2], reverse=True)
        self._last_pairs = pairs
        return pairs

    def sample_matrix(self, limit: int = 48) -> Tuple[List[str], List[List[float]]]:
        # Build a small symmetric matrix from up to limit unique ids present in last pairs
        ids_set = []
        seen = set()
        for a, b, _ in getattr(self, "_last_pairs", [])[: limit * limit]:
            if a not in seen:
                seen.add(a); ids_set.append(a)
            if len(ids_set) >= limit:
                break
            if b not in seen:
                seen.add(b); ids_set.append(b)
            if len(ids_set) >= limit:
                break
        n = len(ids_set)
        mat = [[0.0 for _ in range(n)] for _ in range(n)]
        idx = {s: i for i, s in enumerate(ids_set)}
        for a, b, w in getattr(self, "_last_pairs", []):
            ia = idx.get(a); ib = idx.get(b)
            if ia is None or ib is None:
                continue
            mat[ia][ib] = max(mat[ia][ib], w)
            mat[ib][ia] = max(mat[ib][ia], w)
        for i in range(n):
            mat[i][i] = 1.0
        return ids_set, mat


