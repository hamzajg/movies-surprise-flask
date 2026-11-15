import pytest

import server


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as c:
        yield c


VALID_BODY = {
    'userId': 20,
    'candidateIds': [1, 2, 3],
    'excludeIds': [2],
    'limit': 5,
}


@pytest.mark.parametrize('path', ['/score', '/retrieve', '/rank'])
def test_json_routes_require_a_json_body(client, path):
    response = client.post(path)
    assert response.status_code == 400


@pytest.mark.parametrize('path', ['/score', '/retrieve', '/rank'])
def test_json_routes_reject_missing_fields(client, path):
    response = client.post(path, json={'userId': 20})
    assert response.status_code == 400


@pytest.mark.parametrize('path', ['/score', '/retrieve', '/rank'])
def test_json_routes_reject_non_integer_ids(client, path):
    body = dict(VALID_BODY, userId='abc')
    response = client.post(path, json=body)
    assert response.status_code == 400


@pytest.mark.parametrize('path', ['/score', '/retrieve', '/rank'])
def test_json_routes_reject_non_list_candidates(client, path):
    body = dict(VALID_BODY, candidateIds='1,2,3')
    response = client.post(path, json=body)
    assert response.status_code == 400


@pytest.mark.parametrize('path', ['/similar', '/explain'])
def test_explain_routes_require_a_json_body(client, path):
    response = client.post(path)
    assert response.status_code == 400


@pytest.mark.parametrize('path', ['/similar', '/explain'])
def test_explain_routes_reject_missing_movie(client, path):
    response = client.post(path, json={'limit': 5})
    assert response.status_code == 400


@pytest.mark.parametrize('path', ['/similar', '/explain'])
def test_explain_routes_reject_non_integer_movie_ids(client, path):
    response = client.post(path, json={'movieIds': ['abc'], 'limit': 5})
    assert response.status_code == 400


@pytest.mark.parametrize('path', ['/similar', '/explain'])
def test_explain_routes_reject_bad_limit(client, path):
    response = client.post(path, json={'movieId': 1, 'limit': 'abc'})
    assert response.status_code == 400


def test_explain_routes_return_citations(client):
    response = client.post('/explain', json={'userId': 1, 'movieIds': [1], 'limit': 3})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['source']['id'] == 'movielens-item-item'
    explanation = payload['explanations'][0]
    assert explanation['movieId'] == 1
    assert explanation['title'] == 'Toy Story (1995)'
    assert len(explanation['similar']) == 3
    assert all('similarity' in s and 'userRating' in s for s in explanation['similar'])


def test_similar_route_returns_neighbors(client):
    response = client.post('/similar', json={'movieId': 1, 'limit': 3})
    assert response.status_code == 200
    movies = response.get_json()['movies']
    assert movies[0]['movieId'] == 1
    assert len(movies[0]['similar']) == 3


def test_index_route_renders(client):
    response = client.get('/')
    assert response.status_code == 200


def test_recs_rejects_missing_form_fields(client):
    response = client.post('/recs', data={})
    assert response.status_code == 400


def test_recs_rejects_non_integer_limit(client):
    response = client.post('/recs', data={'userId': '20', 'limit': 'abc'})
    assert response.status_code == 400


def test_api_rejects_missing_or_bad_userid(client):
    assert client.get('/api/').status_code == 400
    assert client.get('/api/?userid=abc').status_code == 400
