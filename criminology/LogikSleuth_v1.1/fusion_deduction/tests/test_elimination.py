from src.logic.elimination import filter_candidates


def test_filter_candidates():
    cands = [
        {"name": "A", "x": True},
        {"name": "B", "x": False},
        {"name": "C", "x": True},
    ]

    def pred(c):
        return c["x"]

    keep_true = filter_candidates(cands, pred, True)
    assert [c["name"] for c in keep_true] == ["A", "C"]

    keep_false = filter_candidates(cands, pred, False)
    assert [c["name"] for c in keep_false] == ["B"]

