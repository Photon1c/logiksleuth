from __future__ import annotations

from advancedmode.backend.matcher import SimilarityMatcher


def test_cosine_similarity_pairs():
    m = SimilarityMatcher()
    # Two orthogonal and one identical vector
    m.add_block([[1.0, 0.0], [0.0, 1.0]], ids=["a", "b"])  # already normalized
    m.add_block([[1.0, 0.0]], ids=["c"])                     # same as 'a'
    pairs = m.find_matches(threshold=0.9)
    assert ("a", "c", 1.0) in pairs or ("c", "a", 1.0) in pairs

