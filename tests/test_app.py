from app import app
from david_web import engine
from david_web import gamestate

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


@pytest.fixture()
def new_client2():

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

    data = {'action': 'greif die pflanze an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kannst du nicht' in rv.data

    data = {'action': 'bau einen build_test'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'erfolgreich' in rv.data
    assert 'build_test' in gamestate.inventory
    assert 'ingredient1' not in gamestate.inventory
    davids_room = engine.match_Room('davids_room')
    assert 'ingredient2' not in davids_room.object_names

    data = {'action': 'nimm den salat'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'iss das bett auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kannst du nicht konsumieren' in rv.data

    data = {'action': 'greif das bett mit dem scalpell an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'besiegt' in rv.data
    assert b'gemuetlich' in rv.data
    assert b'35' in rv.data
    assert 'müde' in gamestate.states

    data = {'action': 'greif das bett an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'besiegt' in rv.data

    data = {'action': 'greif das bett an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'nicht nochmal' in rv.data

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'iss das scalpell auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'befindet sich weder in diesem Raum' in rv.data

    data = {'action': 'greif das monster an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'in diesem Raum'in rv.data

    data = {'action': 'geh in das badezimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Bathroom" in rv.data

    data = {'action': 'greif das monster an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert gamestate.character_stats.get('Health') == 80
    assert b'David hat noch 80' in rv.data

    data = {'action': 'iss den salat auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert gamestate.character_stats.get('Health') == 90
    assert 'vegan' in gamestate.states
    assert 'salat' not in gamestate.inventory

    data = {'action': 'iss den salat auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert gamestate.character_stats.get('Health') == 90
    assert 'vegan' in gamestate.states
    assert 'salat' not in gamestate.inventory
    bathroom = engine.match_Room('bathroom')
    assert 'b12' in bathroom.object_names

    data = {'action': 'iss das B12'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert gamestate.character_stats.get('Health') == 110
    assert gamestate.character_stats.get('Attack_Points') == 30
    assert 'b12' not in bathroom.object_names


# def test_take(new_client2):
#
#     # Fix this!!
#     new_client2.get('/', follow_redirects=True)
#
#     rv = new_client2.get('/game', follow_redirects=True)
#     assert rv.status_code, 200
#     assert b"Davids Room" in rv.data
#
#     data = {'action': 'nimm die pflanze'}
#     rv = new_client2.post('/game', follow_redirects=True, data=data)
#     assert rv.status_code == 200
#     assert b"pflanze" in rv.data


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
