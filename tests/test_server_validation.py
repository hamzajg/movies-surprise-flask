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
