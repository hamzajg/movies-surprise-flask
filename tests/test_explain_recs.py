"""Tests for POST /explain-recs — score contract + reason citations.

The Surprise dump is faked so tests stay fast and deterministic; the
citation path (similarity.py + explain.py) runs for real against the
committed ml-latest-small CSVs.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import server


class FakeTrainset:
    """Minimal trainset: user 20 rated almost every latest-small movie."""

    def all_ratings(self):
        return [(20, mid, 4.0) for mid in range(2, 4000)]

    def build_testset(self):
        return []


class FakeAlgo:
    trainset = FakeTrainset()

    def test(self, _testset):
        return []


def _fake_recs(_predictions):
    return {20: [(1, 4.5), (2, 3.9), (3, 3.1)]}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(server.dump, 'load', lambda _path: (None, FakeAlgo()))
    monkeypatch.setattr(server, 'get_all_recs', _fake_recs)
    server.app.config['TESTING'] = True
    with server.app.test_client() as c:
        yield c


VALID_BODY = {
    'userId': 20,
    'candidateIds': [1, 2, 3],
    'excludeIds': [2],
    'limit': 5,
}


def test_explain_recs_requires_json_body(client):
    assert client.post('/explain-recs').status_code == 400


def test_validation_matches_score(client):
    for body in [
        {'userId': 20},
        dict(VALID_BODY, userId='abc'),
        dict(VALID_BODY, candidateIds='1,2,3'),
        dict(VALID_BODY, explainLimit='x'),
    ]:
        assert client.post('/explain-recs', json=body).status_code == 400


def test_explain_recs_keeps_score_contract(client):
    response = client.post('/explain-recs', json=VALID_BODY)
    assert response.status_code == 200
    data = response.get_json()
    # movieId 2 is excluded -> only 1 and 3 survive, in rec order
    assert data['movieIds'] == [1, 3]
    assert [r['movieId'] for r in data['predictedRatings']] == [1, 3]
    assert data['source'] == {'id': 'SVD_model'}


def test_explain_recs_adds_reasons_per_movie(client):
    data = client.post('/explain-recs', json=VALID_BODY).get_json()
    assert len(data['explanations']) == 2
    for entry in data['explanations']:
        assert entry['movieId'] in (1, 3)
        assert 'predictedRating' in entry
        assert isinstance(entry['reasons'], list)
        # user 20 rated ~everything -> reasons should cite rated neighbors
        for reason in entry['reasons']:
            assert reason['userRating'] == 4.0
            assert 0 < reason['similarity'] <= 1


def test_explain_recs_respects_explain_limit(client):
    body = dict(VALID_BODY, explainLimit=1)
    data = client.post('/explain-recs', json=body).get_json()
    for entry in data['explanations']:
        assert len(entry['reasons']) <= 1


def test_explain_recs_empty_reasons_when_user_rated_nothing(client, monkeypatch):
    class ColdTrainset(FakeTrainset):
        def all_ratings(self):
            return [(99, 5000, 5.0)]

    class ColdAlgo(FakeAlgo):
        trainset = ColdTrainset()

    monkeypatch.setattr(server.dump, 'load', lambda _path: (None, ColdAlgo()))
    body = dict(VALID_BODY, explainLimit=3)
    data = client.post('/explain-recs', json=body).get_json()
    assert data['movieIds'] == [1, 3]
    assert all(e['reasons'] == [] for e in data['explanations'])
