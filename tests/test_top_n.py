from top_n_recommendations import get_top_n, get_all_recs


def _pred(uid, iid, est):
    # Same 5-tuple shape Surprise predictions unpack to in the helpers.
    return (uid, iid, 0.0, est, {})


def test_get_top_n_sorts_by_estimated_rating_desc():
    preds = [
        _pred('1', '10', 3.5),
        _pred('1', '20', 4.5),
        _pred('1', '30', 2.0),
    ]
    top_n = get_top_n(preds, n=10)
    assert top_n[1] == [(20, 4.5), (10, 3.5), (30, 2.0)]


def test_get_top_n_truncates_to_n():
    preds = [_pred('1', str(i), float(i)) for i in range(1, 8)]
    top_n = get_top_n(preds, n=3)
    assert len(top_n[1]) == 3
    assert top_n[1][0] == (7, 7.0)


def test_get_top_n_groups_per_user_and_coerces_ids_to_int():
    preds = [
        _pred('1', '5', 4.0),
        _pred('2', '6', 3.0),
        _pred('1', '7', 5.0),
    ]
    top_n = get_top_n(preds, n=10)
    assert set(top_n.keys()) == {1, 2}
    assert top_n[1] == [(7, 5.0), (5, 4.0)]
    assert top_n[2] == [(6, 3.0)]


def test_get_all_recs_returns_every_prediction_sorted():
    preds = [
        _pred('1', '10', 3.5),
        _pred('1', '20', 4.5),
        _pred('1', '30', 2.0),
        _pred('1', '40', 1.0),
    ]
    recs = get_all_recs(preds)
    assert recs[1] == [(20, 4.5), (10, 3.5), (30, 2.0), (40, 1.0)]
