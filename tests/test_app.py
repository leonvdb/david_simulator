from app import app
from david_web import planisphere

import pytest

@pytest.fixture(scope='session')
def client():

    app.config['TESTING'] = True
    client = app.test_client()

    yield client

@pytest.fixture()
def new_client():

    app.config['TESTING'] = True
    client = app.test_client()

    yield client


def test_index(client):
    rv = client.get('/', follow_redirects=True)
    assert rv.status_code == 200


def test_game(client):

    rv = client.get('/game', follow_redirects=True)
    assert rv.status_code, 200
    assert b"Davids Room" in rv.data

    data = {'action': 'geh in den flur'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'geh raus'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Outside" in rv.data



def test_back_home(new_client):

    new_client.get('/', follow_redirects=True)

    rv = new_client.get('/game', follow_redirects=True)
    assert rv.status_code, 200
    assert b"Davids Room" in rv.data

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

def test_errors(new_client):

    new_client.get('/', follow_redirects=True)

    rv = new_client.get('/game', follow_redirects=True)
    assert rv.status_code, 200
    assert b"Davids Room" in rv.data

    data = {'action': 'geh geh geh!'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"zu viele Verben" in rv.data

    data = {'action': 'Flur!'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"kein bekanntes Verb" in rv.data

    data = {'action': 'geh weg!'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"keine bekannte Richtung" in rv.data
